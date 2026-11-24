---
name: motion
description: Peça de motion sozinha da PPGVET/PPG - abertura, vinheta, logo ou texto animado para story, explicativo animado - com quadros-chave aprovados antes de animar, som e conferência. Motion dentro de um vídeo (cartões dos Reels) é a editar-video.
disable-model-invocation: true
---

# Motion (peça animada avulsa)

## Antes de começar
- Ler `${CLAUDE_PLUGIN_ROOT}/regras/nucleo.md`, `${CLAUDE_PLUGIN_ROOT}/regras/marca.md`, `${CLAUDE_PLUGIN_ROOT}/regras/video.md`, `${CLAUDE_PLUGIN_ROOT}/regras/oficio/motion.md`, `${CLAUDE_PLUGIN_ROOT}/regras/oficio/design.md` (texto na tela), `${CLAUDE_PLUGIN_ROOT}/regras/oficio/som.md` (se tem som) e `${CLAUDE_PLUGIN_ROOT}/regras/antislop-midia.md`. Peça de motion avulsa é nível caprichado (`nucleo.md`).
- Em cada comando: `PY=$(cat ~/.ppgvet/python); S="${CLAUDE_PLUGIN_ROOT}/scripts"; A="${CLAUDE_PLUGIN_ROOT}/acervo"` e, para o HyperFrames, `eval "$("$PY" "$S/comum.py" --hf-env)"` (define `$HF`; parte `motion` do kit, sob demanda).
- Trabalho em `<edicoes>/<peca>/` (`"$PY" "$S/comum.py" --pastas`), com `roteiro.md` (batidas e decisões) e o projeto `hf/`.

## O que preciso de você
Se a pessoa chamou sem o material, explicar em poucas linhas:
- **A peça:** abertura, vinheta, logo ou texto animado, explicativo; onde vai (story, Reels, YouTube, telão) e a duração.
- **O texto exato** (ou os fatos: a skill `copy` escreve e confere) e a marca ou a pós.
- **Som:** com música, só efeitos ou mudo.
- Opcional: uma referência (link) do estilo.
- Exemplo: *"vinheta de 5 s com a logo da PPGVET para abrir os vídeos do YouTube, com som"*.

## Passo a passo
1. **Procurar antes no acervo:** logos animadas, intro e encerramentos (`marca.md`, "Peças do pacote"). O que já existe não se refaz.
2. **Ferramenta:** HyperFrames para texto, logo, cartão e abertura, com ou sem vídeo atrás (ler a skill `hyperframes`; bloco pronto do registro antes de desenhar do zero). Explicativo desenhado do zero (cena, personagem, diagrama que se monta): skill `animate`.
3. **Plano:** o roteiro em batidas (tempo de cada momento, o que entra, como entra, onde o som bate) e 3 a 5 **quadros-chave** estáticos gerados (`npx "$HF" snapshot` ou a prévia do `animate`). Esperar o ok dos quadros antes de animar (`oficio/motion.md`).
4. **Animar** no projeto `hf/`: só cores, fontes e logos do `marca.md` e do acervo; curvas e tempos do `oficio/motion.md` (nunca linear, um herói por momento, saída mais curta que entrada); texto dentro das margens do formato (`video.md`). `npx "$HF" check`; render no Mac com `nice -n 10` na frente: `npx "$HF" render . -o ../<peca>-v1.mp4 --quality delivery`.
5. **Som** (`oficio/som.md`): efeito do acervo `$A/sons/` no pico do gesto, um gesto = um som; música pela regra do `bancos-e-referencias.md`; teste do mudo (a peça se entende sem som).
6. **Conferir e dar nota** de 0 a 10: folha de quadros (`"$PY" "$S/folha.py" <peca>.mp4 folha.jpg 0.5`), `"$PY" "$S/checar.py" <peca>.mp4 [--instagram] [--lufs -14]` (FALHA barra a entrega) e a lista do `antislop-midia.md` (mesma entrada em tudo, curva linear, tudo se mexendo, vidro e neon). Critérios: leitura (cada texto fica na tela o tempo de ler duas vezes), ritmo, marca e acabamento. Abaixo de 8: corrigir.
7. **Entregar** o MP4, a folha e a nota em uma linha; o link do Studio (`npx "$HF" preview --background`) para ajuste fino. Ajuste vira `-v2`. Limpar depois da aprovação: prévias e quadros soltos (ficam o roteiro, o projeto `hf/` e a entrega).
