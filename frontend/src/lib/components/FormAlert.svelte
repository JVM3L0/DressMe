<script lang="ts">
	interface Props {
		message: string;
		element?: HTMLParagraphElement;
	}

	let { message, element = $bindable() }: Props = $props();
</script>

<!-- Erro do formulário inteiro (rede, limite, credenciais). A região fica
     sempre no DOM para o leitor de tela anunciar quando o texto aparecer, e
     recebe foco quando não há um campo com erro para focar. -->
<p class="form-alert" role="alert" tabindex="-1" bind:this={element}>{message}</p>

<style>
	.form-alert {
		font-weight: 600;
		color: var(--field-danger, var(--color-danger));
	}

	/* Vazia, continua na árvore de acessibilidade, mas fora do fluxo */
	.form-alert:empty {
		position: absolute;
	}
</style>
