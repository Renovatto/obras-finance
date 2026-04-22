<script lang="ts">
  import { onMount, tick } from 'svelte';
  import { fade, scale } from 'svelte/transition';
  import { api } from '$lib/api';

  // ─── Props ───────────────────────────────────────────────────
  interface Props {
    onConcluir?: () => void;
  }
  let { onConcluir }: Props = $props();

  // ─── Steps do Tour ───────────────────────────────────────────
  const steps = [
    {
      targetId: 'tour-sidebar',
      emoji: '👋',
      title: 'Bem-vindo ao ObrasFinance!',
      description: 'Este é o seu painel de controle financeiro para obras e projetos. Vou te mostrar como usar os recursos principais — leva só 1 minuto!',
      position: 'right' as const,
    },
    {
      targetId: 'tour-saldo',
      emoji: '💰',
      title: 'Saldo Atual',
      description: 'Aqui você vê o resultado financeiro geral: o total de receitas menos o total de despesas. É o "termômetro" da saúde financeira dos seus projetos.',
      position: 'bottom' as const,
    },
    {
      targetId: 'tour-receitas',
      emoji: '📈',
      title: 'Receitas',
      description: 'Este card mostra tudo que entrou de dinheiro. Clique em "Finanças" no menu para ver os detalhes de cada receita registrada.',
      position: 'bottom' as const,
    },
    {
      targetId: 'tour-filtros',
      emoji: '🔍',
      title: 'Filtros de Período e Categoria',
      description: 'Use estes filtros para visualizar os dados de um mês específico, por categoria de gasto ou por responsável. Os gráficos atualizam instantaneamente!',
      position: 'bottom' as const,
    },
    {
      targetId: 'tour-obras',
      emoji: '🏗️',
      title: 'Módulo de Obras',
      description: 'Cada obra é um projeto independente. Aqui você cadastra uma obra nova e acompanha separadamente as receitas e despesas de cada uma.',
      position: 'right' as const,
    },
    {
      targetId: 'tour-relatorios',
      emoji: '📊',
      title: 'Relatórios',
      description: 'Gere relatórios financeiros detalhados para apresentar para clientes ou para seu controle interno. Você pode filtrar por período e exportar os dados.',
      position: 'right' as const,
    },
    {
      targetId: null,
      emoji: '🎉',
      title: 'Tudo pronto!',
      description: 'Agora você já sabe o básico para usar o sistema. Para registrar uma receita ou despesa, clique no botão "+" na barra superior. Bom trabalho!',
      position: 'center' as const,
    },
  ];

  // ─── Estado ──────────────────────────────────────────────────
  let isVisible = $state(false);
  let currentStep = $state(0);
  let tooltipStyle = $state('');
  let highlightStyle = $state('');
  let tooltipPosition = $state<'top' | 'bottom' | 'left' | 'right' | 'center'>('bottom');

  const step = $derived(steps[currentStep]);
  const isLastStep = $derived(currentStep === steps.length - 1);
  const isCenter = $derived(step.position === 'center' || !step.targetId);

  // ─── Posicionamento ──────────────────────────────────────────
  async function positionTooltip() {
    if (!step.targetId) {
      tooltipStyle = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%)';
      highlightStyle = '';
      return;
    }

    const el = document.getElementById(step.targetId);
    if (!el) {
      tooltipStyle = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%)';
      highlightStyle = '';
      return;
    }

    const rect = el.getBoundingClientRect();
    const padding = 12;

    // Highlight ring ao redor do elemento
    highlightStyle = `
      position: fixed;
      top: ${rect.top - padding}px;
      left: ${rect.left - padding}px;
      width: ${rect.width + padding * 2}px;
      height: ${rect.height + padding * 2}px;
      border-radius: 20px;
      pointer-events: none;
      z-index: 9998;
    `;

    // Posiciona tooltip
    const gap = 16;
    const tooltipW = 340;

    let style = '';
    tooltipPosition = step.position;

    if (step.position === 'right') {
      style = `position:fixed;top:${rect.top + rect.height / 2 - 100}px;left:${rect.right + gap}px;width:${tooltipW}px`;
    } else if (step.position === 'left') {
      style = `position:fixed;top:${rect.top + rect.height / 2 - 100}px;right:${window.innerWidth - rect.left + gap}px;width:${tooltipW}px`;
    } else if (step.position === 'bottom') {
      const left = Math.max(12, Math.min(rect.left + rect.width / 2 - tooltipW / 2, window.innerWidth - tooltipW - 12));
      style = `position:fixed;top:${rect.bottom + gap}px;left:${left}px;width:${tooltipW}px`;
    } else {
      style = `position:fixed;top:${rect.top - 120 - gap}px;left:${Math.max(12, rect.left + rect.width / 2 - tooltipW / 2)}px;width:${tooltipW}px`;
    }

    tooltipStyle = style;
  }

  // ─── Navegação ───────────────────────────────────────────────
  async function goTo(index: number) {
    currentStep = index;
    await tick();
    await positionTooltip();
  }

  async function next() {
    if (isLastStep) {
      await finish();
    } else {
      await goTo(currentStep + 1);
    }
  }

  async function prev() {
    if (currentStep > 0) await goTo(currentStep - 1);
  }

  async function finish() {
    try {
      await api.post('/onboarding/concluir', {});
    } catch (e) {
      console.warn('Erro ao marcar onboarding:', e);
    }
    isVisible = false;
    onConcluir?.();
  }

  // ─── Inicialização ───────────────────────────────────────────
  onMount(async () => {
    await tick();
    await positionTooltip();
    // Pequeno delay para garantir que o layout foi renderizado
    setTimeout(() => {
      isVisible = true;
    }, 600);
  });

  // Reposiciona ao redimensionar
  $effect(() => {
    const handler = () => positionTooltip();
    window.addEventListener('resize', handler);
    return () => window.removeEventListener('resize', handler);
  });
