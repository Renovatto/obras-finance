<script lang="ts">
	/**
	 * Modal.svelte - Svelte 5 Snippets Only
	 * [SSR CACHE INVALIDATION: 2026-04-13T17:55:00]
	 */
	import { fade, scale } from 'svelte/transition';
	import { X } from 'lucide-svelte';

	let { 
		isOpen = $bindable(false), 
		title, 
		subtitle, // Snippet do Svelte 5
		children, // Snippet padrão
		maxWidth = 'max-w-xl'
	} = $props();

	function close() {
		isOpen = false;
	}
</script>

{#if isOpen}
	<!-- Backdrop -->
	<div
		class="fixed inset-0 bg-gray-900/60 backdrop-blur-sm z-[100] flex items-end md:items-center justify-center p-0 md:p-4"
		transition:fade={{ duration: 200 }}
		onclick={close}
		role="button"
		tabindex="0"
		onkeydown={(e) => e.key === 'Escape' && close()}
	>
		<!-- Modal Container -->
		<div
			class="bg-white w-full {maxWidth} rounded-t-[2.5rem] md:rounded-[2.5rem] shadow-2xl flex flex-col max-h-[95vh] md:max-h-[90vh] overflow-hidden"
			transition:scale={{ start: 0.95, duration: 200, opacity: 0 }}
			onclick={(e) => e.stopPropagation()}
			role="none"
		>
			<!-- Header -->
			<div class="px-8 py-6 border-b border-gray-100 flex items-center justify-between sticky top-0 z-20 bg-white/80 backdrop-blur-md">
				<div class="flex flex-col">
					<h3 class="text-2xl font-black text-gray-900 tracking-tight">{title}</h3>
					{#if subtitle}
						{@render subtitle()}
					{/if}
				</div>
				<button
					type="button"
					onclick={close}
					class="p-2.5 hover:bg-gray-100 rounded-2xl transition-all text-gray-400 active:scale-90"
				>
					<X size={24} />
				</button>
			</div>

			<!-- Body -->
			<div class="flex-1 overflow-y-auto px-8 py-6 space-y-8 scrollbar-hide">
				{#if children}
					{@render children()}
				{/if}
			</div>
		</div>
	</div>
{/if}

<style>
	/* Custom scrollbar handling */
	.scrollbar-hide::-webkit-scrollbar {
		display: none;
	}
	.scrollbar-hide {
		-ms-overflow-style: none;
		scrollbar-width: none;
	}
</style>
