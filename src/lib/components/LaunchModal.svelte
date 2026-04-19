<script lang="ts">
	import { slide } from 'svelte/transition';
	import { ui } from '$lib/stores/ui.svelte';
	import { api } from '$lib/api';
	import { Check, ArrowUpCircle, ArrowDownCircle, Loader2 } from 'lucide-svelte';
	import CurrencyInput from './CurrencyInput.svelte';
	import DynamicSelect from './DynamicSelect.svelte';
	import Modal from './Modal.svelte';

	let isSubmitting = $state(false);

	// Estado Inicial do Lançamento (Factory para reset limpo)
	function createInitialState() {
		return {
			tipo: 'Despesa', 
			data: new Date().toISOString().split('T')[0],
			valor: 0,
			status: 'Pendente',
			descricao: '',
			notas: '',
			fk_categoria: '',
			fk_forma_pagamento: '',
			fk_responsavel: '',
			fk_obra: null as string | null
		};
	}

	let form = $state(createInitialState());

	// Sicronização com modalData (Edição/Duplicação)
	$effect(() => {
		if (ui.isLaunchModalOpen) {
			// Sempre começa com um estado limpo
			const freshState = createInitialState();
			
			if (ui.modalData) {
				// Se houver dados (Edit/Duplicate), mescla com o estado limpo
				Object.keys(freshState).forEach(key => {
					// @ts-ignore
					form[key] = ui.modalData[key] ?? freshState[key];
				});
			} else {
				// Se for novo lançamento, garante que tudo é resetado
				Object.assign(form, freshState);
			}
		}
	});

	let isEdit = $derived(ui.modalData && ui.modalData.id);
	let modalTitle = $derived(isEdit ? 'Editar Lançamento' : ui.modalData ? 'Duplicar Lançamento' : 'Novo Lançamento');

	// Estilos dinâmicos baseados no tipo
	let buttonClass = $derived(
		form.tipo === 'Receita' 
			? 'bg-emerald-600 hover:bg-emerald-700 shadow-emerald-100' 
			: 'bg-blue-600 hover:bg-blue-700 shadow-blue-100'
	);

	import { invalidateAll } from '$app/navigation';

	async function handleSubmit(e: Event) {
		e.preventDefault();
		if (isSubmitting) return;

		isSubmitting = true;
		try {
			// Prepara payload mapeando o fk_obra para null (em vez de "") se não estiver setado
			const payload = { 
				...form, 
				fk_obra: form.fk_obra ? form.fk_obra : null 
			};

			if (isEdit) {
				await api.put(`/lancamentos/${ui.modalData.id}`, payload);
			} else {
				await api.post('/lancamentos/', payload);
			}
			
			// Notifica o SvelteKit que os dados mudaram (atualiza dashboard/listas)
			await invalidateAll();
			ui.triggerRefresh();
			ui.closeLaunchModal();
		} catch (err) {
			alert("Erro ao salvar lançamento. Verifique os dados.");
		} finally {
			isSubmitting = false;
		}
	}
</script>

