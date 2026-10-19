# ADR-0006: Sessão em cookie, de uma semana, e proteção das contas

- **Status:** Aceito
- **Data:** 2026-10-19
- **Substitui em parte:** [ADR-0001](0001-escopo-prova-de-conceito.md), item 4 ("Login"). O resto do ADR-0001 continua valendo.

## Contexto

A PoC ganha login. O ADR-0001 previa um token de 24 h, mas a PoC é usada para testes esporádicos (inclusive no celular), e entrar todo dia atrapalha mais do que protege. Ao mesmo tempo, ficavam abertos dois débitos ligados a contas:

- **DT-06:** o cadastro revelava, pela resposta e pelo tempo, se um e-mail já tinha conta;
- **DT-07:** a única regra de senha era o tamanho, e `12345678` era aceita.

O frontend é estático e fica na mesma origem que a API, em `/api` ([ADR-0004](0004-frontend-estatico-com-api-em-api.md)).

## Decisão

1. **Sessão de uma semana** (`ACCESS_TOKEN_EXPIRE_MINUTES=10080`), com um único JWT e sem refresh token.
2. **O token fica num cookie, não no `localStorage`:** `virtualfit_session`, com `HttpOnly`, `SameSite=Strict`, `Path=/` e `Secure` fora de `development` e `testing`.
   - `HttpOnly` impede que um XSS leia o token. Com uma semana de validade, um token roubado valeria muito.
   - `SameSite=Strict` e a mesma origem bastam contra CSRF: outro site não consegue enviar requisições com o cookie, e não há CORS liberado.
   - A API não aceita `Authorization: Bearer`. Há um único caminho de autenticação para testar e proteger.
3. **Logout sem revogação:** o `POST /auth/logout` apaga o cookie, mas o token continua válido até expirar. Para encerrar todas as sessões, troque a `SECRET_KEY`. Uma lista de revogação (ou uma versão de sessão no usuário) fica para quando houver "sair de todos os dispositivos" ou troca de senha.
4. **Login sem enumeração de contas:**
   - a mesma resposta (`401`, "E-mail ou senha incorretos.") para e-mail inexistente e para senha errada;
   - com e-mail inexistente, a senha é verificada contra um hash fictício do mesmo custo, então o tempo é igual;
   - limite de 10 tentativas por minuto por IP (`RATE_LIMIT_LOGIN`), separado do limite de cadastro.
5. **Cadastro (DT-06):** o hash da senha é calculado antes da checagem de duplicidade, então o `409` leva o mesmo tempo que o `201`. O `409` continua existindo: eliminá-lo exigiria confirmação por e-mail, que o ADR-0001 adia. O risco que sobra (descobrir se um e-mail tem conta, a 5 tentativas por minuto por IP) é aceito na PoC.
6. **Política de senha (DT-07)**, como no NIST SP 800-63B:
   - recusa as senhas de 8+ caracteres da lista das 100 mil mais usadas em vazamentos do NCSC (cerca de 46 mil, comparadas em minúsculas), guardada em `backend/domain/data/`, sem chamada a serviços externos;
   - recusa senhas que contêm o username ou a parte local do e-mail (trechos de 4+ caracteres);
   - sem regras de composição;
   - o mínimo continua em 8 caracteres. A revisão 4 da norma pede 15 quando a senha é o único fator; reavaliar ao sair da PoC.
   - Os erros têm tipos próprios (`password_common`, `password_personal`), que o frontend traduz.

## Consequências

- Em produção, o site precisa de HTTPS antes do primeiro login, ou o navegador descarta o cookie ([docs/deploy.md](../deploy.md)).
- Na rede local (celular), o login funciona por HTTP porque o compose roda em `development`.
- A lista de senhas só existe no backend: o frontend antecipa as regras de tamanho e de dados pessoais, e a de senha comum chega como erro `422`.
- Uma sessão roubada vale até uma semana, sem revogação individual. É aceitável enquanto a PoC não guarda dados sensíveis além das fotos.
- Ao sair da PoC, revisar: confirmação por e-mail (elimina o `409`), revogação de sessões e o mínimo de 15 caracteres.
