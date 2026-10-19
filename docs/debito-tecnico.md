# Débito técnico

Pendências conhecidas que ficaram fora das entregas atuais. Ao resolver um item, remova-o daqui no mesmo PR, sem renumerar os demais. Ao encontrar um novo, adicione-o com o próximo ID, evidência e proposta.

Resolvidos: DT-01 (dependências atualizadas), DT-04 (CI), DT-05 (Postgres local e credenciais no `.env`) e DT-08 (grafia do username).

**Prioridade:** 🔴 alta (risco de segurança ou indisponibilidade) · 🟡 média · 🟢 baixa

| ID | Prioridade | Tema | Resumo |
| --- | --- | --- | --- |
| [DT-02](#dt-02-python-jose-sem-correção-disponível) | 🔴 | Segurança | `python-jose` / `ecdsa` sem correção disponível |
| [DT-03](#dt-03-sem-rate-limiting-no-cadastro) | 🔴 | Segurança | Sem rate limiting no cadastro |
| [DT-06](#dt-06-enumeração-de-contas-no-cadastro) | 🟡 | Produto / Segurança | Enumeração de contas no cadastro |
| [DT-07](#dt-07-política-de-senha-mínima) | 🟢 | Segurança | Política de senha mínima |

---

### DT-02: `python-jose` sem correção disponível

- **Evidência:** `pip-audit` aponta vulnerabilidades no `python-jose` e na sua dependência `ecdsa` sem versão corrigida. A documentação do FastAPI passou a recomendar o `PyJWT`.
- **Proposta:** trocar por `PyJWT` em `infrastructure/auth/jwt_service.py` antes de implementar o login. Hoje o `JWTService` não é usado por nenhuma rota, então a troca é barata.
- **Junto com isso:** criar a configuração `SECRET_KEY` obrigatória (sem default) em `config/`.
- **Ao resolver:** remover do job `audit` em `.github/workflows/ci.yml` os `--ignore-vuln PYSEC-2026-4298` (`python-jose`) e `PYSEC-2026-1325` (`ecdsa`).

### DT-03: Sem rate limiting no cadastro

- **Evidência:** cada `POST /users/` consome cerca de 190 ms de CPU com o bcrypt (custo 12). Não há limite por cliente, o que permite esgotar a CPU com muitas requisições e criar contas em massa.
- **Proposta:** limitar por IP no proxy ou na plataforma de deploy, ou na aplicação com `slowapi`. Aplicar também ao futuro endpoint de login.

### DT-06: Enumeração de contas no cadastro

- **Evidência:** e-mail já cadastrado retorna `409` em cerca de 2 ms; e-mail novo retorna `201` em cerca de 190 ms. Pela resposta ou pelo tempo, é possível descobrir quem tem conta.
- **Proposta:** é uma decisão de produto.
  - O mínimo é o rate limiting ([DT-03](#dt-03-sem-rate-limiting-no-cadastro)).
  - Para eliminar o problema: confirmação por e-mail, com resposta idêntica (`202`) nos dois casos.

### DT-07: Política de senha mínima

- **Evidência:** a única regra é ter de 8 caracteres a 72 bytes. Senhas como `12345678` são aceitas.
- **Proposta:** recusar senhas comuns ou vazadas, como recomenda o NIST SP 800-63B, por exemplo com uma lista local ou com a API k-anonymity do Have I Been Pwned. Evitar regras de composição ("1 maiúscula, 1 símbolo").
