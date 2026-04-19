<script lang="ts">
  import { onMount, tick } from 'svelte';
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { ui } from '$lib/stores/ui.svelte';
  import { api } from '$lib/api';
  import { 
    Search, Calendar, ChevronLeft, ChevronRight, 
    ArrowUpDown, ArrowUp, ArrowDown,
    MoreHorizontal, Filter, Download, Info,
    Copy, Edit2, Trash2, Home
  } from 'lucide-svelte';
  import { fade, slide, fly } from 'svelte/transition';
  import DynamicSelect from '$lib/components/DynamicSelect.svelte';
  import PeriodSelect from '$lib/components/PeriodSelect.svelte';

  // --- ESTADO & TIPOS ---
  interface Lancamento {
    id: string;
    data: string;
    descricao: string;
    notas?: string;
    valor: number;
    tipo: 'Receita' | 'Despesa';
    status: string;
    categoria: { nome: string };
    responsavel: { nome: string };
    forma_pagamento: { nome: string };
    obra?: { nome: string };
    fk_categoria: string;
    fk_forma_pagamento: string;
    fk_responsavel: string;
    fk_obra: string | null;
  }

  interface PagedResponse {
    items: Lancamento[];
    total: number;
    page: number;
    page_size: number;
    pages: number;
    stats: {
      total_receitas: number;
      total_despesas: number;
    };
  }

  let data = $state<PagedResponse | null>(null);
  let isLoading = $state(true);
  let selectedIds = $state(new Set<string>());
  let availablePeriods = $state<string[]>([]);
  let categories = $state<any[]>([]);
  let responsibles = $state<any[]>([]);
  
  // Filtros locais (para debouncing)
  let searchInput = $state("");

  // --- LOGICA DE SINCRONIZAÇÃO COM URL ---
  
  // Parâmetros derivados da URL (Runes)
  let currentPage = $derived(Number(page.url.searchParams.get('page')) || 1);
  let pageSize = $derived(Number(page.url.searchParams.get('page_size')) || 10);
  let sortBy = $derived(page.url.searchParams.get('sort_by') || 'data');
  let sortOrder = $derived(page.url.searchParams.get('sort_order') || 'desc');
  let filterDesc = $derived(page.url.searchParams.get('descricao') || '');
  let filterPeriod = $derived(page.url.searchParams.get('periodo') || '');
  let filterCat = $derived(page.url.searchParams.get('fk_categoria') || '');
  let filterRes = $derived(page.url.searchParams.get('fk_responsavel') || '');

  // Efeito para carregar dados quando os parâmetros da URL mudam ou quando há inserção/adição (refreshTrigger)
  $effect(() => {
    ui.refreshTrigger; // Registra a dependência
    fetchData(currentPage, pageSize, sortBy, sortOrder, filterDesc, filterPeriod, filterCat, filterRes);
  });

  async function fetchData(p: number, ps: number, sBy: string, sOrd: string, desc: string, period: string, cat: string, res: string) {
    isLoading = true;
    try {
      const params = new URLSearchParams({
        page: p.toString(),
        page_size: ps.toString(),
        sort_by: sBy,
        sort_order: sOrd
      });
      if (desc) params.append('descricao', desc);
      if (period) params.append('periodo', period);
      if (cat) params.append('fk_categoria', cat);
      if (res) params.append('fk_responsavel', res);

      data = await api.get<PagedResponse>(`/lancamentos/?${params.toString()}`);
      // Limpar seleção ao mudar de página ou filtros
      selectedIds = new Set();
    } catch (err) {
      console.error("Erro ao carregar lançamentos:", err);
    } finally {
      isLoading = false;
    }
  }

  onMount(async () => {
    // Carregar auxiliares para filtros
    try {
      const [pRes, cRes, rRes] = await Promise.all([
        api.get<string[]>('/dashboard/periodos'),
        api.get<any[]>('/auxiliares/categorias/'),
        api.get<any[]>('/auxiliares/responsaveis/')
      ]);
      availablePeriods = pRes;
      categories = cRes;
      responsibles = rRes;
    } catch (err) {
      console.error("Erro ao carregar períodos:", err);
    }
  });

  // --- AÇÕES ---

  function updateParams(newParams: Record<string, string | number | null>) {
    const nextParams = new URLSearchParams(page.url.searchParams);
    for (const [key, value] of Object.entries(newParams)) {
      if (value === null || value === '') {
        nextParams.delete(key);
      } else {
        nextParams.set(key, value.toString());
      }
    }
    // Sempre volta para a página 1 ao filtrar ou ordenar, exceto se estiver mudando a própria página
    if (!('page' in newParams)) {
      nextParams.set('page', '1');
    }
    goto(`?${nextParams.toString()}`, { keepFocus: true, noScroll: true });
  }

  function handleSort(column: string) {
    const isSameColumn = sortBy === column;
    const nextOrder = isSameColumn && sortOrder === 'asc' ? 'desc' : 'asc';
    updateParams({ sort_by: column, sort_order: nextOrder });
  }

  // Debounce para busca
  let searchTimeout: any;
  function handleSearchInput(val: string) {
    searchInput = val;
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      updateParams({ descricao: val });
    }, 500);
  }

  // Seleção
  function toggleSelectAll() {
    if (selectedIds.size === data?.items.length) {
      selectedIds = new Set();
    } else {
      selectedIds = new Set(data?.items.map(i => i.id));
    }
  }

  function toggleSelect(id: string) {
    if (selectedIds.has(id)) {
      selectedIds.delete(id);
    } else {
      selectedIds.add(id);
    }
    // Forçar atualização da Rune Set
    selectedIds = new Set(selectedIds);
  }

  async function handleBatchDelete() {
    if (!confirm(`Deseja excluir ${selectedIds.size} lançamentos selecionados??`)) return;
    
    try {
      await api.post('/lancamentos/batch-delete', { ids: Array.from(selectedIds) });
      selectedIds = new Set();
      // Recarregar dados
      fetchData(currentPage, pageSize, sortBy, sortOrder, filterDesc, filterPeriod, filterCat, filterRes);
    } catch (err) {
      alert("Erro ao excluir itens.");
    }
  }

  async function handleDelete(id: string) {
    if (!confirm("Deseja realmente excluir este lançamento?")) return;
    try {
      await api.delete(`/lancamentos/${id}`);
      fetchData(currentPage, pageSize, sortBy, sortOrder, filterDesc, filterPeriod, filterCat, filterRes);
    } catch (err) {
      alert("Erro ao excluir lançamento.");
    }
  }

  function handleEdit(item: Lancamento) {
    ui.openLaunchModal(item);
  }

  function handleDuplicate(item: Lancamento) {
    // Duplicar: remove o ID para forçar POST e abre a modal
    const { id, categoria, responsavel, forma_pagamento, obra, ...copy } = item;
    ui.openLaunchModal(copy);
  }

  // --- FORMATADORES ---
  const money = (val: number) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
  const formatDate = (dateStr: string) => {
    const [y, m, d] = dateStr.split('-');
    return `${d}/${m}/${y}`;
  };
