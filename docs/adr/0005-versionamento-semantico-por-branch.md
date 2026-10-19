# ADR-0005: Versionamento semântico por branch

- **Status:** Aceito
- **Data:** 2026-10-19

## Contexto

O projeto tem um único desenvolvedor, que trabalha com uma branch por vez a partir da `develop` e faz o merge por pull request. Os nomes de branch numerados por PR ou issue não funcionaram bem:

- o número do PR só existe depois da branch;
- abrir uma issue para cada tarefa foi considerado cerimônia demais.

O documento de visão pede versionamento semântico (RNF07).

## Decisão

1. **Cada branch é a próxima versão do produto:** `<tipo>/<X.Y.Z>-<descrição>` (ex.: `feat/0.2.0-frontend-sveltekit`).
2. **O número sai da versão atual e do tipo da branch:**

   | Tipo | Incremento |
   | --- | --- |
   | `feat` | minor (`0.2.0` → `0.3.0`) |
   | `fix`, `chore`, `docs`, `refactor`, `test` | patch (`0.2.0` → `0.2.1`) |

   Enquanto a versão for `0.x`, mudanças incompatíveis também sobem o minor. A `1.0.0` fica reservada para o lançamento depois da prova de conceito.
3. **Uma versão para o monorepo inteiro:** a mesma em `backend/pyproject.toml` e `frontend/package.json`. A API a expõe no OpenAPI e no healthcheck.
4. **Toda branch** atualiza a versão e adiciona sua entrada no [`CHANGELOG.md`](../../CHANGELOG.md).
5. **Depois do merge** na `develop`, a versão recebe a tag `vX.Y.Z`.

## Consequências

- O nome da branch, o changelog, a tag e a versão em execução contam a mesma história, sem depender de issues.
- Como só existe uma branch aberta por vez, os números não colidem. Se um dia houver branches em paralelo, a de merge mais tardio precisa ser renumerada.
- A branch `chore/6.1-monorepo` foi a última no formato antigo. A `develop`, depois dela, conta como `0.1.0`.
