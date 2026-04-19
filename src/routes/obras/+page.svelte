<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import { 
    Search, Plus, MoreHorizontal, Info,
    Edit2, Trash2, HardHat
  } from 'lucide-svelte';
  import { fade, slide, fly } from 'svelte/transition';
  import ObraModal from '$lib/components/ObraModal.svelte';

  // --- ESTADO & TIPOS ---
  interface Obra {
    id: string;
    nome: string;
    nome_cliente: string;
    custo_estimado: number;
    data_inicio: string;
    data_fim: string | null;
    descricao: string | null;
  }

  let obras = $state<Obra[]>([]);
  let isLoading = $state(true);
  
  // Modal de edição/adição
  let isModalOpen = $state(false);
  let modalData = $state<Obra | null>(null);

  // Filtros locais (para debouncing)
  let searchInput = $state("");

  // --- LOGICA DE SINCRONIZAÇÃO COM URL ---
  let filterNomeCliente = $derived(page.url.searchParams.get('nome_cliente') || '');

  // Efeito para carregar dados quando os parâmetros da URL mudam
  $effect(() => {
    fetchData(filterNomeCliente);
  });

  async function fetchData(cliente: string) {
    isLoading = true;
    try {
      const params = new URLSearchParams();
      if (cliente) params.append('nome_cliente', cliente);

      obras = await api.get<Obra[]>(`/obras/?${params.toString()}`);
    } catch (err) {
      console.error("Erro ao carregar obras:", err);
    } finally {
      isLoading = false;
    }
  }

  // --- AÇÕES ---

  function updateParams(newParams: Record<string, string | null>) {
    const nextParams = new URLSearchParams(page.url.searchParams);
    for (const [key, value] of Object.entries(newParams)) {
      if (value === null || value === '') {
        nextParams.delete(key);
      } else {
        nextParams.set(key, value.toString());
      }
    }
    goto(`?${nextParams.toString()}`, { keepFocus: true, noScroll: true });
  }

  // Debounce para busca
  let searchTimeout: any;
  function handleSearchInput(val: string) {
    searchInput = val;
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      updateParams({ nome_cliente: val });
    }, 500);
  }

  async function handleDelete(id: string) {
    if (!confirm("Deseja realmente excluir esta Obra? Todos os lançamentos vinculados a ela ficarão sem vínculo.")) return;
    try {
      await api.delete(`/obras/${id}`);
      fetchData(filterNomeCliente);
    } catch (err) {
      alert("Erro ao excluir obra.");
    }
  }

  function handleEdit(item: Obra) {
    modalData = item;
    isModalOpen = true;
  }

  function handleNew() {
    modalData = null;
    isModalOpen = true;
  }

  // --- FORMATADORES ---
  const money = (val: number) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '-';
    const [y, m, d] = dateStr.split('-');
    return `${d}/${m}/${y}`;
  };
</script>

<svelte:head>
  <title>Obras | ObrasFinance</title>
</svelte:head>

<div class="p-6 md:p-8 space-y-8 max-w-[1600px] mx-auto w-full">
  
  <!-- HEADER & AÇÕES PRINCIPAIS -->
  <div class="flex flex-col md:flex-row md:items-end justify-between gap-6">
    <div class="space-y-1">
      <h1 class="text-3xl font-black text-gray-900 tracking-tight">Obras e Projetos</h1>
      <p class="text-gray-500 font-medium">Cadastre e acompanhe o andamento de novos empreendimentos.</p>
    </div>

    <button 
      onclick={handleNew}
      class="flex items-center gap-2 px-6 py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-black rounded-2xl transition-all shadow-lg shadow-blue-200 active:scale-95"
    >
      <Plus size={20} />
      <span>Nova Obra</span>
    </button>
  </div>

  <!-- PAINEL DE FILTROS -->
  <section class="grid grid-cols-1 md:grid-cols-12 gap-4 bg-white/50 backdrop-blur-sm p-4 rounded-[2rem] border border-gray-100 shadow-sm" in:slide>
    <!-- Busca (Col 6) -->
    <div class="md:col-span-6 flex flex-col space-y-1">
      <label class="text-[9px] font-black text-gray-400 uppercase tracking-widest ml-1 opacity-70">Pesquisar por Cliente</label>
      <div class="relative group">
        <Search size={14} class="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-blue-500 transition-colors" />
        <input 
          type="text" 
          placeholder="Ex: Maria Souza..." 
          value={searchInput || filterNomeCliente}
          oninput={(e) => handleSearchInput(e.currentTarget.value)}
          class="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-xl focus:border-blue-500 focus:shadow-[0_0_0_3px_rgba(59,130,246,0.1)] outline-none transition-all font-semibold text-sm"
        />
      </div>
    </div>

    <!-- Ações (Col 6) -->
    <div class="md:col-span-6 flex items-end justify-end">
      <button 
        onclick={() => { searchInput = ''; updateParams({ nome_cliente: '' }); }}
        class="flex items-center justify-center p-2.5 bg-white border border-gray-200 text-gray-400 hover:text-red-500 hover:border-red-100 hover:bg-red-50 transition-all rounded-xl shadow-sm active:scale-95"
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
            {#each [
              { label: 'NOME DA OBRA' },
              { label: 'CLIENTE' },
              { label: 'CUSTO ESTIMADO' },
              { label: 'INÍCIO' },
              { label: 'PREVISÃO FIM' },
              { label: 'AÇÕES' }
            ] as col}
              <th class="px-6 py-5 font-black text-[11px] text-gray-400 uppercase tracking-widest">
                {col.label}
              </th>
            {/each}
          </tr>
        </thead>

        <tbody class="divide-y divide-gray-50">
          {#each obras as item (item.id)}
            <tr class="group hover:bg-blue-50/30 transition-colors">
              <td class="px-6 py-4 max-w-[300px]">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-2xl bg-gray-100 flex items-center justify-center text-gray-400 group-hover:bg-blue-100 group-hover:text-blue-600 transition-colors">
                    <HardHat size={20} />
                  </div>
                  <div class="flex flex-col">
                    <span class="text-sm font-black text-gray-900 group-hover:text-blue-600 transition-colors truncate">
                      {item.nome}
                    </span>
                    {#if item.descricao}
                      <span class="text-[10px] font-bold text-gray-400 mt-0.5 truncate max-w-[200px]">
                        {item.descricao}
                      </span>
                    {/if}
                  </div>
                </div>
              </td>

              <td class="px-6 py-4">
                <span class="text-sm font-bold text-gray-700">{item.nome_cliente}</span>
              </td>

              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm font-black text-blue-600">
                  {money(item.custo_estimado)}
                </span>
              </td>

              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm font-bold text-gray-700">{formatDate(item.data_inicio)}</span>
              </td>

              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm font-bold text-gray-700">{formatDate(item.data_fim)}</span>
              </td>

              <td class="px-6 py-4">
                <div class="flex items-center justify-start gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
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
                <td colspan="6" class="py-24 text-center">
                  <div class="flex flex-col items-center opacity-40">
                    <Info size={48} />
                    <p class="mt-4 font-black uppercase tracking-widest text-sm">Nenhuma obra encontrada</p>
                    <p class="text-xs font-medium lowercase shadow-sm mt-1">Tente ajustar seus filtros ou cadastre uma nova.</p>
                  </div>
                </td>
              </tr>
            {/if}
          {/each}
        </tbody>
      </table>
    </div>
  </div>
</div>

<ObraModal bind:isOpen={isModalOpen} modalData={modalData} onSave={() => fetchData(filterNomeCliente)} />

<style>
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