</script>

<svelte:head>
  <title>Lançamentos | ObrasFinance</title>
</svelte:head>

<div class="p-6 md:p-8 space-y-8 max-w-[1600px] mx-auto w-full">
  
  <!-- HEADER SEÇÃO -->
  <header class="flex items-center justify-between">
    <div>
      <h1 class="text-3xl font-black text-gray-900 tracking-tight">Fluxo de Caixa</h1>
      <p class="text-gray-500 font-medium mt-1 uppercase text-xs tracking-widest opacity-70">Gerencie e monitore todas as entradas e saídas.</p>
    </div>
  </header>

  <!-- PAINEL DE FILTROS -->
  <section class="relative z-20 grid grid-cols-1 md:grid-cols-12 gap-4 bg-white/50 backdrop-blur-sm p-4 rounded-[2rem] border border-gray-100 shadow-sm" in:slide>
    
    <!-- Busca (Col 5) -->
    <div class="md:col-span-4 flex flex-col space-y-1">
      <label class="text-[9px] font-black text-gray-400 uppercase tracking-widest ml-1 opacity-70">Pesquisar</label>
      <div class="relative group">
        <Search size={14} class="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-blue-500 transition-colors" />
        <input 
          type="text" 
          placeholder="Descrição..." 
          value={searchInput || filterDesc}
          oninput={(e) => handleSearchInput(e.currentTarget.value)}
          class="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-xl focus:border-blue-500 focus:shadow-[0_0_0_3px_rgba(59,130,246,0.1)] outline-none transition-all font-semibold text-sm"
        />
      </div>
    </div>

    <!-- Período (Col 2) -->
    <div class="md:col-span-2">
      <PeriodSelect 
        value={filterPeriod} 
        periods={availablePeriods} 
        onchange={(v) => updateParams({ periodo: v })}
      />
    </div>

    <!-- Categoria (Col 2) -->
    <div class="md:col-span-2">
      <DynamicSelect 
        label="Categoria"
        endpoint="/auxiliares/categorias/"
        value={filterCat}
        onchange={(v) => updateParams({ fk_categoria: v })}
        placeholder="Todas"
      />
    </div>

    <!-- Responsável (Col 2) -->
    <div class="md:col-span-3">
      <DynamicSelect 
        label="Responsável"
        endpoint="/auxiliares/responsaveis/"
        value={filterRes}
        onchange={(v) => updateParams({ fk_responsavel: v })}
        placeholder="Todos"
      />
    </div>

    <!-- Ações (Col 1) -->
    <div class="md:col-span-1 flex items-end justify-end">
      <button 
        onclick={() => { searchInput = ''; updateParams({ descricao: '', periodo: '', fk_categoria: '', fk_responsavel: '', page: 1 }); }}
        class="w-full flex items-center justify-center p-2.5 bg-white border border-gray-200 text-gray-400 hover:text-red-500 hover:border-red-100 hover:bg-red-50 transition-all rounded-xl shadow-sm active:scale-95"
        title="Limpar Filtros"
      >
        <Trash2 size={18} />
      </button>
    </div>
  </section>

  <!-- TABLE CONTAINER -->
  <div class="bg-white rounded-[2rem] border border-gray-100 shadow-xl shadow-gray-200/50 overflow-hidden flex flex-col relative min-h-[500px]">
    
    {#if isLoading}
      <div class="absolute inset-0 bg-white/60 backdrop-blur-[2px] z-20 flex flex-col items-center justify-center" transition:fade>
        <div class="w-10 h-10 border-4 border-gray-100 border-t-blue-600 rounded-full animate-spin"></div>
        <p class="mt-4 text-xs font-black text-gray-400 uppercase tracking-widest animate-pulse">Sincronizando...</p>
      </div>
    {/if}

    <div class="overflow-x-auto">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-gray-50/50 border-b border-gray-100">
            <th class="pl-8 py-5 w-12">
              <input 
                type="checkbox" 
                checked={(data?.items?.length ?? 0) > 0 && selectedIds.size === data?.items?.length}
                onchange={toggleSelectAll}
                class="w-5 h-5 rounded-lg border-2 border-gray-300 text-blue-600 focus:ring-blue-500 transition-all cursor-pointer"
              />
            </th>
            
            {#each [
              { label: 'DATA', key: 'data', sortable: true },
              { label: 'DESCRIÇÃO', key: 'descricao', sortable: true },
              { label: 'CATEGORIA', key: 'categoria', sortable: false },
              { label: 'VALOR', key: 'valor', sortable: true },
              { label: 'RESPONSÁVEL', key: 'responsavel', sortable: false },
              { label: 'STATUS', key: 'status', sortable: true },
              { label: 'AÇÕES', key: null, sortable: false }
            ] as col}
              <th class="px-4 py-5 font-black text-[11px] text-gray-400 uppercase tracking-widest">
                {#if col.sortable}
                  <button 
                    onclick={() => handleSort(col.key as string)}
                    class="flex items-center gap-1.5 hover:text-blue-600 transition-colors group"
                  >
                    {col.label}
                    <span class={sortBy === col.key ? 'text-blue-600' : 'text-gray-300 group-hover:text-blue-300'}>
                      {#if sortBy === col.key}
                        {sortOrder === 'asc' ? '↑' : '↓'}
                      {:else}
                        <ArrowUpDown size={12} />
                      {/if}
                    </span>
                  </button>
                {:else}
                  {col.label}
                {/if}
              </th>
            {/each}
          </tr>
        </thead>

        <tbody class="divide-y divide-gray-50">
          {#each data?.items || [] as item (item.id)}
            <tr class="group hover:bg-blue-50/30 transition-colors {selectedIds.has(item.id) ? 'bg-blue-50/50' : ''}">
              <td class="pl-8 py-4">
                <input 
                  type="checkbox" 
                  checked={selectedIds.has(item.id)}
                  onchange={() => toggleSelect(item.id)}
                  class="w-5 h-5 rounded-lg border-2 border-gray-300 text-blue-600 focus:ring-blue-500 transition-all cursor-pointer"
                />
              </td>
              
              <td class="px-4 py-4 whitespace-nowrap">
                <span class="text-sm font-bold text-gray-700">{formatDate(item.data)}</span>
              </td>

              <td class="px-4 py-4 max-w-[300px]">
                <div class="flex flex-col">
                  <span class="text-sm font-black text-gray-900 group-hover:text-blue-600 transition-colors truncate">
                    {item.descricao}
                  </span>
                  {#if item.obra}
                    <span class="text-[10px] font-bold text-gray-400 mt-0.5 uppercase tracking-wide">
                      🏗️ {item.obra.nome}
                    </span>
                  {/if}
                </div>
              </td>

              <td class="px-4 py-4">
                <span class="px-2.5 py-1 bg-gray-100 text-gray-600 rounded-lg text-[10px] font-black uppercase tracking-tight">
                  {item.categoria.nome}
                </span>
              </td>

              <td class="px-4 py-4 whitespace-nowrap">
                <span class="text-sm font-black {item.tipo === 'Receita' ? 'text-emerald-600' : 'text-blue-600'}">
                  {item.tipo === 'Receita' ? '+' : '-'} {money(item.valor)}
                </span>
              </td>

              <td class="px-4 py-4">
                <div class="flex items-center gap-2">
                  <div class="w-7 h-7 rounded-lg bg-gray-100 flex items-center justify-center text-[10px] font-bold text-gray-500">
                    {item.responsavel.nome.charAt(0)}
                  </div>
                  <span class="text-xs font-bold text-gray-600">{item.responsavel.nome}</span>
                </div>
              </td>

              <td class="px-4 py-4">
                <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-tighter {item.status === 'Pago' ? 'bg-emerald-100 text-emerald-700' : 'bg-orange-100 text-orange-700'}">
                  <span class="w-1.5 h-1.5 rounded-full {item.status === 'Pago' ? 'bg-emerald-500' : 'bg-orange-500'}"></span>
                  {item.status}
                </span>
              </td>

              <td class="pr-8 py-4">
                <div class="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button 
                    onclick={() => handleDuplicate(item)}
                    class="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all" 
                    title="Duplicar"
                  >
                    <Copy size={16} />
                  </button>
                  <button 
                    onclick={() => handleEdit(item)}
                    class="p-2 text-gray-400 hover:text-amber-600 hover:bg-amber-50 rounded-lg transition-all" 
                    title="Editar"
                  >
                    <Edit2 size={16} />
                  </button>
                  <button 
                    onclick={() => handleDelete(item.id)}
                    class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all" 
                    title="Excluir"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </td>
            </tr>
          {:else}
            {#if !isLoading}
              <tr>
                <td colspan="8" class="py-24 text-center">
                  <div class="flex flex-col items-center opacity-40">
                    <Info size={48} />
                    <p class="mt-4 font-black uppercase tracking-widest text-sm">Nenhum lançamento encontrado</p>
                    <p class="text-xs font-medium lowercase shadow-sm mt-1">Tente ajustar seus filtros ou busca</p>
                  </div>
                </td>
              </tr>
            {/if}
          {/each}
        </tbody>
      </table>
    </div>

    <div class="mt-auto border-t border-gray-100 bg-gray-50/30 px-8 py-6 flex flex-col md:flex-row items-center justify-between gap-6">
      
      <!-- Totais do Filtro (Esquerda) -->
      <div class="flex items-center gap-8">
        <div class="flex flex-col">
          <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-0.5">Receitas</span>
          <span class="text-base font-black text-emerald-600">{money(data?.stats?.total_receitas || 0)}</span>
        </div>
        <div class="w-px h-8 bg-gray-200"></div>
        <div class="flex flex-col">
          <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-0.5">Despesas</span>
          <span class="text-base font-black text-blue-600">{money(data?.stats?.total_despesas || 0)}</span>
        </div>
      </div>

      <!-- Controles de Navegação e Densidade (Direita) -->
      <div class="flex flex-col md:flex-row items-center gap-6">
        
        <!-- Densidade (Estilo solicitado: Exibindo [10] de 166) -->
        <div class="flex items-center gap-2 text-xs font-bold text-gray-500">
          <span class="opacity-60">Exibindo</span>
          <select 
            value={pageSize}
            onchange={(e) => updateParams({ page_size: e.currentTarget.value })}
            class="bg-white border border-gray-200 rounded-xl px-3 py-1.5 font-black text-gray-900 outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all cursor-pointer shadow-sm"
          >
            <option value="10">10</option>
            <option value="20">20</option>
            <option value="30">30</option>
            <option value="50">50</option>
            <option value="100">100</option>
          </select>
          <span class="opacity-60">de <b class="text-gray-900 ml-1">{data?.total || 0}</b> registros</span>
        </div>

        <div class="hidden md:block w-px h-6 bg-gray-200"></div>

      <!-- Paginação -->
      <div class="flex items-center gap-1.5 bg-white p-1 rounded-2xl border border-gray-200 shadow-sm font-bold text-xs">
        <button 
          disabled={currentPage <= 1 || isLoading}
          onclick={() => updateParams({ page: currentPage - 1 })}
          class="p-2.5 rounded-xl hover:bg-gray-50 transition-all text-gray-500 disabled:opacity-30 active:scale-90"
        >
          <ChevronLeft size={16} />
        </button>
        
        <div class="px-4 py-2 flex items-center gap-2 text-gray-400">
           Página <span class="text-gray-900">{currentPage}</span> de <span class="text-gray-900">{data?.pages || 1}</span>
        </div>

        <button 
          disabled={currentPage >= (data?.pages || 1) || isLoading}
          onclick={() => updateParams({ page: currentPage + 1 })}
          class="p-2.5 rounded-xl hover:bg-gray-50 transition-all text-gray-500 disabled:opacity-30 active:scale-90"
        >
          <ChevronRight size={16} />
        </button>
      </div>
    </div>
  </div>

  <!-- BATCH ACTIONS PANEL -->
  {#if selectedIds.size > 0}
    <div 
      class="fixed bottom-24 md:bottom-12 left-1/2 -translate-x-1/2 bg-gray-900 text-white px-6 py-4 rounded-[2rem] shadow-2xl flex items-center gap-6 z-50 ring-4 ring-white"
      transition:fly={{ y: 50, duration: 400 }}
    >
      <div class="flex items-center gap-3 pr-6 border-r border-gray-700">
        <div class="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center font-black text-sm">
          {selectedIds.size}
        </div>
        <span class="text-sm font-bold tracking-tight">Selecionados</span>
      </div>

      <div class="flex items-center gap-4">
        <button 
          onclick={handleBatchDelete}
          class="flex items-center gap-2 px-6 py-2 bg-red-600/10 hover:bg-red-600 text-red-500 hover:text-white rounded-xl transition-all font-black text-sm active:scale-95"
        >
          <Trash2 size={16} />
          Excluir Permanente
        </button>
        
        <button 
          onclick={() => selectedIds = new Set()}
          class="text-gray-400 hover:text-white transition-colors text-sm font-bold"
        >
          Cancelar
        </button>
      </div>
    </div>
  {/if}

  </div>
</div>

<style>
  /* Personalização de scrollbar se necessário */
  ::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }
  ::-webkit-scrollbar-track {
    background: transparent;
  }
  ::-webkit-scrollbar-thumb {
    background: #e2e8f0;
    border-radius: 10px;
  }
  ::-webkit-scrollbar-thumb:hover {
    background: #cbd5e1;
  }
</style>
