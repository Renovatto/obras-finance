<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { 
    Settings, Tags, CreditCard, Users, 
    Plus, Trash2, Edit2, Check, X, Loader2, Database
  } from 'lucide-svelte';
  import { fade, slide } from 'svelte/transition';

  type Item = { id: string; nome: string };

  let isLoading = $state(true);
  let isSaving = $state(false);

  // Estados locais para os 3 domínios
  let categorias = $state<Item[]>([]);
  let formas = $state<Item[]>([]);
  let responsaveis = $state<Item[]>([]);

  // Estados de "Add Novo"
  let newCategoria = $state('');
  let newForma = $state('');
  let newResponsavel = $state('');

  // Estados de "Edição" (guarda o ID e o novo texto)
  let editingId = $state<string | null>(null);
  let editingText = $state('');

  // Estado de Configuração de Sistema
  let systemConfig = $state({
    database_path: '',
    port: 8000
  });

  async function loadSystemConfig() {
    try {
      const config = await api.get<any>('/config/');
      systemConfig = config;
    } catch (err) {
      console.error("Erro ao carregar config de sistema:", err);
    }
  }

  async function loadData() {
    isLoading = true;
    try {
      const res = await api.get<any>('/auxiliares/todos');
      categorias = res.categorias;
      formas = res.formas_pagamento;
      responsaveis = res.responsaveis;
    } catch (err) {
      console.error("Erro ao carregar auxiliares:", err);
    } finally {
      isLoading = false;
    }
  }

  onMount(() => {
    loadData();
    loadSystemConfig();
  });

  // --- FUNÇÕES GENÉRICAS DE CRUD ---
  
  async function handleAdd(type: 'categoria' | 'forma' | 'responsavel') {
    if (isSaving) return;
    isSaving = true;

    try {
      if (type === 'categoria' && newCategoria) {
        await api.post('/auxiliares/categorias/', { nome: newCategoria });
        newCategoria = '';
      } else if (type === 'forma' && newForma) {
        await api.post('/auxiliares/formas-pagamento/', { nome: newForma });
        newForma = '';
      } else if (type === 'responsavel' && newResponsavel) {
        await api.post('/auxiliares/responsaveis/', { nome: newResponsavel });
        newResponsavel = '';
      }
      await loadData();
    } catch (err) {
      alert("Erro ao salvar o registro.");
    } finally {
      isSaving = false;
    }
  }

  function startEdit(item: Item) {
    editingId = item.id;
    editingText = item.nome;
  }

  function cancelEdit() {
    editingId = null;
    editingText = '';
  }

  async function saveEdit(type: 'categoria' | 'forma' | 'responsavel', id: string) {
    if (isSaving || !editingText) return;
    isSaving = true;

    try {
      const endpoint = type === 'categoria' ? 'categorias' 
                     : type === 'forma' ? 'formas-pagamento' 
                     : 'responsaveis';

      await api.patch(`/auxiliares/${endpoint}/${id}`, { nome: editingText });
      await loadData();
      cancelEdit();
    } catch (err) {
      alert("Erro ao editar o registro.");
    } finally {
      isSaving = false;
    }
  }

  async function handleDelete(type: 'categoria' | 'forma' | 'responsavel', id: string) {
    if (!confirm("Deseja realmente excluir este item? Lançamentos vinculados podem ser afetados.")) return;
    
    isSaving = true;
    try {
      const endpoint = type === 'categoria' ? 'categorias' 
                     : type === 'forma' ? 'formas-pagamento' 
                     : 'responsaveis';

      await api.delete(`/auxiliares/${endpoint}/${id}`);
      await loadData();
    } catch (err) {
      alert("Erro ao excluir. O item pode estar em uso.");
    } finally {
      isSaving = false;
    }
  }

  async function handleSaveSystemConfig() {
    if (isSaving) return;
    isSaving = true;
    try {
      await api.post('/config/', systemConfig);
      alert("Configuração salva! Reinicie o aplicativo para aplicar as mudanças de banco de dados.");
    } catch (err) {
      alert("Erro ao salvar configuração de sistema.");
    } finally {
      isSaving = false;
    }
  }

</script>

