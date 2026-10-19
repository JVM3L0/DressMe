# ADR-0003: Imagens em disco local, servidas pelo nginx

- **Status:** Aceito
- **Data:** 2026-10-19

## Contexto

A prova de conceito ([ADR-0001](0001-escopo-prova-de-conceito.md)) precisa guardar fotos dos usuários e das roupas. As fotos do usuário mostram o **corpo da pessoa**: são dados pessoais sensíveis no contexto da LGPD (RNF08). A PoC roda numa única máquina, sem orçamento para serviços externos.

## Decisão

1. **Sem S3 na PoC.** As imagens ficam em disco, num volume Docker (`media`) fora dos containers, para sobreviver a rebuilds.
2. **O nginx é a porta de entrada** e serve os arquivos:
   ```
   nginx (porta 80)
   ├── /         → frontend (SvelteKit)
   ├── /api/     → FastAPI
   └── /media/   → internal: acessível só via X-Accel-Redirect
   volume "media" → montado no nginx (leitura) e na API (escrita)
   ```
3. **Nenhuma imagem é pública.** O front pede a imagem à API (ex.: `GET /api/photos/{id}`). A API confere o token e se a imagem pertence ao usuário, e responde apenas com o cabeçalho `X-Accel-Redirect`, que manda o nginx entregar o arquivo da pasta `internal`. Assim, o controle de acesso fica no backend e a entrega do arquivo no nginx, sem passar os bytes pelo Python.
4. **Todo upload é validado e reprocessado:**
   - limite de 10 MB no nginx (`client_max_body_size`) e na API (RF04);
   - a imagem é aberta com Pillow, para confirmar que é JPG ou PNG pelo conteúdo e não pela extensão;
   - a imagem é salva como uma nova cópia, **sem metadados EXIF**, que costumam trazer a localização GPS de onde a foto foi tirada;
   - o arquivo recebe um nome gerado (`<uuid>.<ext>`), nunca o nome enviado pelo usuário.
5. **O armazenamento fica atrás de uma interface.** Um protocolo `ImageStorage` em `domain/ports/` (`save`, `delete`, `path`), com a implementação `LocalImageStorage` em `infrastructure/`, no mesmo padrão do `PasswordHasher`. Trocar por S3 depois significa trocar só a implementação.

## Consequências

- Sem custo de storage externo, e com entrega eficiente pelo nginx.
- **Limitações aceitas para a PoC:**
  - armazenamento numa única máquina, que pode encher o disco;
  - backup manual do volume;
  - não funciona com várias instâncias da API sem um disco compartilhado.
- Ao sair da PoC (mais de uma instância, CDN, RNF06), substituir por um storage de objetos compatível com S3, com URLs assinadas, num novo ADR.
- A exclusão de uma peça ou de uma conta precisa remover também os arquivos do disco (RF06 e RF13).
