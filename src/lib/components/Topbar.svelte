<script lang="ts">
	import { Home, Wallet, PieChart, Users, HardHat, Plus } from 'lucide-svelte';
	import { ui } from '$lib/stores/ui.svelte';

	// Componente de navegação superior fixa
</script>

<header class="fixed top-0 left-0 right-0 h-16 bg-white/80 backdrop-blur-md border-b border-gray-100 z-40 px-4 md:px-8 flex items-center justify-between shadow-sm">
	<div class="flex items-center gap-2">
		<!-- Logotipo / Título (Mobile: só ícone ou texto curto) -->
		<div class="p-2 bg-blue-600 rounded-lg text-white shadow-lg shadow-blue-200">
			<HardHat size={20} />
		</div>
		<span class="text-xl font-bold tracking-tight text-gray-900 hidden sm:block">
			Obras<span class="text-blue-600">Finance</span>
		</span>
	</div>

	<div class="flex items-center gap-3">
		<!-- Botão Global Proeminente -->
		<button
			onclick={() => ui.openLaunchModal()}
			class="flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white text-sm font-bold rounded-xl transition-all shadow-md shadow-blue-100 active:scale-95 group"
		>
			<Plus size={18} class="group-hover:rotate-90 transition-transform duration-300" />
			<span class="hidden md:inline">Novo Lançamento</span>
			<span class="md:hidden">Novo</span>
		</button>
	</div>
</header>