<Modal bind:isOpen={ui.isLaunchModalOpen} title={modalTitle}>
	{#snippet subtitle()}
		<p class="text-xs font-bold text-gray-400 uppercase tracking-widest mt-0.5">Gestão de Fluxo de Caixa</p>
	{/snippet}

	<div class="space-y-8">
		<!-- Seletor de Tipo (Receita vs Despesa) -->
		<div class="bg-gray-100 p-1.5 rounded-2xl flex items-center gap-1.5">
			<button
				type="button"
				onclick={() => form.tipo = 'Receita'}
				class="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl font-black text-sm transition-all {form.tipo === 'Receita' ? 'bg-white text-emerald-600 shadow-sm' : 'text-gray-500 opacity-60'}"
			>
				<ArrowUpCircle size={18} />
				Receita
			</button>
			<button
				type="button"
				onclick={() => form.tipo = 'Despesa'}
				class="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl font-black text-sm transition-all {form.tipo === 'Despesa' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-500 opacity-60'}"
			>
				<ArrowDownCircle size={18} />
				Despesa
			</button>
		</div>

		<!-- Grid Principal -->
		<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
			<div class="md:col-span-2">
				<CurrencyInput bind:value={form.valor} label="Quanto?" />
			</div>

			<div class="flex flex-col space-y-1.5">
				<label for="input-data" class="text-xs font-bold text-gray-700 ml-1 uppercase tracking-widest opacity-60">Data</label>
				<input id="input-data" type="date" bind:value={form.data} class="w-full px-5 py-3.5 bg-gray-50 border-2 border-transparent rounded-2xl font-bold text-gray-900 focus:bg-white focus:border-blue-600 outline-none transition-all" />
			</div>

			<div class="flex flex-col space-y-1.5">
				<label for="input-status" class="text-xs font-bold text-gray-700 ml-1 uppercase tracking-widest opacity-60">Status</label>
				<select id="input-status" bind:value={form.status} class="w-full px-5 py-3.5 bg-gray-50 border-2 border-transparent rounded-2xl font-bold text-gray-900 focus:bg-white focus:border-blue-600 outline-none transition-all appearance-none">
					<option value="Pendente">Aberto / Pendente</option>
					<option value="Pago">Liquidado / Pago</option>
				</select>
			</div>

			<div class="md:col-span-2 flex flex-col space-y-1.5">
				<label for="input-descricao" class="text-xs font-bold text-gray-700 ml-1 uppercase tracking-widest opacity-60">Descrição</label>
				<input 
					id="input-descricao"
					type="text" 
					bind:value={form.descricao} 
					maxlength="60"
					placeholder="Breve descrição (ex: Cimento CP-II)"
					class="w-full px-5 py-3.5 bg-gray-50 border-2 border-transparent rounded-2xl font-bold text-gray-900 focus:bg-white focus:border-blue-600 outline-none transition-all" 
				/>
			</div>

			<div class="md:col-span-2">
				<DynamicSelect label="Categoria" endpoint="/auxiliares/categorias/" bind:value={form.fk_categoria} />
			</div>

			<DynamicSelect label="Forma de Pagamento" endpoint="/auxiliares/formas-pagamento/" bind:value={form.fk_forma_pagamento} />
			<DynamicSelect label="Responsável" endpoint="/auxiliares/responsaveis/" bind:value={form.fk_responsavel} />
			
			<div class="md:col-span-2">
				<DynamicSelect label="Obra (Opcional)" endpoint="/obras/" bind:value={form.fk_obra} placeholder="Geral / Sem Obra" />
			</div>

			<div class="md:col-span-2 flex flex-col space-y-1.5">
				<div class="flex justify-between items-center ml-1">
					<label for="input-notas" class="text-xs font-bold text-gray-700 uppercase tracking-widest opacity-60">Notas</label>
					<span class="text-[10px] font-black {form.notas.length > 240 ? 'text-red-500' : 'text-gray-400'} uppercase tracking-tighter">
						{form.notas.length} / 255
					</span>
				</div>
				<textarea 
					id="input-notas"
					bind:value={form.notas} 
					rows="2" 
					maxlength="255"
					placeholder="Observações adicionais, nota fiscal, etc..." 
					class="w-full px-5 py-4 bg-gray-50 border-2 border-transparent rounded-2xl font-bold text-gray-900 focus:bg-white focus:border-blue-600 outline-none transition-all resize-none"
				></textarea>
			</div>
		</div>

		<!-- Ações -->
		<div class="flex items-center justify-end gap-4 pt-4 border-t border-gray-100">
			<button type="button" onclick={() => ui.closeLaunchModal()} class="px-6 py-4 text-sm font-black text-gray-500 hover:text-gray-700 active:scale-95 transition-all">Cancelar</button>
			<button type="button" onclick={handleSubmit} disabled={isSubmitting || !form.descricao || !form.valor} class="px-10 py-4 {buttonClass} text-white font-black rounded-2xl transition-all shadow-lg active:scale-95 disabled:opacity-50 flex items-center gap-3">
				{#if isSubmitting}
					<Loader2 size={20} class="animate-spin" />
					Salvando...
				{:else}
					<Check size={20} />
					Confirmar {form.tipo}
				{/if}
			</button>
		</div>
	</div>
</Modal>

<style>
	/* Esconder scrollbar mas permitir scroll */
	.scrollbar-hide::-webkit-scrollbar {
		display: none;
	}
	.scrollbar-hide {
		-ms-overflow-style: none;
		scrollbar-width: none;
	}
</style>