<svelte:head>
  <title>Ajustes | ObrasFinance</title>
</svelte:head>

<div class="p-6 md:p-8 space-y-8 max-w-[1600px] mx-auto w-full">
  
  <!-- HEADER -->
  <div class="flex flex-col md:flex-row md:items-end justify-between gap-6">
    <div class="space-y-1">
      <h1 class="text-3xl font-black text-gray-900 tracking-tight flex items-center gap-3">
        <Settings size={28} class="text-blue-600" />
        Configurações do Sistema
      </h1>
      <p class="text-gray-500 font-medium">Gerencie categorias, métodos de pagamento e responsáveis.</p>
    </div>
  </div>

  {#if isLoading}
    <div class="flex flex-col items-center justify-center p-24" transition:fade>
      <Loader2 size={40} class="animate-spin text-blue-600" />
      <p class="mt-4 text-xs font-black text-gray-400 border border-gray-100 uppercase tracking-widest animate-pulse">Carregando Módulos...</p>
    </div>
  {:else}
    <!-- GRID DE 3 COLUNAS -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6" in:slide={{ duration: 400 }}>
      
      <!-- COLUNA: CATEGORIAS -->
      <section class="bg-white rounded-[2rem] border border-gray-100 shadow-xl shadow-gray-200/50 flex flex-col h-[600px] overflow-hidden">
        <div class="p-6 border-b border-gray-50 bg-gray-50/30 flex items-center gap-3">
          <div class="p-2.5 bg-blue-100 text-blue-600 rounded-xl">
            <Tags size={20} />
          </div>
          <h2 class="text-lg font-black text-gray-900 tracking-tight">Categorias</h2>
        </div>
        
        <!-- Input Nova -->
        <div class="p-4 border-b border-gray-50 flex items-center gap-2">
          <input 
            type="text" 
            bind:value={newCategoria} 
            placeholder="Nova categoria..." 
            onkeydown={(e) => e.key === 'Enter' && handleAdd('categoria')}
            class="flex-1 px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:border-blue-500 outline-none text-sm font-semibold transition-all uppercase"
          />
          <button 
            onclick={() => handleAdd('categoria')}
            disabled={!newCategoria || isSaving}
            class="p-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 active:scale-95 transition-all disabled:opacity-50"
            title="Adicionar"
          >
            <Plus size={18} />
          </button>
        </div>

        <!-- Lista -->
        <div class="flex-1 overflow-y-auto p-2">
          <ul class="space-y-1">
            {#each categorias as item}
              <li class="group flex items-center justify-between p-3 hover:bg-blue-50/50 rounded-xl transition-colors">
                {#if editingId === item.id}
                  <div class="flex-1 flex flex-col sm:flex-row items-center gap-2">
                    <input 
                      type="text" 
                      bind:value={editingText}
                      class="flex-1 w-full px-3 py-1 bg-white border border-blue-300 rounded-lg outline-none text-xs font-bold uppercase transition-all shadow-sm"
                    />
                    <div class="flex items-center gap-1">
                      <button onclick={() => saveEdit('categoria', item.id)} class="p-1.5 text-green-600 hover:bg-green-100 rounded-lg"><Check size={14}/></button>
                      <button onclick={cancelEdit} class="p-1.5 text-red-500 hover:bg-red-100 rounded-lg"><X size={14}/></button>
                    </div>
                  </div>
                {:else}
                  <span class="text-sm font-black text-gray-700 uppercase tracking-wide truncate pr-2">{item.nome}</span>
                  <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button onclick={() => startEdit(item)} class="p-1.5 text-gray-400 hover:text-amber-500 hover:bg-amber-50 rounded-lg transition-colors"><Edit2 size={14}/></button>
                    <button onclick={() => handleDelete('categoria', item.id)} class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"><Trash2 size={14}/></button>
                  </div>
                {/if}
              </li>
            {/each}
          </ul>
        </div>
      </section>

      <!-- COLUNA: FORMAS DE PAGAMENTO -->
      <section class="bg-white rounded-[2rem] border border-gray-100 shadow-xl shadow-gray-200/50 flex flex-col h-[600px] overflow-hidden">
        <div class="p-6 border-b border-gray-50 bg-gray-50/30 flex items-center gap-3">
          <div class="p-2.5 bg-emerald-100 text-emerald-600 rounded-xl">
            <CreditCard size={20} />
          </div>
          <h2 class="text-lg font-black text-gray-900 tracking-tight">Formas Pagto.</h2>
        </div>
        
        <!-- Input Nova -->
        <div class="p-4 border-b border-gray-50 flex items-center gap-2">
          <input 
            type="text" 
            bind:value={newForma} 
            placeholder="Novo método..." 
            onkeydown={(e) => e.key === 'Enter' && handleAdd('forma')}
            class="flex-1 px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:border-emerald-500 outline-none text-sm font-semibold transition-all uppercase"
          />
          <button 
            onclick={() => handleAdd('forma')}
            disabled={!newForma || isSaving}
            class="p-2 bg-emerald-600 text-white rounded-xl hover:bg-emerald-700 active:scale-95 transition-all disabled:opacity-50"
            title="Adicionar"
          >
            <Plus size={18} />
          </button>
        </div>

        <!-- Lista -->
        <div class="flex-1 overflow-y-auto p-2">
          <ul class="space-y-1">
            {#each formas as item}
              <li class="group flex items-center justify-between p-3 hover:bg-emerald-50/50 rounded-xl transition-colors">
                {#if editingId === item.id}
                  <div class="flex-1 flex flex-col sm:flex-row items-center gap-2">
                    <input 
                      type="text" 
                      bind:value={editingText}
                      class="flex-1 w-full px-3 py-1 bg-white border border-emerald-300 rounded-lg outline-none text-xs font-bold uppercase transition-all shadow-sm"
                    />
                    <div class="flex items-center gap-1">
                      <button onclick={() => saveEdit('forma', item.id)} class="p-1.5 text-green-600 hover:bg-green-100 rounded-lg"><Check size={14}/></button>
                      <button onclick={cancelEdit} class="p-1.5 text-red-500 hover:bg-red-100 rounded-lg"><X size={14}/></button>
                    </div>
                  </div>
                {:else}
                  <span class="text-sm font-black text-gray-700 uppercase tracking-wide truncate pr-2">{item.nome}</span>
                  <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button onclick={() => startEdit(item)} class="p-1.5 text-gray-400 hover:text-amber-500 hover:bg-amber-50 rounded-lg transition-colors"><Edit2 size={14}/></button>
                    <button onclick={() => handleDelete('forma', item.id)} class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"><Trash2 size={14}/></button>
                  </div>
                {/if}
              </li>
            {/each}
          </ul>
        </div>
      </section>

      <!-- COLUNA: RESPONSÁVEIS -->
      <section class="bg-white rounded-[2rem] border border-gray-100 shadow-xl shadow-gray-200/50 flex flex-col h-[600px] overflow-hidden">
        <div class="p-6 border-b border-gray-50 bg-gray-50/30 flex items-center gap-3">
          <div class="p-2.5 bg-amber-100 text-amber-600 rounded-xl">
            <Users size={20} />
          </div>
          <h2 class="text-lg font-black text-gray-900 tracking-tight">Responsáveis</h2>
        </div>
        
        <!-- Input Nova -->
        <div class="p-4 border-b border-gray-50 flex items-center gap-2">
          <input 
            type="text" 
            bind:value={newResponsavel} 
            placeholder="Novo responsável..." 
            onkeydown={(e) => e.key === 'Enter' && handleAdd('responsavel')}
            class="flex-1 px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:border-amber-500 outline-none text-sm font-semibold transition-all uppercase"
          />
          <button 
            onclick={() => handleAdd('responsavel')}
            disabled={!newResponsavel || isSaving}
            class="p-2 bg-amber-500 text-white rounded-xl hover:bg-amber-600 active:scale-95 transition-all disabled:opacity-50"
            title="Adicionar"
          >
            <Plus size={18} />
          </button>
        </div>

        <!-- Lista -->
        <div class="flex-1 overflow-y-auto p-2">
          <ul class="space-y-1">
            {#each responsaveis as item}
              <li class="group flex items-center justify-between p-3 hover:bg-amber-50/50 rounded-xl transition-colors">
                {#if editingId === item.id}
                  <div class="flex-1 flex flex-col sm:flex-row items-center gap-2">
                    <input 
                      type="text" 
                      bind:value={editingText}
                      class="flex-1 w-full px-3 py-1 bg-white border border-amber-300 rounded-lg outline-none text-xs font-bold uppercase transition-all shadow-sm"
                    />
                    <div class="flex items-center gap-1">
                      <button onclick={() => saveEdit('responsavel', item.id)} class="p-1.5 text-green-600 hover:bg-green-100 rounded-lg"><Check size={14}/></button>
                      <button onclick={cancelEdit} class="p-1.5 text-red-500 hover:bg-red-100 rounded-lg"><X size={14}/></button>
                    </div>
                  </div>
                {:else}
                  <span class="text-sm font-black text-gray-700 uppercase tracking-wide truncate pr-2">{item.nome}</span>
                  <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button onclick={() => startEdit(item)} class="p-1.5 text-gray-400 hover:text-amber-500 hover:bg-amber-50 rounded-lg transition-colors"><Edit2 size={14}/></button>
                    <button onclick={() => handleDelete('responsavel', item.id)} class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"><Trash2 size={14}/></button>
                  </div>
                {/if}
              </li>
            {/each}
          </ul>
        </div>
      </section>

    </div>

    <!-- SEÇÃO: AJUSTES DE SISTEMA (OPÇÕES OCULTAS/AVANÇADAS) -->
    <div class="mt-12 pt-8 border-t border-gray-100" in:fade>
      <div class="bg-gray-50/50 rounded-[2rem] border border-gray-100 p-8 space-y-6">
        <div class="flex items-center gap-3">
          <div class="p-2.5 bg-gray-200 text-gray-600 rounded-xl">
            <Database size={20} />
          </div>
          <div>
            <h2 class="text-xl font-black text-gray-900 tracking-tight">Ajustes de Sistema</h2>
            <p class="text-xs font-bold text-gray-400 uppercase tracking-widest mt-1">Configurações Avançadas e Infraestrutura</p>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div class="flex flex-col space-y-2">
            <label for="db-path" class="text-xs font-black text-gray-500 uppercase tracking-widest ml-1">Caminho do Banco de Dados (SQLite)</label>
            <div class="flex gap-2">
              <input 
                id="db-path"
                type="text" 
                bind:value={systemConfig.database_path}
                placeholder="Ex: C:/Usuarios/Nome/Documents/database.db"
                class="flex-1 px-5 py-3.5 bg-white border border-gray-200 rounded-2xl font-bold text-gray-900 focus:border-blue-600 outline-none transition-all shadow-sm"
              />
            </div>
            <p class="text-[10px] text-gray-400 font-medium ml-1">Mude este caminho para mover seus dados ou conectar a um backup externo.</p>
          </div>

          <div class="flex flex-col space-y-2">
            <label for="sys-port" class="text-xs font-black text-gray-500 uppercase tracking-widest ml-1">Porta do Servidor (Padrão: 8000)</label>
            <input 
              id="sys-port"
              type="number" 
              bind:value={systemConfig.port}
              class="w-32 px-5 py-3.5 bg-white border border-gray-200 rounded-2xl font-bold text-gray-900 focus:border-blue-600 outline-none transition-all shadow-sm"
            />
          </div>
        </div>

        <div class="flex justify-end pt-4">
          <button 
            onclick={handleSaveSystemConfig}
            disabled={isSaving}
            class="flex items-center gap-2 px-8 py-4 bg-gray-900 text-white font-black rounded-2xl hover:bg-black active:scale-95 transition-all shadow-lg disabled:opacity-50"
          >
            {#if isSaving}
              <Loader2 size={18} class="animate-spin" />
              Sincronizando...
            {:else}
              <Check size={18} />
              Salvar Ajustes de Sistema
            {/if}
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  ::-webkit-scrollbar {
    width: 4px;
  }
  ::-webkit-scrollbar-thumb {
    background: #e2e8f0;
    border-radius: 4px;
  }
  ::-webkit-scrollbar-thumb:hover {
    background: #cbd5e1;
  }
</style>
