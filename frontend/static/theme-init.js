// Aplica o tema escolhido antes da primeira pintura, para não piscar o tema
// errado. Carregado de forma bloqueante no <head> (src/app.html); é um arquivo,
// e não um script inline, para ser permitido pela CSP (script-src 'self').
// Mantenha em sincronia com src/lib/theme.ts.
(() => {
	let saved = null;
	try {
		saved = localStorage.getItem('theme');
	} catch {
		// Armazenamento indisponível: segue o tema do sistema
	}
	if (saved === 'light' || saved === 'dark') {
		document.documentElement.dataset.theme = saved;
	}
	const dark =
		saved === 'dark' ||
		(saved !== 'light' && matchMedia('(prefers-color-scheme: dark)').matches);
	document
		.querySelector('meta[name="theme-color"]')
		.setAttribute('content', dark ? '#1d2021' : '#f9f5d7');
})();
