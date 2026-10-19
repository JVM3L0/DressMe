# Débito técnico

Pendências conhecidas que ficaram fora das entregas atuais. Ao resolver um item, remova-o daqui no mesmo PR, sem renumerar os demais. Ao encontrar um novo, adicione-o com o próximo ID, evidência e proposta.

Resolvidos:
- DT-01: dependências atualizadas;
- DT-02: PyJWT e `SECRET_KEY`;
- DT-03: rate limiting;
- DT-04: CI;
- DT-05: Postgres local e credenciais no `.env`;
- DT-06: enumeração de contas ([ADR-0006](adr/0006-sessao-em-cookie-e-protecao-de-contas.md));
- DT-07: política de senha;
- DT-08: grafia do username;
- DT-09: CSP.

**Prioridade:** 🔴 alta (risco de segurança ou indisponibilidade) · 🟡 média · 🟢 baixa

| ID | Prioridade | Tema | Resumo |
| --- | --- | --- | --- |
| [DT-10](#dt-10-sessões-sem-revogação) | 🟢 | Segurança | Sessões sem revogação |

---

### DT-10: Sessões sem revogação

- **Evidência:** o token da sessão é um JWT sem estado, válido por uma semana. O logout só apaga o cookie do navegador, então um token copiado antes continua válido até expirar. Não há como encerrar a sessão de um dispositivo específico.
- **Proposta:**
  - guardar no usuário uma versão de sessão (`session_version`), incluída no token e conferida no `GET /users/me` e nas rotas protegidas;
  - incrementá-la na troca de senha e em "sair de todos os dispositivos".
  - Hoje, o único jeito de invalidar tudo é trocar a `SECRET_KEY` (ADR-0006).
