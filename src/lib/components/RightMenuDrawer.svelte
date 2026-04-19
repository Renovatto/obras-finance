<script lang="ts">
	import { Settings, ChevronLeft, ChevronRight } from 'lucide-svelte';
	import { fade, slide } from 'svelte/transition';
	
	let isOpen = $state(false);
</script>

<div class="fixed top-1/2 right-0 -translate-y-1/2 z-50 flex items-center">
	
	<!-- Botão Seta (Gatilho) -->
	<button 
		onclick={() => isOpen = !isOpen}
		class="bg-white border text-gray-400 hover:text-blue-600 shadow-xl p-2 rounded-l-2xl border-r-0 {isOpen ? 'border-blue-500 bg-blue-50 text-blue-600 shadow-blue-200/50' : 'border-gray-200 hover:bg-gray-50'} transition-all flex items-center justify-center outline-none"
	>
		{#if isOpen}
			<ChevronRight size={20} />
		{:else}
			<ChevronLeft size={20} />
		{/if}
	</button>

	<!-- Painel Deslizante -->
	{#if isOpen}
		<div transition:slide={{ axis: 'x', duration: 300 }} class="bg-white border-y border-l border-gray-200 shadow-2xl h-auto py-4 pl-4 pr-6 rounded-l-[2rem] flex flex-col gap-2">
			
			<div class="border-b border-gray-100 pb-2 mb-2 flex flex-col">
				<span class="text-[10px] font-black uppercase tracking-widest text-gray-400">Opções Ocultas</span>
			</div>

			<a 
				href="/ajustes"
				onclick={() => { isOpen = false; }}
				class="flex items-center gap-3 px-4 py-3 bg-gray-50 hover:bg-blue-600 text-gray-700 hover:text-white rounded-xl transition-all shadow-sm active:scale-95 group font-bold text-sm"
			>
				<Settings size={18} class="group-hover:animate-spin-slow" />
				Ajustes Gerais
			</a>
			
		</div>
	{/if}

</div>

<style>
	:global(.animate-spin-slow) {
		animation: spin 3s linear infinite;
	}
</style>
