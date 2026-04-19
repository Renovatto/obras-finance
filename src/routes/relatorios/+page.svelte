<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { fade, slide } from 'svelte/transition';
	import { 
		TrendingUp, TrendingDown, Target, CheckCircle2, 
		PieChart, Briefcase, Activity, Building2, ExternalLink
	} from 'lucide-svelte';
	
	import { 
		Chart, CategoryScale, LinearScale, PointElement, LineElement, 
		Title, Tooltip, Legend, Filler 
	} from 'chart.js';

	Chart.register(
		CategoryScale, LinearScale, PointElement, LineElement, 
		Title, Tooltip, Legend, Filler
	);

	let isLoading = $state(true);
	
	// Dados
	let kpis = $state({ total_receitas: 0, total_despesas: 0, saldo: 0 });
	let plData = $state<any[]>([]);
	let portfolio = $state<any[]>([]);

	let plCanvas = $state<HTMLCanvasElement | null>(null);
	let chartInstance = $state<Chart | null>(null);

	async function loadAllData() {
		isLoading = true;
		try {
			// Busca KPIs do histórico completo (passando periodo=todos)
			const kpiRes = await api.get<any>('/dashboard/kpis?periodo=todos');
			
			// Busca P&L do histórico mensal
			const monthlyRes = await api.get<any[]>('/dashboard/grafico-mensal?periodo=todos');
			
			// Busca Portfólio Budget Obras
			const obrasRes = await api.get<any[]>('/relatorios/obras-budget');

			kpis = kpiRes;
			plData = monthlyRes;
			portfolio = obrasRes;
		} catch (error) {
			console.error("Erro ao carregar os relatórios:", error);
		} finally {
			isLoading = false;
		}
	}

	// Svelte 5: React to data loading and canvas availability
	$effect(() => {
		if (!isLoading && plData.length >= 0 && plCanvas) {
			initChart();
		}
	});

	onMount(() => {
		loadAllData();
	});

	function initChart() {
		if (chartInstance) chartInstance.destroy();
		if (!plCanvas) return;

		// Se o histórico for muito pequeno, adiciona placeholders visuais
		const labels = plData.map(d => d.mes.split('-').reverse().join('/'));
		const receitas = plData.map(d => d.receita);
		const despesas = plData.map(d => d.despesa);

		chartInstance = new Chart(plCanvas, {
			type: 'line',
			data: {
				labels,
				datasets: [
					{
						label: 'Receita',
						data: receitas,
						borderColor: '#3b82f6', // blue-500
						backgroundColor: 'rgba(59, 130, 246, 0.1)',
						borderWidth: 3,
						pointBackgroundColor: '#ffffff',
						pointBorderColor: '#3b82f6',
						pointBorderWidth: 2,
						pointRadius: 4,
						fill: true,
						tension: 0.4 // Bezier curve para suavidade
					},
					{
						label: 'Despesas',
						data: despesas,
						borderColor: '#f59e0b', // amber-500
						backgroundColor: 'rgba(245, 158, 11, 0.1)',
						borderWidth: 3,
						pointBackgroundColor: '#ffffff',
						pointBorderColor: '#f59e0b',
						pointBorderWidth: 2,
						pointRadius: 4,
						fill: true,
						tension: 0.4
					}
				]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					legend: { position: 'top', labels: { font: { weight: 'bold' } } },
					tooltip: {
						mode: 'index',
						intersect: false,
						backgroundColor: 'rgba(255, 255, 255, 0.9)',
						titleColor: '#1f2937',
						bodyColor: '#4b5563',
						borderColor: '#e5e7eb',
						borderWidth: 1,
						titleFont: { size: 14, weight: 'bold' }
					}
				},
				interaction: {
					mode: 'nearest',
					axis: 'x',
					intersect: false
				},
				scales: {
					y: { beginAtZero: true, grid: { color: '#f3f4f6' }, border: { display: false } },
					x: { grid: { display: false } }
				}
			}
		});
	}

	const money = (val: number | string) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(Number(val));
	
	// Lógica de Cor do Progresso
	function getProgressColor(percent: number, gasto: number, orcado: number) {
		if (orcado === 0 && gasto > 0) return 'bg-red-500'; // Estouro de 0
		if (percent <= 50) return 'bg-emerald-500';
		if (percent <= 85) return 'bg-amber-500';
		return 'bg-red-500';
	}
	
	function getStatusBadge(percent: number, gasto: number, orcado: number) {
		if (orcado === 0 && gasto > 0) return { text: 'Extrapolado', bg: 'bg-red-100', textc: 'text-red-700' };
		if (orcado === 0 && gasto === 0) return { text: 'No Prego', bg: 'bg-gray-100', textc: 'text-gray-700' };
		if (percent >= 100) return { text: 'Estourou Orçamento', bg: 'bg-red-100', textc: 'text-red-700' };
		if (percent >= 75) return { text: 'Atenção Orçament.', bg: 'bg-amber-100', textc: 'text-amber-700' };
		return { text: 'No Orcamento', bg: 'bg-emerald-100', textc: 'text-emerald-700' };
	}

