# Débito técnico

Pendências conhecidas que ficaram fora das entregas atuais. Ao resolver um item, remova-o daqui no mesmo PR, sem renumerar os demais. Ao encontrar um novo, adicione-o com o próximo ID, evidência e proposta.

Resolvidos: DT-01 (dependências atualizadas), DT-02 (PyJWT e `SECRET_KEY`), DT-03 (rate limiting), DT-04 (CI), DT-05 (Postgres local e credenciais no `.env`) e DT-08 (grafia do username).

**Prioridade:** 🔴 alta (risco de segurança ou indisponibilidade) · 🟡 média · 🟢 baixa

| ID | Prioridade | Tema | Resumo |
| --- | --- | --- | --- |
| [DT-06](#dt-06-enumeração-de-contas-no-cadastro) | 🟡 | Produto / Segurança | Enumeração de contas no cadastro |
| [DT-07](#dt-07-política-de-senha-mínima) | 🟢 | Segurança | Política de senha mínima |

---

### DT-06: Enumeração de contas no cadastro

- **Evidência:** e-mail já cadastrado retorna `409` em cerca de 2 ms; e-mail novo retorna `201` em cerca de 190 ms. Pela resposta ou pelo tempo, é possível descobrir quem tem conta.
- **Proposta:** é uma decisão de produto.
  - Já mitigado pelo rate limiting de cadastro (5/min por IP).
  - Para eliminar o problema: confirmação por e-mail, com resposta idêntica (`202`) nos dois casos.

### DT-07: Política de senha mínima

- **Evidência:** a única regra é ter de 8 caracteres a 72 bytes. Senhas como `12345678` são aceitas.
- **Proposta:** recusar senhas comuns ou vazadas, como recomenda o NIST SP 800-63B, por exemplo com uma lista local ou com a API k-anonymity do Have I Been Pwned. Evitar regras de composição ("1 maiúscula, 1 símbolo").
