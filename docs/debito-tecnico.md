# Débito técnico

Pendências conhecidas que ficaram fora das entregas atuais. Ao resolver um item, remova-o daqui no mesmo PR, sem renumerar os demais. Ao encontrar um novo, adicione-o com o próximo ID, evidência e proposta.

Resolvidos:
- DT-01: dependências atualizadas;
- DT-02: PyJWT e `SECRET_KEY`;
- DT-03: rate limiting;
- DT-04: CI;
- DT-05: Postgres local e credenciais no `.env`;
- DT-06: enumeração de contas ([ADR-0006](adr/0006-sessao-em-cookie-e-protecao-de-contas.md));
- DT-07: política de senha;
- DT-08: grafia do username;
- DT-09: CSP.

**Prioridade:** 🔴 alta (risco de segurança ou indisponibilidade) · 🟡 média · 🟢 baixa

| ID | Prioridade | Tema | Resumo |
| --- | --- | --- | --- |
| [DT-10](#dt-10-sessões-sem-revogação) | 🟢 | Segurança | Sessões sem revogação |
| [DT-11](#dt-11-arquivos-órfãos-ao-apagar-contas) | 🟡 | Privacidade | Arquivos órfãos ao apagar contas |
| [DT-12](#dt-12-imagens-sem-miniaturas-nem-redimensionamento) | 🟡 | Desempenho | Imagens sem miniaturas nem redimensionamento |
| [DT-13](#dt-13-sem-testes-de-ponta-a-ponta-no-ci) | 🟢 | Qualidade | Sem testes de ponta a ponta no CI |

---

### DT-10: Sessões sem revogação

- **Evidência:** o token da sessão é um JWT sem estado, válido por uma semana. O logout só apaga o cookie do navegador, então um token copiado antes continua válido até expirar. Não há como encerrar a sessão de um dispositivo específico.
- **Proposta:**
  - guardar no usuário uma versão de sessão (`session_version`), incluída no token e conferida no `GET /users/me` e nas rotas protegidas;
  - incrementá-la na troca de senha e em "sair de todos os dispositivos".
  - Hoje, o único jeito de invalidar tudo é trocar a `SECRET_KEY` (ADR-0006).

### DT-11: Arquivos órfãos ao apagar contas

- **Evidência:** `photos` e `garments` têm `ON DELETE CASCADE` para o usuário, então apagar um usuário apaga os registros, mas não os arquivos do volume `media`. As fotos mostram o corpo da pessoa (dados sensíveis, LGPD). Hoje não há tela nem rota para apagar a conta (RF13 está adiado), então só acontece com uma exclusão manual no banco. Uma falha entre apagar o registro e apagar o arquivo também deixa um arquivo órfão.
- **Proposta:**
  - ao implementar a exclusão de conta, listar as chaves das imagens do usuário, apagar os registros e, depois, os arquivos (`ImageStorage.delete`);
  - um comando de manutenção que compara `media/` com `image_key` no banco e remove o que não está referenciado.

### DT-12: Imagens sem miniaturas nem redimensionamento

- **Evidência:** as imagens são guardadas e entregues no tamanho original (até 10 MB e 60 megapixels). A grade de peças e fotos carrega os arquivos inteiros, e uma foto de celular tem de 3 a 8 MB.
- **Proposta:**
  - gerar uma miniatura (cerca de 480 px no lado maior) no upload, em `ImageProcessor`, e entregá-la na grade (`GET .../image?size=thumb` ou uma rota própria);
  - limitar o lado maior da imagem original (por exemplo, 2.048 px);
  - no navegador, reduzir a foto antes de enviar (canvas), o que também poupa a rede do celular.

### DT-13: Sem testes de ponta a ponta no CI

- **Evidência:** os testes de unidade e de componente (com `fetch` simulado) não pegaram dois problemas que só apareceram ao rodar o fluxo num navegador real, atrás do nginx: um estilo inline bloqueado pela CSP e a diferença de espaços entre o modo de desenvolvimento e a build. Hoje esse fluxo é rodado à mão.
- **Proposta:** um job no CI que sobe o `docker compose`, e um script do Playwright com o fluxo principal (cadastro, login, envio de foto e de peça, exclusão), falhando em erros de console e violações de CSP.