</script>

<svelte:head>
	<title>Relatórios Analíticos</title>
</svelte:head>

<div class="flex flex-col h-full max-w-[1600px] mx-auto w-full p-6 md:p-8 space-y-8">
	
	{#if isLoading}
		<div class="flex-1 flex flex-col items-center justify-center h-96 w-full animate-pulse opacity-50">
			<Activity size={48} class="text-blue-500 mb-4" />
			<p class="text-sm font-black uppercase tracking-widest text-gray-500">Compilando Relatórios...</p>
		</div>
	{:else}
		<!-- HEADER KPIs -->
		<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6" in:fade>
			
			<div class="bg-white p-6 rounded-[2rem] border border-gray-100 shadow-xl shadow-gray-200/30 relative overflow-hidden group hover:scale-[1.02] transition-all">
				<div class="absolute -right-4 -top-4 opacity-[0.05] group-hover:scale-110 transition-transform text-blue-600">
					<TrendingUp size={120} />
				</div>
				<div class="flex flex-col gap-4 relative z-10">
					<div class="w-12 h-12 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center shadow-inner">
						<TrendingUp size={24} />
					</div>
					<div>
						<p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Total Faturado</p>
						<h3 class="text-2xl font-black text-gray-900 leading-none">{money(kpis.total_receitas)}</h3>
					</div>
				</div>
			</div>

			<div class="bg-white p-6 rounded-[2rem] border border-gray-100 shadow-xl shadow-gray-200/30 relative overflow-hidden group hover:scale-[1.02] transition-all">
				<div class="absolute -right-4 -top-4 opacity-[0.05] group-hover:scale-110 transition-transform text-emerald-600">
					<Briefcase size={120} />
				</div>
				<div class="flex flex-col gap-4 relative z-10">
					<div class="w-12 h-12 bg-emerald-50 text-emerald-600 rounded-2xl flex items-center justify-center shadow-inner">
						<Briefcase size={24} />
					</div>
					<div>
						<p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Obras Registradas</p>
						<h3 class="text-2xl font-black text-gray-900 leading-none">{portfolio.length}</h3>
					</div>
				</div>
			</div>

			<div class="bg-white p-6 rounded-[2rem] border border-gray-100 shadow-xl shadow-gray-200/30 relative overflow-hidden group hover:scale-[1.02] transition-all">
				<div class="absolute -right-4 -top-4 opacity-[0.05] group-hover:scale-110 transition-transform text-amber-600">
					<TrendingDown size={120} />
				</div>
				<div class="flex flex-col gap-4 relative z-10">
					<div class="w-12 h-12 bg-amber-50 text-amber-600 rounded-2xl flex items-center justify-center shadow-inner">
						<TrendingDown size={24} />
					</div>
					<div>
						<p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Custos Gerais</p>
						<h3 class="text-2xl font-black text-gray-900 leading-none">{money(kpis.total_despesas)}</h3>
					</div>
				</div>
			</div>
			
			<div class="bg-gray-900 p-6 rounded-[2rem] border border-gray-800 shadow-xl shadow-black/10 relative overflow-hidden group hover:scale-[1.02] transition-all">
				<div class="absolute -right-4 -top-4 opacity-[0.1] group-hover:scale-110 transition-transform text-white">
					<Target size={120} />
				</div>
				<div class="flex flex-col gap-4 relative z-10">
					<div class="w-12 h-12 bg-white/10 text-white rounded-2xl backdrop-blur-md flex items-center justify-center border border-white/10">
						<Target size={24} />
					</div>
					<div>
						<p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Saldo Retido</p>
						<h3 class="text-2xl font-black text-white leading-none">{money(kpis.saldo)}</h3>
					</div>
				</div>
			</div>

		</div>

		<!-- CHART AREA (GLASSMORPHISM) -->
		<section class="bg-white p-6 md:p-8 rounded-[2.5rem] shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-gray-100 flex flex-col h-[500px]" in:fade={{ delay: 100 }}>
			<div class="flex justify-between items-center mb-6">
				<div>
					<h2 class="text-xl font-black text-gray-900 tracking-tight">Evolução Receitas vs Despesas</h2>
					<p class="text-xs font-bold text-gray-400 tracking-wide uppercase mt-1">Acumulado Histórico Consolidado</p>
				</div>
			</div>
			<div class="flex-1 relative">
				<canvas bind:this={plCanvas}></canvas>
			</div>
		</section>

		<!-- PORTFOLIO TABLE -->
		<section class="bg-white rounded-[2.5rem] shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-gray-100 flex flex-col overflow-hidden" in:fade={{ delay: 200 }}>
			<div class="p-6 md:p-8 border-b border-gray-50 flex justify-between items-center bg-gray-50/30">
				<div>
					<h2 class="text-xl font-black text-gray-900 tracking-tight">Portfólio de Obras e Planejamento Histórico</h2>
					<p class="text-xs font-bold text-gray-400 tracking-wide uppercase mt-1">Comparativo de Budget e Progresso Custeado</p>
				</div>
			</div>
			
			<div class="overflow-x-auto">
				<table class="w-full text-left border-collapse">
					<thead>
						<tr class="bg-gray-50/50">
							<th class="py-4 px-6 text-[10px] font-black text-gray-500 uppercase tracking-widest border-b border-gray-100">Nome da Obra</th>
							<th class="py-4 px-6 text-[10px] font-black text-gray-500 uppercase tracking-widest border-b border-gray-100">Status</th>
							<th class="py-4 px-6 text-[10px] font-black text-gray-500 uppercase tracking-widest border-b border-gray-100">Custo Estimado (Budget)</th>
							<th class="py-4 px-6 text-[10px] font-black text-gray-500 uppercase tracking-widest border-b border-gray-100 w-1/4">Progresso de Verba</th>
							<th class="py-4 px-6 text-[10px] font-black text-gray-500 uppercase tracking-widest border-b border-gray-100 text-right">Despesas Totais</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-gray-50">
						{#each portfolio as obra}
							{@const pct = Number(obra.progresso_porcentagem)}
							{@const bgColor = getProgressColor(pct, Number(obra.total_gasto), Number(obra.custo_estimado))}
							{@const badge = getStatusBadge(pct, Number(obra.total_gasto), Number(obra.custo_estimado))}

							<tr class="hover:bg-blue-50/30 transition-colors group">
								<td class="py-4 px-6">
									<div class="flex items-center gap-3">
										<div class="p-2 bg-blue-100 text-blue-600 rounded-xl">
											<Building2 size={16} />
										</div>
										<div>
											<p class="text-sm font-bold text-gray-900">{obra.nome_obra}</p>
											<p class="text-xs font-semibold text-gray-400">{obra.gerente}</p>
										</div>
									</div>
								</td>
								
								<td class="py-4 px-6">
									<span class="inline-flex items-center px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-wider {badge.bg} {badge.textc}">
										{badge.text}
									</span>
								</td>

								<td class="py-4 px-6">
									<span class="text-sm font-bold text-gray-700">{money(obra.custo_estimado)}</span>
								</td>

								<td class="py-4 px-6">
									<div class="flex items-center gap-3">
										<div class="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
											<div 
												class="h-full rounded-full transition-all duration-1000 {bgColor}" 
												style="width: {pct > 100 ? 100 : pct}%"
											></div>
										</div>
										<span class="text-xs font-bold {pct > 100 ? 'text-red-500' : 'text-gray-500'} w-12 text-right">
											{pct}%
										</span>
									</div>
								</td>

								<td class="py-4 px-6 text-right">
									<span class="text-sm font-black text-gray-900">{money(obra.total_gasto)}</span>
								</td>
							</tr>
						{/each}
						
						{#if portfolio.length === 0}
							<tr>
								<td colspan="5" class="py-12 text-center text-gray-400">
									<CheckCircle2 size={40} class="mx-auto mb-4 opacity-50" />
									<p class="text-sm font-bold">Nenhuma obra localizada para montar o portfólio.</p>
								</td>
							</tr>
						{/if}
					</tbody>
				</table>
			</div>
		</section>
	{/if}
</div>
