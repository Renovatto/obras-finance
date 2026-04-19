<script lang="ts">
	import { ChevronDown, Calendar, Check } from 'lucide-svelte';
	import { fade } from 'svelte/transition';

	/**
	 * PeriodSelect - Seletor especializado para períodos mensais (ex: '2024-01').
	 */
	let { 
		value = $bindable(), 
		periods = [], 
		placeholder = "Todo o Histórico",
		class: classes = "",
		onchange = null
	} = $props();

	let isOpen = $state(false);

	// Formatador: '2024-03' -> 'Mar/2024'
	function formatLabel(p: string) {
		if (!p || !p.includes('-')) return placeholder;
		const [year, month] = p.split('-');
		const months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
		const monthIdx = parseInt(month) - 1;
		if (isNaN(monthIdx) || !months[monthIdx]) return placeholder;
		return `${months[monthIdx]}/${year}`;
	}

	let selectedLabel = $derived(formatLabel(value));

	function selectItem(p: string) {
		value = p;
		isOpen = false;
		if (onchange) onchange(p);
	}
</script>

<div class="flex flex-col space-y-1.5 w-full relative {classes}">
	<label class="text-[9px] font-black text-gray-400 uppercase tracking-widest ml-1 opacity-70">
		Período Mensal
	</label>
	
	<!-- Botão Gatilho -->
	<button
		type="button"
		onclick={() => isOpen = !isOpen}
		class="w-full flex items-center justify-between px-4 py-2.5 bg-white border border-gray-200 {isOpen ? 'border-blue-500 shadow-[0_0_0_3px_rgba(59,130,246,0.1)]' : 'hover:border-gray-300'} rounded-xl transition-all outline-none group"
	>
		<div class="flex items-center gap-2.5 truncate">
			<Calendar size={14} class="text-gray-400 group-hover:text-blue-500 transition-colors" />
			<span class="text-sm font-semibold {value ? 'text-gray-900' : 'text-gray-400'} truncate">
				{selectedLabel}
			</span>
		</div>
		
		<ChevronDown 
			size={16} 
			class="text-gray-400 transition-transform duration-200 {isOpen ? 'rotate-180' : 'group-hover:text-gray-500'}" 
		/>
	</button>

	<!-- Dropdown -->
	{#if isOpen}
		<div 
			class="absolute top-[calc(100%+8px)] left-0 right-0 bg-white border border-gray-100 shadow-xl rounded-xl z-50 overflow-hidden flex flex-col max-h-[300px]"
			transition:fade={{ duration: 100 }}
		>
			<div class="overflow-y-auto flex-1 p-1.5 space-y-0.5">
				<!-- Opção padrão (Todos) -->
				<button
					type="button"
					onclick={() => selectItem('')}
					class="w-full flex items-center justify-between px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium {value === '' ? 'text-blue-600 bg-blue-50/50' : 'text-gray-600'}"
				>
					<span>{placeholder}</span>
					{#if value === ''}
						<Check size={14} />
					{/if}
				</button>

				{#each periods as p}
					<button
						type="button"
						onclick={() => selectItem(p)}
						class="w-full flex items-center justify-between px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium {value === p ? 'text-blue-600 bg-blue-50/50' : 'text-gray-600'}"
					>
						<span>{formatLabel(p)}</span>
						{#if value === p}
							<Check size={14} />
						{/if}
					</button>
				{/each}
			</div>
		</div>
	{/if}
</div>

<!-- Backdrop -->
{#if isOpen}
	<div 
		class="fixed inset-0 z-40 bg-transparent" 
		onclick={() => isOpen = false}
		role="none"
	></div>
{/if}
