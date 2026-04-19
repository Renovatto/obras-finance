<script lang="ts">
	import '../app.postcss';
	import { Home, Wallet, PieChart, HardHat, Settings } from 'lucide-svelte';
	import Topbar from '$lib/components/Topbar.svelte';
	import LaunchModal from '$lib/components/LaunchModal.svelte';
	import RightMenuDrawer from '$lib/components/RightMenuDrawer.svelte';
	import { ui } from '$lib/stores/ui.svelte';

	let { children } = $props();

	// Estrutura de rotas principal
	const navItems = [
		{ name: 'Dashboard', icon: Home, href: '/' },
		{ name: 'Finanças', icon: Wallet, href: '/lancamentos' },
		{ name: 'Obras', icon: HardHat, href: '/obras' },
		{ name: 'Relatórios', icon: PieChart, href: '/relatorios' }
	];
</script>

<div class="flex h-screen w-full bg-gray-50/50 overflow-hidden font-sans">
	
	<!-- Topbar Fixa (Z-40) -->
	<Topbar />

	<!-- Layout em Row para Sidebar + Conteúdo -->
	<div class="flex flex-1 pt-16 h-full w-full overflow-hidden">
		
		<!-- [DESKTOP] Sidebar (Z-30) -->
		<aside class="hidden md:flex w-72 flex-col bg-white border-r border-gray-100 shadow-[2px_0_12px_rgba(0,0,0,0.02)] h-full z-30">
			<nav class="flex-1 px-4 py-8 space-y-1.5 overflow-y-auto w-full">
				{#each navItems as item}
					<a
						href={item.href}
						class="flex items-center gap-3.5 px-4 py-3.5 rounded-2xl text-gray-500 hover:bg-blue-50/50 hover:text-blue-600 transition-all active:scale-[0.98] cursor-pointer font-semibold group"
					>
						<div class="p-2 transition-colors group-hover:bg-white group-hover:shadow-sm rounded-lg">
							<item.icon size={20} strokeWidth={2.25} />
						</div>
						<span class="tracking-tight">{item.name}</span>
					</a>
				{/each}
			</nav>

			<!-- Footer Sidebar (User Info ou algo assim) -->
			<div class="p-6 border-t border-gray-50">
				<div class="flex items-center gap-3 p-3 rounded-2xl bg-gray-50 border border-gray-100/50">
					<div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold shadow-sm">
						A
					</div>
					<div class="flex flex-col">
						<span class="text-sm font-bold text-gray-900">André S.</span>
						<span class="text-[10px] font-bold text-blue-600 uppercase tracking-widest">Admin</span>
					</div>
				</div>
			</div>
		</aside>

		<!-- [ÁREA PRINCIPAL] Conteúdo -->
		<main class="flex-1 flex flex-col h-full relative overflow-y-auto pb-24 md:pb-6 z-0">
			<!-- Transição suave entre páginas -->
			<div class="w-full">
				{@render children()}
			</div>
		</main>
	</div>

	<!-- [MOBILE] Bottom Navigation Fixa (Z-50) -->
	<nav class="md:hidden fixed bottom-0 left-0 w-full bg-white/90 backdrop-blur-lg border-t border-gray-100 shadow-[0_-8px_20px_rgba(0,0,0,0.05)] pb-safe pt-2 z-50">
		<div class="flex justify-around items-center px-4 pb-2">
			{#each navItems as item}
				<a
					href={item.href}
					class="flex flex-col items-center gap-1.5 p-2 w-20 text-gray-400 hover:text-blue-600 transition-all active:scale-90"
				>
					<div class="p-2 rounded-xl transition-colors">
						<item.icon size={24} strokeWidth={2.25} />
					</div>
					<span class="text-[10px] font-bold tracking-wider uppercase opacity-80">{item.name}</span>
				</a>
			{/each}
		</div>
	</nav>

	<!-- Menu Oculto da Direita -->
	<RightMenuDrawer />

	<!-- Modal Global de Lançamento (Z-100) -->
	<LaunchModal />
</div>

<style>
	/* Garantir que o scroll principal seja suave */
	:global(html) {
		scroll-behavior: smooth;
	}
</style>
