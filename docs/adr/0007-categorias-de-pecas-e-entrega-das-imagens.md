# ADR-0007: Categorias de peças e entrega das imagens

- **Status:** Aceito
- **Data:** 2026-10-20

## Contexto

O guarda-roupa da PoC ([ADR-0001](0001-escopo-prova-de-conceito.md)) pede "categoria manual" para cada peça, e as imagens ficam em disco, atrás do nginx ([ADR-0003](0003-armazenamento-local-de-imagens-com-nginx.md)). Faltava decidir quais são as categorias e como o navegador recebe as imagens, que não são públicas.

## Decisão

1. **Seis categorias, pela região do corpo**, em vez de por tipo de peça, ocasião ou estação:

   | Valor | Nome | Exemplos |
   | --- | --- | --- |
   | `top` | Parte de cima | camiseta, camisa, blusa, suéter |
   | `outerwear` | Agasalho | jaqueta, casaco, blazer, cardigã |
   | `bottom` | Parte de baixo | calça, short, saia |
   | `one_piece` | Peça única | vestido, macacão |
   | `footwear` | Calçado | tênis, sapato, sandália, bota |
   | `accessory` | Acessório | bolsa, boné, óculos, cinto |

   - A categoria decide a camada e a posição inicial da peça no provador manual: de baixo para cima, parte de baixo, parte de cima, agasalho e acessórios, com o calçado nos pés. Uma peça única ocupa o lugar das duas primeiras.
   - Quando a IA identificar a categoria sozinha (RF05), ela devolve um destes valores, e a troca é direta.
   - Ocasião, estação, cor e subtipos ficam para filtros futuros, como tags opcionais.
   - No banco, a coluna é `VARCHAR` com `CHECK`, e não um `ENUM` do Postgres: incluir uma categoria é trocar a constraint numa migração simples.
2. **Entrega das imagens pela API, no mesmo caminho do dono:** `GET /photos/{id}/image` e `GET /garments/{id}/image`.
   - A API confere a sessão e o dono. Atrás do nginx (`MEDIA_ACCEL_REDIRECT=true`), responde só com `X-Accel-Redirect: /_media/<chave>`, e o nginx entrega o arquivo (`location /_media/` é `internal`: acessá-lo direto dá 404). Sem o nginx (desenvolvimento local), a própria API envia o arquivo.
   - Como o cookie da sessão é `SameSite=Strict` e a API fica na mesma origem ([ADR-0004](0004-frontend-estatico-com-api-em-api.md)), um `<img src="/api/photos/<id>/image">` funciona sem token na URL.
   - O dono de outro usuário recebe `404`, igual a um id que não existe, para não revelar o que há na conta de outra pessoa.
   - `Cache-Control: private, max-age=31536000, immutable`: a imagem de um id nunca muda (uma nova foto ganha outro id), e `private` impede que um cache compartilhado a guarde.
3. **Exclusão:** primeiro o registro, depois o arquivo. Se o arquivo não puder ser apagado, sobra um arquivo órfão e inofensivo, em vez de um registro apontando para o nada. Se o registro falhar depois de o arquivo ser gravado no upload, o arquivo é removido.
4. **Limites:** 10 MB por imagem (a API confere e o nginx recusa corpos acima de 11 MB, que incluem os campos do formulário), no máximo 60 megapixels (proteção contra "bombas de descompressão"), e 30 envios por minuto por IP (`RATE_LIMIT_UPLOAD`).
5. **Cada envio gera dois arquivos, o original reduzido e uma miniatura**, ambos regravados sem metadados e no mesmo formato (JPEG ou PNG, que mantém a transparência das peças recortadas).
   - O lado maior do original é limitado a 2.048 px (uma foto de celular tem 4.000 px ou mais, e a tela não mostra tanto), e o da miniatura a 480 px. Imagens menores não são ampliadas.
   - A miniatura tem a chave derivada da imagem (`photos/<uuid>_thumb.jpg`), sem outra coluna no banco, e é entregue por `GET .../{id}/thumbnail`. As grades usam a miniatura, e o provador, a imagem inteira.
   - A orientação do EXIF é aplicada antes de descartar os metadados, para fotos de celular não ficarem deitadas.

## Consequências

- A grade carrega só miniaturas (cerca de 480 px), então a lista não fica pesada em redes lentas. O envio ainda leva o arquivo original (até 10 MB) pela rede: reduzir a foto no navegador, antes de enviar, ficou para depois.
- Apagar um usuário apaga os registros (`ON DELETE CASCADE`), mas não os arquivos (o original e a miniatura). A exclusão de conta (RF13) está adiada, e o risco aparece no DT-11.
- O volume `media` só cresce com o uso. Backup e espaço em disco ficam por conta de quem opera ([docs/deploy.md](../deploy.md)).
- O provador manual (próxima versão) lê as peças e as fotos por estas mesmas rotas, e usa a categoria para posicionar cada peça.
