/**
 * UI State Store - Using Svelte 5 Runes
 * Controls global UI elements like the Launch Modal.
 */

class UIState {
	// Modal Lançamento
	#isLaunchModalOpen = $state(false);
	#modalData = $state<any>(null);
	#refreshTrigger = $state(0);

	get isLaunchModalOpen() {
		return this.#isLaunchModalOpen;
	}

	set isLaunchModalOpen(val: boolean) {
		this.#isLaunchModalOpen = val;
		if (!val) {
			// Se estiver fechando, limpamos os dados após a transição
			setTimeout(() => {
				this.#modalData = null;
			}, 300);
		}
	}

	get modalData() {
		return this.#modalData;
	}

	openLaunchModal(data: any = null) {
		this.#modalData = data;
		this.#isLaunchModalOpen = true;
	}

	closeLaunchModal() {
		this.#isLaunchModalOpen = false;
		// Pequeno delay para não resetar visualmente antes da transição de fechar acabar
		setTimeout(() => {
			this.#modalData = null;
		}, 300);
	}

	get refreshTrigger() {
		return this.#refreshTrigger;
	}

	triggerRefresh() {
		this.#refreshTrigger++;
	}
}

export const ui = new UIState();
