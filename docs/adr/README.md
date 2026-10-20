# Registros de decisão (ADR)

Cada arquivo registra uma decisão de arquitetura ou de escopo: o contexto, o que foi decidido e as consequências. Uma decisão aceita não é editada. Se ela mudar, crie um novo ADR que a substitua e marque o antigo como **Substituído por ADR-XXXX**.

| ADR | Decisão | Status |
| --- | --- | --- |
| [0001](0001-escopo-prova-de-conceito.md) | Escopo da prova de conceito, sem IA | Aceito (item 4, "Login", substituído pelo ADR-0006) |
| [0002](0002-monorepo-e-sveltekit.md) | Monorepo com frontend em SvelteKit | Aceito |
| [0003](0003-armazenamento-local-de-imagens-com-nginx.md) | Imagens em disco local, servidas pelo nginx | Aceito |
| [0004](0004-frontend-estatico-com-api-em-api.md) | Frontend estático, com a API na mesma origem em `/api` | Aceito |
| [0005](0005-versionamento-semantico-por-branch.md) | Versionamento semântico por branch | Aceito |
| [0006](0006-sessao-em-cookie-e-protecao-de-contas.md) | Sessão em cookie, de uma semana, e proteção das contas | Aceito |
| [0007](0007-categorias-de-pecas-e-entrega-das-imagens.md) | Categorias de peças e entrega das imagens | Aceito |

## Modelo

```markdown
# ADR-XXXX: Título

- **Status:** Proposto | Aceito | Substituído por ADR-YYYY
- **Data:** AAAA-MM-DD

## Contexto
## Decisão
## Consequências
```
