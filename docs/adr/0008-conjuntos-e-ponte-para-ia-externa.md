# ADR-0008: Conjuntos de peças e ponte para uma IA externa

- **Status:** Aceito
- **Data:** 2026-10-20
- **Substitui em parte:** [ADR-0001](0001-escopo-prova-de-conceito.md), item 2 ("A prova virtual é manual", com arrastar, redimensionar e girar). O resto do ADR-0001, inclusive "sem IA integrada", continua valendo.

## Contexto

O ADR-0001 previa que o usuário posicionasse as peças sobre a própria foto no navegador. Ao desenhar a tela, a decisão mudou: em vez de editar uma imagem, o usuário **monta um conjunto** (peças em "quadradinhos", uma por categoria) e leva o resultado para uma IA de imagens, que faz a prova de verdade. O VirtualFit não integra nenhuma IA (sem custo de API, e a foto nunca sai do sistema por conta própria); ele prepara a entrada.

## Decisão

1. **Um conjunto é um nome e as peças do guarda-roupa**, salvo no banco: a tabela `outfits` (dono e nome) e a tabela de vínculo `outfit_garments` (`outfit_id`, `garment_id`).
   - Regras, no domínio (`domain/outfit_rules.py`) e conferidas no backend: **uma peça por categoria**, e a **peça única** (vestido, macacão) não combina com parte de cima nem de baixo, porque ocupa o lugar das duas. O frontend aplica as mesmas regras para não montar o que seria recusado, mas quem manda é o backend.
   - As peças precisam ser do usuário. Uma peça de outro usuário responde como uma que não existe (`outfit_unknown_garment`, 422).
   - Excluir um conjunto não exclui as peças. Excluir uma peça a tira de todos os conjuntos (`ON DELETE CASCADE` no vínculo), e um conjunto pode ficar vazio.
   - A **foto não faz parte do conjunto**: o usuário a escolhe na hora de usar. Assim, o mesmo conjunto serve para qualquer foto.
2. **O provador é um mapa do corpo**: cada categoria tem um quadradinho **na posição em que a peça é vestida**, ao lado da foto (no celular, abaixo dela).
   - Acessório na cabeça (em cima, no meio), agasalho e parte de cima lado a lado no tronco, parte de baixo nas pernas e calçado nos pés, em colunas de dois quadrados. No computador, a foto tem a altura do mapa, então as zonas do corpo ficam na altura dos quadradinhos.
   - A **peça única** (vestido, macacão) é uma opção abaixo do mapa. Quando escolhida, vira um quadradinho **vertical** (a altura do tronco e das pernas juntos), ao lado do agasalho, e a parte de cima e a de baixo somem.
   - Sem arrastar, girar ou redimensionar.
3. **A imagem das roupas é montada no navegador** (canvas): as peças, em tamanho inteiro, numa grade de células quadradas de 512 px, na ordem do corpo, sobre fundo branco liso, sem texto. A grade é de 1×1, 2×1, 2×2 ou 3×2, conforme o número de peças. Nada é enviado ao servidor.
4. **O texto para a IA é gerado por regras, no frontend**, em uma função pura (`src/lib/outfit/prompt.ts`), em **inglês** (as IAs de imagem costumam entendê-lo melhor):
   - diz que a imagem 1 é a foto da pessoa e que a imagem 2 é a grade de roupas, e lista as peças na mesma ordem da grade, com a categoria e o nome que o usuário deu à peça;
   - pede a mesma pessoa vestida exatamente com aquelas peças, mantendo rosto, cabelo, tom de pele, corpo e pose, sem acrescentar outras roupas;
   - opções: manter o fundo da foto (padrão) ou usar um fundo neutro, e um pedido extra em texto livre (até 200 caracteres).
   - Como não há visão computacional, **o nome da peça é o que descreve a roupa para a IA**. O campo de nome continua opcional, e o formulário sugere incluir a cor e o tipo.
5. **Levar para a IA:** copiar a foto, copiar a imagem das roupas, copiar o texto, baixar as imagens e, em aparelhos que sabem, compartilhar tudo pelo menu do sistema.
   - Imagens vão como PNG (o único formato aceito pela área de transferência em todos os navegadores, e as fotos são JPEG).
   - A cópia de **imagem** só funciona em contexto seguro (HTTPS ou `localhost`). Fora dele, a tela oferece só o download e explica o motivo. O texto pode ser copiado sempre, com um método alternativo.
   - A cópia começa dentro do clique, com a imagem entregue como promessa, o que o Safari exige.
6. **O resultado da IA não volta para o VirtualFit.** O usuário usa a imagem gerada fora do sistema. Quando houver integração com uma IA, a mesma entrada (foto e conjunto) a alimenta.

## Consequências

- Sem custo de IA e sem enviar dados a terceiros pelo servidor. Mas a foto sai do VirtualFit quando o usuário a cola em outra ferramenta, e a tela avisa isso antes.
- A qualidade do resultado depende da IA escolhida e do nome das peças, e o VirtualFit não consegue conferi-lo.
- Pelo celular em HTTP na rede local (desenvolvimento), a cópia de imagem não funciona: usa-se o download. Em produção, com HTTPS, funciona.
- Um conjunto pode ficar vazio se todas as suas peças forem excluídas. A lista mostra "Conjunto vazio", e o usuário pode excluí-lo.
- O limite de uma peça por categoria vale também para acessórios: quem usa dois acessórios monta o conjunto com um deles.
