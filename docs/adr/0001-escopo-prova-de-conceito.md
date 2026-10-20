# ADR-0001: Escopo da prova de conceito, sem IA

- **Status:** Aceito. O item 4, "Login", foi substituído pelo [ADR-0006](0006-sessao-em-cookie-e-protecao-de-contas.md), e o item 2, "A prova virtual é manual", pelo [ADR-0008](0008-conjuntos-e-ponte-para-ia-externa.md)
- **Data:** 2026-10-19

## Contexto

O documento de visão do VirtualFit (v1.0, 22/01/2026) descreve uma plataforma de prova virtual de roupas. A prova é gerada por IA (Google Gemini), e o documento inclui também assinatura premium, limites freemium e requisitos de LGPD.

O projeto tem um único desenvolvedor e ainda não tem deploy. O objetivo agora é validar a ideia com uma **prova de conceito (PoC)**, sem o custo e a complexidade da IA.

## Decisão

1. **A IA fica fora da PoC.** Ficam adiados:
   - a prova virtual por IA (RF07 e RF08);
   - a detecção de pessoa na foto (RF04);
   - a identificação automática da categoria da roupa (RF05).
2. **A prova virtual é manual.** O usuário posiciona as peças sobre a própria foto no navegador (arrastar, redimensionar e girar) e baixa o resultado. Isso demonstra o fluxo completo (foto → guarda-roupa → vestir → resultado). Quando a IA vier, ela substitui só a etapa de "vestir".
3. **Escopo da PoC:**

   | Parte | Na PoC | Adiado |
   | --- | --- | --- |
   | Conta | Cadastro e login com JWT | Confirmação por e-mail, refresh token, recuperação de senha (RF03), exclusão da conta (RF13) |
   | Fotos | Upload da foto do usuário e das roupas, em disco local ([ADR-0003](0003-armazenamento-local-de-imagens-com-nginx.md)) | Storage de objetos, CDN, redimensionamento |
   | Guarda-roupa | Listar, adicionar e excluir, com categoria manual | Filtros, busca, limite de 20 peças |
   | Prova virtual | Montagem manual no navegador, com download | IA, histórico (RF09), compartilhamento (RF12) |
   | Monetização | Nada | Premium (RF10) e limites freemium (RF11) |

4. **Padrões adotados enquanto não houver outra decisão:**
   - **Cadastro:** mantém o `username` atual. O `full_name` do RF01 entra se a PoC evoluir.
   - **Login:** um único token de acesso com validade de 24 h, como no RF02, sem refresh token. Hoje o padrão é `ACCESS_TOKEN_EXPIRE_MINUTES=15`; para a PoC, ele será configurado como `1440`.
   - **Navegadores:** apenas versões modernas. O documento pede ao mesmo tempo iOS 14+ e Safari 16+, o que é contraditório (o iOS 14 vem com o Safari 14), e isso fica para decidir depois.

## Consequências

- Sem fila nem worker de processamento: eles só seriam necessários pelo tempo de resposta da IA.
- O Redis continua opcional. Com uma instância, o rate limiting em memória basta ([docs/deploy.md](../deploy.md)).
- Sem custo de API de IA na PoC.
- Itens adiados com impacto de segurança já mapeados continuam em [docs/debito-tecnico.md](../debito-tecnico.md) (DT-06: confirmação por e-mail; DT-07: política de senha).
- Ao sair da PoC, revisar este ADR antes de implementar os requisitos adiados.
