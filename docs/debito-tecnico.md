# Débito técnico

Pendências conhecidas que ficaram fora das entregas atuais. Ao resolver um item, remova-o daqui no mesmo PR, sem renumerar os demais. Ao encontrar um novo, adicione-o com o próximo ID, evidência e proposta.

Resolvidos: DT-01 (dependências atualizadas), DT-02 (PyJWT e `SECRET_KEY`), DT-03 (rate limiting), DT-04 (CI), DT-05 (Postgres local e credenciais no `.env`) e DT-08 (grafia do username).

**Prioridade:** 🔴 alta (risco de segurança ou indisponibilidade) · 🟡 média · 🟢 baixa

| ID | Prioridade | Tema | Resumo |
| --- | --- | --- | --- |
| [DT-06](#dt-06-enumeração-de-contas-no-cadastro) | 🟡 | Produto / Segurança | Enumeração de contas no cadastro |
| [DT-07](#dt-07-política-de-senha-mínima) | 🟢 | Segurança | Política de senha mínima |
| [DT-09](#dt-09-sem-content-security-policy) | 🟡 | Segurança | Sem Content Security Policy |

---

### DT-06: Enumeração de contas no cadastro

- **Evidência:** e-mail já cadastrado retorna `409` em cerca de 2 ms; e-mail novo retorna `201` em cerca de 190 ms. Pela resposta ou pelo tempo, é possível descobrir quem tem conta.
- **Proposta:** é uma decisão de produto.
  - Já mitigado pelo rate limiting de cadastro (5/min por IP).
  - Para eliminar o problema: confirmação por e-mail, com resposta idêntica (`202`) nos dois casos.

### DT-07: Política de senha mínima

- **Evidência:** a única regra é ter de 8 caracteres a 72 bytes. Senhas como `12345678` são aceitas.
- **Proposta:** recusar senhas comuns ou vazadas, como recomenda o NIST SP 800-63B, por exemplo com uma lista local ou com a API k-anonymity do Have I Been Pwned. Evitar regras de composição ("1 maiúscula, 1 símbolo").

### DT-09: Sem Content Security Policy

- **Evidência:** o nginx (`frontend/nginx/`) envia `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` e `Permissions-Policy`, mas nenhuma `Content-Security-Policy`. As páginas pré-renderizadas do SvelteKit têm um script inline de inicialização, então uma CSP simples (`script-src 'self'`) quebraria o site.
- **Proposta:** ativar a CSP do próprio SvelteKit no modo `hash`, que calcula o hash dos scripts inline no build e o inclui na política. Começar com `default-src 'self'`, mais `img-src 'self' blob: data:` para os previews de foto. Validar com testes de ponta a ponta e, antes de aplicar, publicar em modo `Content-Security-Policy-Report-Only`.

