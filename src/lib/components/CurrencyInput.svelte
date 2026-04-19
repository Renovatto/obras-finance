<script lang="ts">
	/**
	 * CurrencyInput - Componente de input com máscara de Real Brasileiro (R$)
	 * Utiliza Runes do Svelte 5 para reatividades e formatação imediata.
	 */
	let { 
		value = $bindable(0), 
		label = "Valor", 
		id = "valor",
		placeholder = "R$ 0,00",
		class: classes = ""
	} = $props();

	// Valor formatado para exibição no input
	let displayValue = $state("");

	// Sicroniza displayValue sempre que o valor numérico mudar externamente (ex: reset da modal)
	$effect(() => {
		displayValue = formatCurrency(value);
	});

	function formatCurrency(val: number): string {
		return new Intl.NumberFormat('pt-BR', {
			style: 'currency',
			currency: 'BRL'
		}).format(val);
	}

	function handleInput(e: Event) {
		const target = e.target as HTMLInputElement;
		// Remove tudo que não é dígito
		let raw = target.value.replace(/\D/g, "");
		
		// Converte para centavos (ex: "12345" -> 123.45)
		const numericValue = Number(raw) / 100;
		
		// Atualiza o bindable value (numérico para a API)
		value = numericValue;
		
		// Atualiza a exibição visual formatted
		displayValue = formatCurrency(numericValue);
	}

	function handleFocus(e: FocusEvent) {
		// Ao focar, se estiver 0, limpa para facilitar digitação
		if (value === 0) displayValue = "";
	}

	function handleBlur() {
		// Ao sair, se estiver vazio, volta para R$ 0,00
		if (displayValue === "") displayValue = formatCurrency(0);
	}
</script>

<div class="flex flex-col space-y-1.5 w-full {classes}">
	<label for={id} class="text-sm font-bold text-gray-700 ml-1 uppercase tracking-wider opacity-70">
		{label}
	</label>
	<div class="relative group">
		<input
			{id}
			type="text"
			inputmode="numeric"
			bind:value={displayValue}
			oninput={handleInput}
			onfocus={handleFocus}
			onblur={handleBlur}
			{placeholder}
			class="w-full px-5 py-4 bg-gray-50 border-2 border-transparent rounded-2xl text-xl font-black text-gray-900 focus:bg-white focus:border-blue-600 focus:ring-4 focus:ring-blue-50 transition-all outline-none placeholder:text-gray-300 placeholder:font-bold"
		/>
		<div class="absolute right-5 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-blue-600 transition-colors pointer-events-none font-bold">
			BRL
		</div>
	</div>
</div>
