# Changelog

As mudanças de cada versão do VirtualFit ficam registradas aqui. O formato segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), e as versões seguem o [Versionamento Semântico](https://semver.org/lang/pt-BR/) (veja o [ADR-0005](docs/adr/0005-versionamento-semantico-por-branch.md)).

## [0.5.0] - 2026-10-20

### Adicionado

- Provador (`/provador`) e conjuntos de peças ([ADR-0008](docs/adr/0008-conjuntos-e-ponte-para-ia-externa.md)):
  - a foto ao lado de um mapa do corpo, com um quadradinho para cada categoria na posição em que a peça é vestida (acessório na cabeça, agasalho e parte de cima no tronco, parte de baixo nas pernas, calçado nos pés); os acessórios (até 4) ficam numa fileira de quadradinhos pequenos no alto; a peça única fica na vertical, ocupando a altura do tronco e das pernas, e o app avisa o que sairá do conjunto antes de trocar;
  - conjuntos salvos com nome (API `POST`/`GET /outfits/`, `PUT` e `DELETE /outfits/{id}`): usar, atualizar, salvar como novo e excluir. Excluir um conjunto não exclui as peças, e excluir uma peça a tira dos conjuntos;
  - o backend confere a composição: peças do usuário e sem repetir, uma por categoria (até 4 acessórios), e peça única sem parte de cima ou de baixo.
- Levar o conjunto para uma IA de imagens, sem o VirtualFit enviar nada a ninguém:
  - a imagem das roupas é montada no navegador, numa grade de quadradinhos em ordem do corpo (até 8 peças);
  - copiar a foto e copiar a imagem das roupas (PNG) para a área de transferência, e baixar as duas imagens (em contexto seguro; em HTTP só o download);
  - texto em inglês gerado por regras a partir das peças (categoria e nome), com a opção de manter o fundo e um pedido extra, para copiar e colar na IA;
  - "Compartilhar tudo" (foto, roupas e texto) em aparelhos que suportam.
- Link "Provador" no cabeçalho.
- Menu para celular (DT-14): quem está logado ganha uma barra de navegação fixa embaixo da tela, com ícone e rótulo para Fotos, Guarda-roupa, Provador e Sua conta, alvos de toque grandes, o destino atual marcado e respeito à área segura do aparelho. O cabeçalho fica só com o logo e o botão de tema. No computador, o menu continua no cabeçalho.
- O teste de ponta a ponta cobre o provador, com a área de transferência de verdade.

### Corrigido

- Um registro de imagem sem o arquivo no disco (arquivo apagado, disco restaurado pela metade) passa a responder `404`, e não um erro `500`; o provador explica que a peça (ou foto) deve ser excluída e enviada de novo.

### Corrigido

- Gerenciador de senhas: o e-mail passa a ser o login que ele guarda e preenche (`autocomplete="username"` no cadastro e no login), e o nome de usuário vira só o apelido (`nickname`). Antes, ele poderia salvar o nome de usuário como login, e o preenchimento no login usaria um valor que não entra.

### Alterado

- O item "prova virtual manual com arrastar, redimensionar e girar" do ADR-0001 foi substituído pelo ADR-0008.
- A etapa "Monte o conjunto" substitui "Prove sem trocar de roupa" na página inicial.

## [0.4.0] - 2026-10-20

### Adicionado

- Fotos do usuário e guarda-roupa ([ADR-0007](docs/adr/0007-categorias-de-pecas-e-entrega-das-imagens.md)):
  - API: `POST` e `GET /photos/`, `GET /photos/{id}/image` e `DELETE /photos/{id}`, e as mesmas rotas em `/garments/`, com o filtro `?category=`;
  - telas `/fotos` e `/guarda-roupa`, com pré-visualização antes do envio, filtro por categoria com contagem, e confirmação antes de excluir;
  - seis categorias de peça, pela região do corpo: parte de cima, agasalho, parte de baixo, peça única, calçado e acessório;
  - links "Fotos", "Guarda-roupa" e "Sua conta" no cabeçalho, para quem está logado.
- Armazenamento das imagens em disco, num volume `media` do compose. O nginx entrega os arquivos (`X-Accel-Redirect`) depois que a API confere a sessão e o dono, e o endereço `/_media/` não abre direto ([ADR-0003](docs/adr/0003-armazenamento-local-de-imagens-com-nginx.md)).
- Variáveis `MEDIA_ROOT`, `MEDIA_ACCEL_REDIRECT` e `RATE_LIMIT_UPLOAD`.
- Miniaturas (DT-12): cada envio gera o original, reduzido a 2.048 px no lado maior, e uma miniatura de 480 px (`GET .../{id}/thumbnail`). As grades usam a miniatura, e a imagem inteira fica para o provador.
- Teste de ponta a ponta (DT-13): `npm run e2e` roda o fluxo principal num navegador real, contra o ambiente completo (cadastro, login, envio, EXIF removido, imagem privada, exclusão e saída), e o workflow `e2e.yml` o executa no CI. Falha com qualquer erro de console, de CSP ou de rede inesperado.
- Débito técnico DT-11 (arquivos órfãos ao apagar contas).

### Alterado

- O limite de corpo no nginx passa de 10 MB para 11 MB (a imagem pode ter 10 MB, e o corpo leva também os campos do formulário).
- A tela da conta usa o mesmo componente de proteção das novas telas (`RequireSession`).

### Segurança

- Todo envio é validado e regravado: o tipo vem do conteúdo (JPEG ou PNG), e não da extensão; o nome do arquivo é gerado pelo servidor; imagens com mais de 60 megapixels são recusadas; e os metadados EXIF, incluindo a localização GPS, são removidos. A rotação da foto é aplicada antes de descartá-los.
- A imagem de outro usuário se comporta como se não existisse (`404`), e as imagens têm `Cache-Control: private`.

### Corrigido

- O nome acessível do botão "Excluir" saía sem espaço ("ExcluirCamisa azul"), por causa de como o Svelte trata espaços no começo de um elemento.

## [0.3.0] - 2026-10-19

### Adicionado

- Login com sessão de uma semana ([ADR-0006](docs/adr/0006-sessao-em-cookie-e-protecao-de-contas.md)):
  - `POST /auth/login`, `POST /auth/logout` e `GET /users/me`;
  - o token fica num cookie `HttpOnly` e `SameSite=Strict` (e `Secure` em produção), que o JavaScript da página não lê;
  - limite de 10 tentativas de login por minuto por IP (`RATE_LIMIT_LOGIN`).
- Telas de login (`/entrar`) e da conta (`/conta`), com saída da conta. O cabeçalho mostra "Entrar" ou "Sua conta", conforme a sessão.
- Política de senha (DT-07), como no NIST SP 800-63B:
  - recusa as senhas mais usadas em vazamentos (lista do NCSC) e senhas que contêm o username ou o e-mail;
  - sem regras de composição;
  - o frontend antecipa a regra de dados pessoais e traduz os erros da API.
- Content Security Policy nas páginas (DT-09): só recursos da própria origem e nenhum script inline sem hash. O script de tema virou um arquivo (`static/theme-init.js`).
- Variável `WEB_HOST` no compose e instruções para testar no celular pela rede local.

### Alterado

- A sessão passa de 15 minutos para uma semana (`ACCESS_TOKEN_EXPIRE_MINUTES=10080`).
- Nos formulários, a dica e o erro de cada campo ocupam o mesmo espaço. Antes, o erro que aparecia ao sair do campo mudava a altura do formulário, e o clique no botão de enviar podia se perder.

### Segurança

- O login não revela se um e-mail tem conta: a resposta e o tempo são iguais para e-mail inexistente e senha errada (DT-06).
- O cadastro calcula o hash da senha antes de checar duplicidade, então o tempo de resposta também não revela contas (DT-06). O `409` continua, com risco aceito no ADR-0006.

### Removido

- Capturas de tela de testes que falharam, commitadas por engano, agora ignoradas pelo Git.

## [0.2.0] - 2026-10-19

### Adicionado

- Frontend em SvelteKit (`frontend/`), mobile-first, com identidade visual própria: paleta Gruvbox, títulos em Bodoni Moda e a etiqueta de roupa como elemento de destaque.
- Página inicial explicando o fluxo do produto e página de cadastro, com validação no navegador, mensagens de erro em português, foco no primeiro erro e opção de mostrar a senha.
- Botão para alternar entre os temas claro e escuro. O padrão segue o sistema, a escolha fica salva no navegador e é aplicada antes da primeira pintura, sem piscar.
- Link para o código no GitHub no rodapé.
- Cliente HTTP tipado (`openapi-fetch`), com os tipos gerados a partir do OpenAPI do backend (`npm run api:sync`).
- A API informa a própria versão no OpenAPI (`/docs`) e no `GET /healthcheck/`.
- Workflow de CI do frontend: lint, checagem de tipos, build, testes (unidade e componentes no Chromium), auditoria, verificação do contrato da API e build da imagem.
- Serviço `web` no `docker compose`, com o nginx servindo o frontend e repassando `/api` para a API. É a entrada única em <http://localhost:8080>, com cabeçalhos de segurança, cache de arquivos estáticos e gzip.

### Alterado

- A versão do produto passa a ser única para o monorepo (`backend/pyproject.toml` e `frontend/package.json`).
- No compose, a API deixa de ser publicada no host e ganha um healthcheck. Ela confia no `X-Forwarded-For` definido pelo nginx, então o rate limiting usa o IP real do cliente e não aceita IP forjado. A documentação fica em `/api/docs`.

## [0.1.0] - 2026-10-19

Primeira versão da API, consolidando o trabalho até a reorganização em monorepo.

### Adicionado

- Cadastro de usuários (`POST /users/`):
  - senha com hash bcrypt, calculado fora do event loop;
  - e-mail e username únicos sem diferenciar maiúsculas, e o username preserva a grafia;
  - limite de 5 cadastros por minuto por IP.
- Serviço de tokens JWT (PyJWT) e configuração obrigatória de `SECRET_KEY`.
- Testes unitários e de integração com Postgres, incluindo as migrações.
- CI com Ruff, testes, `pip-audit` e build da imagem Docker.
- Documentação de deploy, débito técnico e decisões (ADRs 0001 a 0003).

### Segurança

- Valores das queries ocultos nos logs, e erros 422 sem ecoar a entrada (para não expor senhas).
- Postgres e API acessíveis apenas por `127.0.0.1` no compose, e credenciais no `.env`.

[0.5.0]: https://github.com/JVM3L0/DressMe/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/JVM3L0/DressMe/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/JVM3L0/DressMe/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/JVM3L0/DressMe/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/JVM3L0/DressMe/releases/tag/v0.1.0
