# Deploy

Checklist para colocar a API em produção. A imagem é gerada pelo `backend/Dockerfile` (contexto de build: `backend/`). Ao iniciar, o container executa `alembic upgrade head` e sobe o uvicorn na porta `PORT` (padrão `8000`).

## Variáveis de ambiente

| Variável | Obrigatória | Valor em produção |
| --- | --- | --- |
| `MODE` | Sim | `production` |
| `DATABASE_URL` | Sim | URL do Postgres de produção (`postgresql+asyncpg://...`), com SSL se o banco não estiver na mesma rede privada |
| `SECRET_KEY` | Sim | Chave aleatória e exclusiva de produção (ver abaixo) |
| `FORWARDED_ALLOW_IPS` | Sim, atrás de proxy | IPs do proxy da plataforma, ou `*` (ver abaixo) |
| `PORT` | Não | Porta exigida pela plataforma, se houver |
| `RATE_LIMIT_STORAGE_URI` | Só com mais de uma instância | `redis://...` |
| `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `RATE_LIMIT_SIGNUP` | Não | Padrões: `HS256`, `15`, `5/minute` |

A API valida a configuração ao iniciar e **não sobe** se faltar `DATABASE_URL` ou `SECRET_KEY`, ou se elas forem inválidas.

### `SECRET_KEY`

Assina os tokens JWT. Se vazar, qualquer pessoa pode gerar tokens válidos.

- Gere no próprio ambiente de deploy ou na sua máquina, e cadastre direto no gerenciador de segredos da plataforma:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(48))"
  ```
- Tamanho mínimo: 32 bytes para `HS256` (48 para `HS384` e 64 para `HS512`). O comando acima gera 64 caracteres.
- Use uma chave diferente por ambiente (staging e produção). Nunca use a do `backend/settings.toml` (ambiente de testes) nem a do `.env` local.
- Trocar a chave invalida todos os tokens emitidos.

### `FORWARDED_ALLOW_IPS`

O limite de cadastros é **por IP do cliente**. Atrás de um proxy ou load balancer, a conexão chega com o IP do proxy, e o IP real vem no cabeçalho `X-Forwarded-For`. O uvicorn só usa esse cabeçalho quando a conexão vem de um IP listado em `FORWARDED_ALLOW_IPS` (padrão: apenas `127.0.0.1`).

- **Sem configurar:** todos os clientes aparecem com o IP do proxy e **compartilham o mesmo limite** (5 cadastros por minuto para o site inteiro).
- **IPs ou faixas do proxy** (ex.: `10.0.0.0/8`): a opção mais segura, quando a plataforma documenta essas faixas.
- **`*`:** aceitável **apenas** se a API não puder ser acessada diretamente, sem passar pelo proxy (caso comum em PaaS). Se ela for acessível diretamente, qualquer cliente pode forjar o `X-Forwarded-For` e burlar o limite.

Como validar depois do deploy: faça 6 cadastros seguidos de uma mesma máquina. O 6º deve receber `429`. Em seguida, um cadastro de outra rede (ex.: celular no 4G) deve ser aceito.

## Rate limiting e instâncias

Com **uma instância** e um processo do uvicorn (configuração atual do `backend/scripts/entrypoint.sh`), o contador em memória (`memory://`, padrão) é suficiente. Ele é zerado quando o container reinicia.

Com **mais de uma instância**, ou com `--workers` maior que 1, cada processo teria o próprio contador, e o limite efetivo seria multiplicado. Nesse caso:

1. Provisione um Redis acessível pela API, na mesma rede privada.
2. Defina `RATE_LIMIT_STORAGE_URI=redis://usuario:senha@host:6379/0` (ou `rediss://` com TLS).

O suporte já está instalado (`limits[redis]`), e o teste `backend/tests/integration/test_rate_limit_redis.py` valida o limite compartilhado no CI.

## Primeiro deploy

1. Provisione o Postgres e defina as variáveis acima.
2. Faça o deploy da imagem. As migrações rodam automaticamente na inicialização.
3. Verifique:
   - `GET /healthcheck/` responde `200`;
   - `POST /users/` cria um usuário (`201`);
   - o teste de rate limit da seção [`FORWARDED_ALLOW_IPS`](#forwarded_allow_ips) passa.
4. Nos logs, confirme que não aparecem valores de queries (`ECHO_SQL` desligado e parâmetros ocultos).