</script>

<!-- Overlay escuro + hole no elemento alvo -->
{#if isVisible}
  <!-- Fundo escurecido (SVG com hole) -->
  <div
    class="tour-overlay"
    transition:fade={{ duration: 250 }}
    role="presentation"
    onclick={finish}
  >
    <!-- Camada escura -->
    <div class="tour-overlay-bg"></div>
    <!-- Anel luminoso ao redor do elemento alvo -->
    {#if step.targetId && highlightStyle}
      <div class="tour-highlight-ring" style={highlightStyle}></div>
    {/if}
  </div>

  <!-- Tooltip -->
  <div
    class="tour-tooltip"
    style={tooltipStyle}
    transition:scale={{ duration: 280, start: 0.88 }}
    role="dialog"
    aria-label="Tour de apresentação"
  >
    <!-- Seta direcional (exceto no center) -->
    {#if !isCenter}
      <div
        class="tour-arrow"
        class:tour-arrow-left={tooltipPosition === 'right'}
        class:tour-arrow-right={tooltipPosition === 'left'}
        class:tour-arrow-top={tooltipPosition === 'bottom'}
        class:tour-arrow-bottom={tooltipPosition === 'top'}
      ></div>
    {/if}

    <!-- Header -->
    <div class="tour-header">
      <span class="tour-emoji">{step.emoji}</span>
      <div class="tour-meta">
        <span class="tour-counter">{currentStep + 1} de {steps.length}</span>
        <!-- Dots de progresso -->
        <div class="tour-dots">
          {#each steps as _, i}
            <button
              class="tour-dot"
              class:tour-dot-active={i === currentStep}
              onclick={() => goTo(i)}
              aria-label="Ir para o passo {i + 1}"
            ></button>
          {/each}
        </div>
      </div>
    </div>

    <!-- Conteúdo -->
    <div class="tour-body">
      <h3 class="tour-title">{step.title}</h3>
      <p class="tour-description">{step.description}</p>
    </div>

    <!-- Ações -->
    <div class="tour-actions">
      <button class="tour-btn-skip" onclick={finish}>
        Pular tour
      </button>
      <div class="tour-nav">
        {#if currentStep > 0}
          <button class="tour-btn-prev" onclick={prev}>
            ← Anterior
          </button>
        {/if}
        <button class="tour-btn-next" onclick={next}>
          {isLastStep ? '🎉 Concluir' : 'Próximo →'}
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  /* ── Overlay ─────────────────────────────────── */
  .tour-overlay {
    position: fixed;
    inset: 0;
    z-index: 9997;
    pointer-events: all;
  }

  .tour-overlay-bg {
    position: fixed;
    inset: 0;
    background: rgba(10, 14, 30, 0.62);
    backdrop-filter: blur(2px);
  }

  .tour-highlight-ring {
    box-shadow:
      0 0 0 3px #3b82f6,
      0 0 0 6px rgba(59, 130, 246, 0.3),
      0 0 32px rgba(59, 130, 246, 0.25);
    z-index: 9998;
  }

  /* ── Tooltip ─────────────────────────────────── */
  .tour-tooltip {
    z-index: 9999;
    background: #ffffff;
    border-radius: 24px;
    box-shadow:
      0 24px 60px rgba(0, 0, 0, 0.18),
      0 4px 16px rgba(0, 0, 0, 0.08);
    padding: 24px;
    pointer-events: all;
    max-width: calc(100vw - 24px);
  }

  /* ── Seta direcional ─────────────────────────── */
  .tour-arrow {
    position: absolute;
    width: 12px;
    height: 12px;
    background: #fff;
    transform: rotate(45deg);
  }

  .tour-arrow-left {
    left: -6px;
    top: 32px;
    box-shadow: -2px 2px 6px rgba(0,0,0,0.08);
  }

  .tour-arrow-right {
    right: -6px;
    top: 32px;
    box-shadow: 2px -2px 6px rgba(0,0,0,0.08);
  }

  .tour-arrow-top {
    top: -6px;
    left: 28px;
    box-shadow: -2px -2px 6px rgba(0,0,0,0.08);
  }

  .tour-arrow-bottom {
    bottom: -6px;
    left: 28px;
    box-shadow: 2px 2px 6px rgba(0,0,0,0.08);
  }

  /* ── Header ──────────────────────────────────── */
  .tour-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
  }

  .tour-emoji {
    font-size: 28px;
    line-height: 1;
  }

  .tour-meta {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 6px;
  }

  .tour-counter {
    font-size: 10px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #94a3b8;
  }

  .tour-dots {
    display: flex;
    gap: 5px;
  }

  .tour-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #e2e8f0;
    border: none;
    cursor: pointer;
    padding: 0;
    transition: all 0.2s;
  }

  .tour-dot-active {
    background: #3b82f6;
    width: 18px;
    border-radius: 4px;
  }

  /* ── Body ────────────────────────────────────── */
  .tour-body {
    margin-bottom: 20px;
  }

  .tour-title {
    font-size: 17px;
    font-weight: 900;
    color: #0f172a;
    margin: 0 0 8px;
    letter-spacing: -0.02em;
    line-height: 1.3;
  }

  .tour-description {
    font-size: 13.5px;
    font-weight: 500;
    color: #475569;
    line-height: 1.6;
    margin: 0;
  }

  /* ── Actions ─────────────────────────────────── */
  .tour-actions {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding-top: 16px;
    border-top: 1px solid #f1f5f9;
  }

  .tour-nav {
    display: flex;
    gap: 8px;
  }

  .tour-btn-skip {
    font-size: 12px;
    font-weight: 700;
    color: #94a3b8;
    background: none;
    border: none;
    cursor: pointer;
    padding: 6px 0;
    transition: color 0.2s;
  }

  .tour-btn-skip:hover {
    color: #64748b;
  }

  .tour-btn-prev {
    font-size: 13px;
    font-weight: 700;
    color: #64748b;
    background: #f1f5f9;
    border: none;
    cursor: pointer;
    padding: 9px 16px;
    border-radius: 12px;
    transition: all 0.2s;
  }

  .tour-btn-prev:hover {
    background: #e2e8f0;
  }

  .tour-btn-next {
    font-size: 13px;
    font-weight: 800;
    color: #fff;
    background: #3b82f6;
    border: none;
    cursor: pointer;
    padding: 9px 20px;
    border-radius: 12px;
    transition: all 0.2s;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  }

  .tour-btn-next:hover {
    background: #2563eb;
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(59, 130, 246, 0.35);
  }

  .tour-btn-next:active {
    transform: translateY(0);
  }
</style>
