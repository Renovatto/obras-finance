<script lang="ts">
	import { ui } from '$lib/stores/ui.svelte';
	import { api } from '$lib/api';
	import { Check, Loader2, HardHat } from 'lucide-svelte';
	import CurrencyInput from './CurrencyInput.svelte';
	import Modal from './Modal.svelte';

	let isSubmitting = $state(false);

	// Estado Inicial da Obra
	function createInitialState() {
		return {
			nome: '',
			nome_cliente: '',
			custo_estimado: 0,
			data_inicio: new Date().toISOString().split('T')[0],
			data_fim: '',
			descricao: ''
		};
	}

	let form = $state(createInitialState());

	// Prop que controla a abertura localmente (mas injetada pela Store caso o botão acione)
	let { isOpen = $bindable(false), modalData = null, onSave } = $props();

	$effect(() => {
		if (isOpen) {
			const freshState = createInitialState();
			if (modalData) {
				Object.keys(freshState).forEach(key => {
					// @ts-ignore
					form[key] = modalData[key] ?? freshState[key];
				});
			} else {
				Object.assign(form, freshState);
			}
		}
	});

	let isEdit = $derived(modalData && modalData.id);
	let modalTitle = $derived(isEdit ? 'Editar Obra' : 'Nova Obra');

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (isSubmitting) return;

		isSubmitting = true;
		try {
			// Prepara payload mapeando string vazia de data_fim para null se necessário
			const payload = {
				...form,
				data_fim: form.data_fim ? form.data_fim : null
			};

			if (isEdit) {
				await api.put(`/obras/${modalData.id}`, payload);
			} else {
				await api.post('/obras/', payload);
			}
			
			if (onSave) onSave();
			isOpen = false;
		} catch (err) {
			console.error("Erro ao salvar Obra:", err);
			alert("Erro ao salvar Obra. Verifique os dados.");
		} finally {
			isSubmitting = false;
		}
	}
</script>

<Modal bind:isOpen={isOpen} title={modalTitle}>
	{#snippet subtitle()}
		<div class="flex items-center gap-1 mt-0.5 text-gray-400">
			<HardHat size={12} />
			<p class="text-xs font-bold uppercase tracking-widest">Gestão de Obras</p>
		</div>
	{/snippet}

	<form onsubmit={handleSubmit} class="space-y-6 pt-2">
		<!-- Grid Principal -->
		<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
			
			<div class="md:col-span-2 flex flex-col space-y-1.5">
				<label class="text-xs font-bold text-gray-700 ml-1 uppercase tracking-widest opacity-60">Nome da Obra *</label>
				<input 
					type="text" 
					bind:value={form.nome} 
					required
					maxlength="255"
					placeholder="Ex: Residência Alto da Serra"
					class="w-full px-5 py-3.5 bg-gray-50 border-2 border-transparent rounded-2xl font-bold text-gray-900 focus:bg-white focus:border-blue-600 outline-none transition-all" 
				/>
			</div>

			<div class="flex flex-col space-y-1.5">
				<label class="text-xs font-bold text-gray-700 ml-1 uppercase tracking-widest opacity-60">Nome do Cliente *</label>
				<input 
					type="text" 
					bind:value={form.nome_cliente} 
					required
					maxlength="255"
					placeholder="Ex: Maria Souza"
					class="w-full px-5 py-3.5 bg-gray-50 border-2 border-transparent rounded-2xl font-bold text-gray-900 focus:bg-white focus:border-blue-600 outline-none transition-all" 
				/>
			</div>

			<div class="flex flex-col space-y-1.5">
				<CurrencyInput bind:value={form.custo_estimado} label="Custo Estimado *" />
			</div>

			<div class="flex flex-col space-y-1.5">
				<label class="text-xs font-bold text-gray-700 ml-1 uppercase tracking-widest opacity-60">Data de Início *</label>
				<input 
					type="date" 
					bind:value={form.data_inicio} 
					required
					class="w-full px-5 py-3.5 bg-gray-50 border-2 border-transparent rounded-2xl font-bold text-gray-900 focus:bg-white focus:border-blue-600 outline-none transition-all" 
				/>
			</div>

			<div class="flex flex-col space-y-1.5">
				<label class="text-xs font-bold text-gray-700 ml-1 uppercase tracking-widest opacity-60">Previsão Fim</label>
				<input 
					type="date" 
					bind:value={form.data_fim} 
					class="w-full px-5 py-3.5 bg-gray-50 border-2 border-transparent rounded-2xl font-bold text-gray-900 focus:bg-white focus:border-blue-600 outline-none transition-all" 
				/>
			</div>

			<div class="md:col-span-2 flex flex-col space-y-1.5">
				<label class="text-xs font-bold text-gray-700 ml-1 uppercase tracking-widest opacity-60">Descrição Detalhada</label>
				<textarea 
					bind:value={form.descricao} 
					rows="3" 
					placeholder="Descrição adicional da obra..." 
					class="w-full px-5 py-4 bg-gray-50 border-2 border-transparent rounded-2xl font-bold text-gray-900 focus:bg-white focus:border-blue-600 outline-none transition-all resize-none"
				></textarea>
			</div>
		</div>

		<!-- Ações -->
		<div class="flex items-center justify-end gap-4 pt-6 border-t border-gray-100">
			<button type="button" onclick={() => isOpen = false} class="px-6 py-4 text-sm font-black text-gray-500 hover:text-gray-700 active:scale-95 transition-all">Cancelar</button>
			<button type="submit" disabled={isSubmitting || !form.nome || !form.nome_cliente || !form.data_inicio} class="px-10 py-4 bg-blue-600 hover:bg-blue-700 shadow-blue-100 text-white font-black rounded-2xl transition-all shadow-lg active:scale-95 disabled:opacity-50 flex items-center gap-3">
				{#if isSubmitting}
					<Loader2 size={20} class="animate-spin" />
					Salvando...
				{:else}
					<Check size={20} />
					Confirmar Obra
				{/if}
			</button>
		</div>
	</form>
</Modal>
