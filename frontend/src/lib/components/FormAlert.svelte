<script lang="ts">
	interface Props {
		message: string;
		/** `success` é um aviso educado (`role="status"`); `error` interrompe a leitura */
		kind?: 'error' | 'success';
		element?: HTMLParagraphElement;
	}

	let { message, kind = 'error', element = $bindable() }: Props = $props();
</script>

<!-- Aviso do formulário inteiro (rede, limite, credenciais, confirmação). A
     região fica sempre no DOM para o leitor de tela anunciar quando o texto
     aparecer, e recebe foco quando não há um campo com erro para focar. -->
<p
	class="form-alert"
	class:success={kind === 'success'}
	role={kind === 'error' ? 'alert' : 'status'}
	tabindex="-1"
	bind:this={element}
>
	{message}
</p>

<style>
	.form-alert {
		font-weight: 600;
		color: var(--field-danger, var(--color-danger));
	}

	.form-alert.success {
		color: var(--field-text, var(--color-text));
	}

	/* Vazia, continua na árvore de acessibilidade, mas fora do fluxo */
	.form-alert:empty {
		position: absolute;
	}
</style>
