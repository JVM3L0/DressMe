# Registros de decisão (ADR)

Cada arquivo registra uma decisão de arquitetura ou de escopo: o contexto, o que foi decidido e as consequências. Uma decisão aceita não é editada. Se ela mudar, crie um novo ADR que a substitua e marque o antigo como **Substituído por ADR-XXXX**.

| ADR | Decisão | Status |
| --- | --- | --- |
| [0001](0001-escopo-prova-de-conceito.md) | Escopo da prova de conceito, sem IA | Aceito |
| [0002](0002-monorepo-e-sveltekit.md) | Monorepo com frontend em SvelteKit | Aceito |
| [0003](0003-armazenamento-local-de-imagens-com-nginx.md) | Imagens em disco local, servidas pelo nginx | Aceito |

## Modelo

```markdown
# ADR-XXXX: Título

- **Status:** Proposto | Aceito | Substituído por ADR-YYYY
- **Data:** AAAA-MM-DD

## Contexto
## Decisão
## Consequências
```
