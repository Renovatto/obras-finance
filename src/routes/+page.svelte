<script lang="ts">
	import { onMount } from 'svelte';
	import { ui } from '$lib/stores/ui.svelte';
	import { api } from '$lib/api';
	import { 
		TrendingUp, TrendingDown, Wallet, DollarSign, 
		PieChart as PieChartIcon, BarChart3, Info, AlertCircle 
	} from 'lucide-svelte';
	import { fade, slide, scale } from 'svelte/transition';
	import DynamicSelect from '$lib/components/DynamicSelect.svelte';
	import PeriodSelect from '$lib/components/PeriodSelect.svelte';
	
	// Chart.js imports
	import { 
		Chart, CategoryScale, LinearScale, BarElement, Title, 
		Tooltip, Legend, ArcElement, BarController, DoughnutController 
	} from 'chart.js';

	// Registro de componentes do Chart.js
	Chart.register(
		CategoryScale, LinearScale, BarElement, Title, 
		Tooltip, Legend, ArcElement, BarController, DoughnutController
	);

	// --- ESTADOS (Runes Svelte 5) ---
	let isLoading = $state(true);
	let error = $state<string | null>(null);
	
	let kpis = $state({ total_receitas: 0, total_despesas: 0, saldo: 0 });
	let monthlyData = $state<any[]>([]);
	let categoryData = $state<any[]>([]);

	let plCanvas = $state<HTMLCanvasElement | null>(null);
	let catCanvas = $state<HTMLCanvasElement | null>(null);
	let plChart = $state<Chart | null>(null);
	let catChart = $state<Chart | null>(null);

	// --- FILTROS (Runes Svelte 5) ---
	let filters = $state({
		periodo: '',
		fk_categoria: '',
		fk_responsavel: ''
	});

	// Listas para os filtros
	let periods = $state<string[]>([]);
	let categories = $state<any[]>([]);
	let responsibles = $state<any[]>([]);

	async function loadAuxiliarData() {
		try {
			const [pRes, cRes, rRes] = await Promise.all([
				api.get<string[]>('/dashboard/periodos'),
				api.get<any[]>('/auxiliares/categorias/'),
				api.get<any[]>('/auxiliares/responsaveis/')
			]);
			periods = pRes;
			categories = cRes;
			responsibles = rRes;
		} catch (err) {
			console.error("Erro ao carregar auxiliares do dashboard:", err);
		}
	}

	async function loadDashboard() {
		isLoading = true;
		error = null;
		try {
			// Constrói query params baseado nos filtros
			const params = new URLSearchParams();
			if (filters.periodo !== 'todos') params.append('periodo', filters.periodo);
			if (filters.fk_categoria) params.append('fk_categoria', filters.fk_categoria);
			if (filters.fk_responsavel) params.append('fk_responsavel', filters.fk_responsavel);

			const query = params.toString() ? `?${params.toString()}` : '';

			// Busca concorrente de todos os dados necessários
			const [kpiRes, plRes, catRes] = await Promise.all([
				api.get<any>(`/dashboard/kpis${query}`),
				api.get<any[]>(`/dashboard/grafico-mensal${query}`),
				api.get<any[]>(`/dashboard/grafico-categorias${query}`)
			]);

			kpis = kpiRes;
			monthlyData = plRes;
			categoryData = catRes;

			// Inicializa gráficos após o próximo tick do Svelte
			setTimeout(initCharts, 0);
		} catch (err: any) {
			console.error("Erro ao carregar dashboard:", err);
			error = "Não foi possível carregar os dados financeiros.";
		} finally {
			isLoading = false;
		}
	}

	function initCharts() {
		// Destruir instâncias anteriores se existirem
		if (plChart) plChart.destroy();
		if (catChart) catChart.destroy();

		if (plCanvas) {
			plChart = new Chart(plCanvas, {
				type: 'bar',
				data: {
					labels: monthlyData.map(d => d.mes.split('-').reverse().join('/')),
					datasets: [
						{
							label: 'Receitas',
							data: monthlyData.map(d => d.receita),
							backgroundColor: '#10b981', // emerald-500
							borderRadius: 8,
						},
						{
							label: 'Despesas',
							data: monthlyData.map(d => d.despesa),
							backgroundColor: '#3b82f6', // blue-500
							borderRadius: 8,
						}
					]
				},
				options: {
					responsive: true,
					maintainAspectRatio: false,
					plugins: { legend: { position: 'bottom', labels: { font: { weight: 'bold' } } } },
					scales: { y: { beginAtZero: true, border: { display: false } }, x: { grid: { display: false } } }
				}
			});
		}

		if (catCanvas) {
			catChart = new Chart(catCanvas, {
				type: 'doughnut',
				data: {
					labels: categoryData.map(d => d.categoria),
					datasets: [{
						data: categoryData.map(d => d.total),
						backgroundColor: [
							'#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'
						],
						borderWidth: 0,
						hoverOffset: 20
					}]
				},
				options: {
					responsive: true,
					maintainAspectRatio: false,
					cutout: '70%',
					plugins: { 
						legend: { position: 'right', labels: { padding: 20, font: { weight: 'bold' } } } 
					}
				}
			});
		}
	}

	onMount(async () => {
		await loadAuxiliarData();
		await loadDashboard();
	});

	// Re-carregar quando filtros mudarem ou houver inserção (refreshTrigger)
	$effect(() => {
		ui.refreshTrigger; // Tracker
		// Rastreadores de dependência (runes)
		const { periodo, fk_categoria, fk_responsavel } = filters;
		loadDashboard();
	});

	// Formatador de Moeda
	const money = (val: number) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
