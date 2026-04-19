<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { Plus, Check, Loader2, ChevronDown } from 'lucide-svelte';
	import { fade, slide } from 'svelte/transition';

	/**
	 * DynamicSelect - Dropdown assíncrono com cadastro rápido inline.
	 */
	let { 
		label, 
		endpoint, 
		value = $bindable(), 
		placeholder = "Selecione uma opção...",
		class: classes = "",
		onchange = null, // Callback opcional
		allowAdd = true // Permite desativar o cadastro rápido
	} = $props();

	let items = $state<any[]>([]);
	let isLoading = $state(true);
	let isOpen = $state(false);
	let isAddingNew = $state(false);
	let newItemName = $state("");
	let isSavingNew = $state(false);

	// Pega o nome do item selecionado para mostrar no placeholder
	let selectedLabel = $derived(
		items.find(i => i.id === value)?.nome || placeholder
	);

	async function loadItems() {
		try {
			// Alguns endpoints podem retornar listas simples ou objetos (como o /todos)
			// Aqui assumimos que o endpoint passado retorna a lista diretamente (ex: /categorias/)
			items = await api.get<any[]>(endpoint);
		} catch (err) {
			console.error("Erro ao carregar itens de", endpoint, err);
		} finally {
			isLoading = false;
		}
	}

	onMount(loadItems);

	async function handleAddNew() {
		if (!newItemName.trim()) return;
		
		isSavingNew = true;
		try {
			// POST idempotente conforme implementado no backend (recebe só nome)
			const newItem = await api.post<any>(endpoint, { nome: newItemName });
			
			// Recarrega lista e seleciona o novo
			await loadItems();
			value = newItem.id;
			
			// Reset estado
			isAddingNew = false;
			newItemName = "";
			isOpen = false;
		} catch (err) {
			console.error("Erro ao cadastrar novo item:", err);
		} finally {
			isSavingNew = false;
		}
	}

	function selectItem(id: string) {
		value = id;
		isOpen = false;
		if (onchange) onchange(id);
	}
</script>

<div class="flex flex-col space-y-1.5 w-full relative {classes}">
	<label class="text-xs font-bold text-gray-700 ml-1 uppercase tracking-widest opacity-60">
		{label}
	</label>
	
	<!-- Botão Gatilho Dropdown -->
	<button
		type="button"
		onclick={() => isOpen = !isOpen}
		class="w-full flex items-center justify-between px-4 py-2.5 bg-white border border-gray-200 {isOpen ? 'border-blue-500 shadow-[0_0_0_3px_rgba(59,130,246,0.1)]' : 'hover:border-gray-300'} rounded-xl transition-all outline-none group"
	>
		<span class="text-sm font-semibold {value ? 'text-gray-900' : 'text-gray-400'} truncate">
			{selectedLabel}
		</span>
		
		{#if isLoading}
			<Loader2 size={14} class="animate-spin text-gray-300" />
		{:else}
			<ChevronDown 
				size={16} 
				class="text-gray-400 transition-transform duration-200 {isOpen ? 'rotate-180' : 'group-hover:text-gray-500'}" 
			/>
		{/if}
	</button>

	<!-- Menu suspenso -->
	{#if isOpen}
		<div 
			class="absolute top-[calc(100%+8px)] left-0 right-0 bg-white border border-gray-100 shadow-xl rounded-xl z-50 overflow-hidden flex flex-col max-h-[300px]"
			transition:fade={{ duration: 100 }}
		>
			<div class="overflow-y-auto flex-1 p-1.5 space-y-0.5">
				{#each items as item}
					<button
						type="button"
						onclick={() => selectItem(item.id)}
						class="w-full flex items-center justify-between px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium {value === item.id ? 'text-blue-600 bg-blue-50/50' : 'text-gray-600'}"
					>
						<span>{item.nome}</span>
						{#if value === item.id}
							<Check size={14} />
						{/if}
					</button>
				{:else}
					{#if !isLoading}
						<p class="p-4 text-xs font-bold text-gray-400 italic">Nenhuma opção encontrada</p>
					{/if}
				{/each}
			</div>

			<!-- Rodapé de Cadastro Rápido -->
			{#if allowAdd}
				<div class="border-t border-gray-50 bg-gray-50/30 p-2">
					{#if isAddingNew}
						<div class="flex items-center gap-1.5" in:slide={{ duration: 150 }}>
							<input
								type="text"
								bind:value={newItemName}
								placeholder="Novo item..."
								class="flex-1 bg-white border border-gray-200 rounded-lg px-2.5 py-1.5 text-xs font-semibold focus:border-blue-500 outline-none transition-all"
								onkeydown={(e) => e.key === 'Enter' && handleAddNew()}
							/>
							<button 
								type="button"
								onclick={handleAddNew}
								disabled={isSavingNew || !newItemName}
								class="p-1.5 bg-blue-600 text-white rounded-lg active:scale-95 disabled:opacity-50"
							>
								{#if isSavingNew}
									<Loader2 size={14} class="animate-spin" />
								{:else}
									<Plus size={14} />
								{/if}
							</button>
						</div>
					{:else}
						<button
							type="button"
							onclick={() => isAddingNew = true}
							class="w-full flex items-center justify-center gap-1.5 px-3 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-all text-xs font-bold active:scale-[0.98]"
						>
							<Plus size={14} />
							<span>Adicionar Novo</span>
						</button>
					{/if}
				</div>
			{/if}
		</div>
	{/if}
</div>

<!-- Backdrop para fechar ao clicar fora (Simplificado) -->
{#if isOpen}
	<div 
		class="fixed inset-0 z-40 bg-transparent" 
		onclick={() => { isOpen = false; isAddingNew = false; }}
		role="none"
	></div>
{/if}
