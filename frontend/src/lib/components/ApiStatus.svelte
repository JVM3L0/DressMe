<script lang="ts">
	import { api } from '#lib/api/client.ts';

	type Status = { kind: 'checking' } | { kind: 'online'; version: string } | { kind: 'offline' };

	let status: Status = $state({ kind: 'checking' });

	async function check() {
		try {
			const { data } = await api.GET('/healthcheck/');
			status = data ? { kind: 'online', version: data.version } : { kind: 'offline' };
		} catch {
			status = { kind: 'offline' };
		}
	}

	$effect(() => {
		check();
	});
</script>

<p class="status" data-status={status.kind} role="status">
	<span class="dot" aria-hidden="true"></span>
	{#if status.kind === 'checking'}
		Verificando a API…
	{:else if status.kind === 'online'}
		API {status.version} conectada
	{:else}
		API indisponível. Inicie o backend e recarregue a página.
	{/if}
</p>

<style>
	.status {
		display: inline-flex;
		align-items: center;
		gap: var(--space-2);
		font-size: var(--text-sm);
		color: var(--color-text-muted);
	}

	.dot {
		width: 0.5rem;
		height: 0.5rem;
		border-radius: 50%;
		background: var(--color-border);
	}

	[data-status='online'] .dot {
		background: var(--color-success);
	}

	[data-status='offline'] .dot {
		background: var(--color-danger);
	}
</style>