</script>

<svelte:head>
	<title>ObrasFinance | Dashboard</title>
</svelte:head>

<div class="flex flex-col h-full max-w-[1600px] mx-auto w-full p-6 md:p-8 space-y-8">
	
	<!-- Header Seção -->
	<header class="flex items-center justify-between">
		<div>
			<h2 class="text-3xl font-black tracking-tight text-gray-900">Visão Geral</h2>
			<p class="text-gray-500 font-medium mt-1 uppercase text-xs tracking-widest opacity-70">Saúde Financeira dos Projetos</p>
		</div>
		
		{#if !isLoading && !error}
			<div class="flex items-center gap-2">
				<div class="bg-blue-600/5 text-blue-600 px-4 py-2 rounded-2xl border border-blue-100 flex items-center gap-2" in:fade>
					<Info size={14} />
					<span class="text-[10px] font-black uppercase tracking-tighter">
						{filters.periodo === 'todos' ? 'Todo o Histórico' : `Período: ${filters.periodo}`}
					</span>
				</div>
			</div>
		{/if}
	</header>

	<!-- Painel de Filtros Avançados -->
	<section id="tour-filtros" class="relative z-20 grid grid-cols-1 sm:grid-cols-3 gap-4 bg-white/50 backdrop-blur-sm p-4 rounded-[2rem] border border-gray-100 shadow-sm" in:slide>
		<!-- Filtro Período -->
		<PeriodSelect 
			bind:value={filters.periodo} 
			periods={periods} 
		/>

		<!-- Filtro Categoria -->
		<DynamicSelect 
			label="Categoria"
			endpoint="/auxiliares/categorias/"
			bind:value={filters.fk_categoria}
			placeholder="Todas as Categorias"
		/>

		<!-- Filtro Responsável -->
		<DynamicSelect 
			label="Responsável"
			endpoint="/auxiliares/responsaveis/"
			bind:value={filters.fk_responsavel}
			placeholder="Todos os Responsáveis"
		/>
	</section>

	{#if isLoading}
		<!-- Skeleton Loader -->
		<div class="flex-1 flex flex-col items-center justify-center p-12 h-96 w-full">
			<div class="w-12 h-12 border-4 border-gray-100 border-t-blue-600 rounded-full animate-spin"></div>
			<p class="mt-4 text-xs font-black text-gray-400 uppercase tracking-widest animate-pulse">Sincronizando Dados...</p>
		</div>
	{:else if error}
		<div class="bg-red-50 p-8 rounded-[2rem] border-2 border-red-100 flex flex-col items-center text-center space-y-4" in:slide>
			<AlertCircle size={48} class="text-red-500" />
			<h3 class="text-xl font-bold text-red-900">{error}</h3>
			<button 
				onclick={loadDashboard}
				class="px-6 py-2 bg-red-600 text-white font-bold rounded-xl active:scale-95 transition-all"
			>
				Tentar Novamente
			</button>
		</div>
	{:else}
		<!-- KPI Grid -->
		<div class="grid grid-cols-1 md:grid-cols-3 gap-6 w-full" in:slide={{ duration: 400 }}>
			<!-- Card Saldo -->
			<div id="tour-saldo" class="bg-white p-6 rounded-[2rem] shadow-xl shadow-gray-200/50 border border-gray-100 flex flex-col justify-between hover:scale-[1.02] transition-all group">
				<div class="flex justify-between items-start">
					<div class="p-3 bg-blue-600 text-white rounded-2xl shadow-lg shadow-blue-200 group-hover:rotate-6 transition-transform">
						<Wallet size={24} />
					</div>
					<div class="text-right">
						<p class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Saldo Atual</p>
						<p class="text-3xl font-black text-gray-900 mt-1">{money(kpis.saldo)}</p>
					</div>
				</div>
				<div class="mt-6 flex items-center justify-between text-xs font-bold text-gray-400">
					<span>Total Consolidado</span>
					<div class="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
				</div>
			</div>

			<!-- Card Receitas -->
			<div id="tour-receitas" class="bg-emerald-600 p-6 rounded-[2rem] shadow-xl shadow-emerald-200/50 text-white flex flex-col justify-between hover:scale-[1.02] transition-all group overflow-hidden relative">
				<div class="absolute -right-4 -top-4 opacity-10 group-hover:scale-110 transition-transform">
					<TrendingUp size={120} />
				</div>
				<div class="flex justify-between items-start z-10">
					<div class="p-3 bg-white/20 backdrop-blur-md rounded-2xl">
						<TrendingUp size={24} />
					</div>
					<div class="text-right">
						<p class="text-[10px] font-black text-white/60 uppercase tracking-widest">Total Receitas</p>
						<p class="text-3xl font-black mt-1">{money(kpis.total_receitas)}</p>
					</div>
				</div>
				<p class="mt-6 text-xs font-bold text-white/70 z-10">Entradas este ano</p>
			</div>

			<!-- Card Despesas -->
			<div class="bg-blue-600 p-6 rounded-[2rem] shadow-xl shadow-blue-200/50 text-white flex flex-col justify-between hover:scale-[1.02] transition-all group overflow-hidden relative">
				<div class="absolute -right-4 -top-4 opacity-10 group-hover:scale-110 transition-transform">
					<TrendingDown size={120} />
				</div>
				<div class="flex justify-between items-start z-10">
					<div class="p-3 bg-white/20 backdrop-blur-md rounded-2xl">
						<TrendingDown size={24} />
					</div>
					<div class="text-right">
						<p class="text-[10px] font-black text-white/60 uppercase tracking-widest">Total Despesas</p>
						<p class="text-3xl font-black mt-1">{money(kpis.total_despesas)}</p>
					</div>
				</div>
				<p class="mt-6 text-xs font-bold text-white/70 z-10">Saídas este ano</p>
			</div>
		</div>

		<!-- Charts Section -->
		<div class="grid grid-cols-1 lg:grid-cols-5 gap-6 w-full pb-8">
			
			<!-- Gráfico P&L Mensal -->
			<section class="lg:col-span-3 bg-white p-6 rounded-[2rem] shadow-xl shadow-gray-200/40 border border-gray-100 flex flex-col h-[480px]" in:fade={{ delay: 100 }}>
				<div class="flex items-center justify-between mb-6">
					<div class="flex items-center gap-3">
						<div class="p-2 bg-gray-50 rounded-xl text-gray-400 scale-90">
							<BarChart3 size={20} />
						</div>
						<h3 class="text-lg font-black text-gray-900 tracking-tight">Evolução Mensal</h3>
					</div>
				</div>
				<div class="flex-1 relative">
					<canvas bind:this={plCanvas}></canvas>
				</div>
			</section>

			<!-- Gráfico Categorias -->
			<section class="lg:col-span-2 bg-white p-6 rounded-[2rem] shadow-xl shadow-gray-200/40 border border-gray-100 flex flex-col h-[480px]" in:fade={{ delay: 200 }}>
				<div class="flex items-center justify-between mb-6">
					<div class="flex items-center gap-3">
						<div class="p-2 bg-gray-50 rounded-xl text-gray-400 scale-90">
							<PieChartIcon size={20} />
						</div>
						<h3 class="text-lg font-black text-gray-900 tracking-tight">Por Categoria</h3>
					</div>
				</div>
				<div class="flex-1 relative">
					<canvas bind:this={catCanvas}></canvas>
				</div>
			</section>

		</div>
	{/if}
</div>
