---
name: designer
description: Arte estática da PPGVET/PPG como um designer da casa - post, carrossel, story, criativo de professor, arte de anúncio - com referência nas artes da equipe e conferência medida. Use quando pedirem arte, post, carrossel, story ou criativo. Aulas da semana: skill aulas-da-semana.
---

# Designer (arte estática)

## Antes de começar
- Ler `${CLAUDE_PLUGIN_ROOT}/regras/nucleo.md`, `${CLAUDE_PLUGIN_ROOT}/regras/marca.md`, `${CLAUDE_PLUGIN_ROOT}/regras/oficio/design.md` (o padrão da casa, tirado das artes e dos perfis), `${CLAUDE_PLUGIN_ROOT}/regras/oficio/copy.md` (todo texto da arte) e `${CLAUDE_PLUGIN_ROOT}/regras/antislop-midia.md`.
- Em cada comando: `PY=$(cat ~/.ppgvet/python); S="${CLAUDE_PLUGIN_ROOT}/scripts"; A="${CLAUDE_PLUGIN_ROOT}/acervo"`. Pasta: a linha `artes:` de `"$PY" "$S/comum.py" --pastas` (aqui `<artes>`).

## O que preciso de você
Se a pessoa chamou sem o material, explicar em poucas linhas:
- **A peça:** o que é (post, carrossel, story, criativo de professor, anúncio), onde vai e a marca ou a pós.
- **O objetivo e a ação** (salvar, link na bio, falar com especialista, confirmar presença).
- **O texto**, ou os fatos para escrever (a skill `copy` escreve e confere).
- **As fotos reais** (professor, aula, campo, turma). Sem foto boa, a peça sai sem foto; nunca banco nem IA fingindo pessoa ou lugar (`nucleo.md`).
- Exemplo: *"post para o feed da pós de Suínos chamando para falar com um especialista, com esta foto da aula na granja"*.

## Passo a passo
1. **Referência** (antes do plano; nível padrão e caprichado):
   - Drive conectado: 3 a 5 artes do mesmo tipo nas pastas da equipe, das mais recentes (descer pasta a pasta com `parentId`): artes atuais `1xWSoczhAye1qy_gAeUAQG99GLMD8fS8Y`, artes de 2024 a 2026 `1g5EHmuvCbiIOwAlLUu5WpyYJvk2Sh46y`. Sem Drive: o `oficio/design.md` já resume o padrão, mais os prints que a pessoa mandar.
   - Perfis `@ppgvet_oficial` e `@ppg.educacao`: o que está no ar do mesmo tipo (prints da pessoa, ou a API da Meta, só leitura, se o MCP estiver conectado).
   - Tirar 3 princípios (grid, hierarquia, cor) e desenhar do zero com a marca: copiar o como, nunca a peça (`oficio/design.md`, "Usar referência").
2. **Plano:** o desenho em palavras (formato, grid, os 3 níveis de texto com o texto exato, foto e recorte, cores pelo código, onde vão a logo e o bloco "PÓS-GRADUAÇÃO │ nome" de `$A/titulos-pos/`). Peça nova ou fora do padrão: mostrar um protótipo gerado (passo 4) antes de fazer o resto. Esperar o ok.
3. **Montar** em `<artes>/<peca>/` um HTML por peça ou lâmina (`01-capa.html`, `02-…`), todas com o mesmo grid:
   - fonte declarada com o nome Montserrat: `@font-face{font-family:Montserrat;src:url('<$A>/fontes/montserrat-variavel.ttf')}`;
   - logos, títulos das pós e peças pelo caminho do acervo (`file://`); cores só pelo código do `marca.md`;
   - foto tratada antes pela skill `editar-foto` (retoque, ampliar, tirar fundo) e nunca esticada;
   - faixa ou foto de ponta a ponta: `data-sangra` no elemento (pode encostar na borda).
4. **Gerar e medir:** `"$PY" "$S/arte.py" <peca>.html --formato <feed|carrossel|story|story-anuncio|quadrado>` em cada HTML. Ele gera o PNG e reprova texto que estoura ou sai da área segura, fonte que não é Montserrat, contraste baixo (pequena 4,5:1, grande 3:1), cor fora do `marca.md` e texto que a conferência da copy barra. FALHA: corrigir e rodar de novo. AVISO de letra sobre foto: olhar na peça e, se não ler bem, escurecer a foto com um degradê atrás do texto.
5. **Conferir e dar nota** de 0 a 10: hierarquia (o olho vai para o gancho primeiro), leitura no celular (olhar a peça com ~390 px de largura), marca e acabamento (`antislop-midia.md`). Carrossel: as lâminas lado a lado numa folha só (mesmo grid, ritmo). Abaixo de 8: corrigir.
6. **Entregar** os PNGs (e a folha do carrossel) com a nota em uma linha. Ajuste vira versão nova (`-v2`); o HTML fica para refazer.

| formato | tamanho | área livre (sem texto nem logo) |
|---|---|---|
| feed, carrossel | 1080x1350 | 64 px em volta |
| quadrado | 1080x1080 | 64 px em volta |
| story | 1080x1920 | 250 px em cima e embaixo |
| story de anúncio | 1080x1920 | 14% em cima, 35% embaixo, 6% dos lados (Meta) |
