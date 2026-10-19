# Débito técnico

Pendências conhecidas que ficaram fora das entregas atuais. Ao resolver um item, remova-o daqui no mesmo PR. Ao encontrar um novo, adicione-o com evidência e proposta.

**Prioridade:** 🔴 alta (risco de segurança ou indisponibilidade) · 🟡 média · 🟢 baixa

| ID | Prioridade | Tema | Resumo |
| --- | --- | --- | --- |
| [DT-01](#dt-01-dependências-com-vulnerabilidades-conhecidas) | 🔴 | Segurança | Dependências com vulnerabilidades conhecidas |
| [DT-02](#dt-02-python-jose-sem-correção-disponível) | 🔴 | Segurança | `python-jose` / `ecdsa` sem correção disponível |
| [DT-03](#dt-03-sem-rate-limiting-no-cadastro) | 🔴 | Segurança | Sem rate limiting no cadastro |
| [DT-04](#dt-04-sem-pipeline-de-ci) | 🟡 | Qualidade | Sem pipeline de CI |
| [DT-05](#dt-05-postgres-exposto-e-credenciais-no-compose) | 🟡 | Segurança | Postgres exposto e credenciais fixas no compose |
| [DT-06](#dt-06-enumeração-de-contas-no-cadastro) | 🟡 | Produto / Segurança | Enumeração de contas no cadastro |
| [DT-07](#dt-07-política-de-senha-mínima) | 🟢 | Segurança | Política de senha mínima |
| [DT-08](#dt-08-username-perde-a-grafia-original) | 🟢 | Produto | Username perde a grafia original |

---

### DT-01: Dependências com vulnerabilidades conhecidas

- **Evidência:** `pip-audit` (19/10/2026) aponta vulnerabilidades em `starlette`, `python-multipart`, `cryptography`, `urllib3`, `idna`, `dynaconf`, `python-dotenv`, `mako`, `pyasn1`, `pygments`, `anyio` e `pydantic-settings`.
- **Proposta:** `uv lock --upgrade`, rodar os testes e conferir breaking changes (o `starlette` muda de major, então o `fastapi` precisa acompanhar).
- **Como verificar:**
  ```bash
  uv export --frozen --no-hashes > /tmp/req.txt
  uvx pip-audit -r /tmp/req.txt --no-deps --disable-pip
  ```

### DT-02: `python-jose` sem correção disponível

- **Evidência:** `pip-audit` aponta vulnerabilidades no `python-jose` e na sua dependência `ecdsa` sem versão corrigida. A documentação do FastAPI passou a recomendar o `PyJWT`.
- **Proposta:** trocar por `PyJWT` em `infrastructure/auth/jwt_service.py` antes de implementar o login. Hoje o `JWTService` não é usado por nenhuma rota, então a troca é barata.
- **Junto com isso:** criar a configuração `SECRET_KEY` obrigatória (sem default) em `config/`.

### DT-03: Sem rate limiting no cadastro

- **Evidência:** cada `POST /users/` consome cerca de 190 ms de CPU com o bcrypt (custo 12). Não há limite por cliente, o que permite esgotar a CPU com muitas requisições e criar contas em massa.
- **Proposta:** limitar por IP no proxy ou na plataforma de deploy, ou na aplicação com `slowapi`. Aplicar também ao futuro endpoint de login.

### DT-04: Sem pipeline de CI

- **Evidência:** não existe `.github/workflows/`. Ruff, testes e auditoria rodam apenas localmente ou via pre-commit.
- **Proposta:** workflow no GitHub Actions com um service container `postgres:16` rodando:
  - `ruff check` e `ruff format --check`;
  - `pytest`, com `TEST_DATABASE_URL` apontando para o service, para os testes de integração não serem pulados;
  - `pip-audit`.

### DT-05: Postgres exposto e credenciais fixas no compose

- **Evidência:** `docker-compose.yml` publica `5432` em `0.0.0.0` (acessível pela rede) e define usuário e senha no próprio arquivo.
- **Proposta:**
  - publicar como `127.0.0.1:5432:5432`;
  - ler as credenciais de variáveis de ambiente ou `.env`;
  - em produção, garantir conexão com SSL e credenciais exclusivas.

### DT-06: Enumeração de contas no cadastro

- **Evidência:** e-mail já cadastrado retorna `409` em cerca de 2 ms; e-mail novo retorna `201` em cerca de 190 ms. Pela resposta ou pelo tempo, é possível descobrir quem tem conta.
- **Proposta:** é uma decisão de produto.
  - O mínimo é o rate limiting ([DT-03](#dt-03-sem-rate-limiting-no-cadastro)).
  - Para eliminar o problema: confirmação por e-mail, com resposta idêntica (`202`) nos dois casos.

### DT-07: Política de senha mínima

- **Evidência:** a única regra é ter de 8 caracteres a 72 bytes. Senhas como `12345678` são aceitas.
- **Proposta:** recusar senhas comuns ou vazadas, como recomenda o NIST SP 800-63B, por exemplo com uma lista local ou com a API k-anonymity do Have I Been Pwned. Evitar regras de composição ("1 maiúscula, 1 símbolo").

### DT-08: Username perde a grafia original

- **Evidência:** para ser único sem diferenciar maiúsculas, o username é salvo em minúsculas (`JoaoSilva` vira `joaosilva`). Hoje só são aceitos caracteres ASCII (`a-z`, `0-9`, `_`, `.`, `-`).
- **Proposta:** se a grafia original for necessária para exibição, guardar o username como digitado e garantir a unicidade com um índice único em `lower(username)`, no lugar da constraint `ck_users_username_lowercase`.
