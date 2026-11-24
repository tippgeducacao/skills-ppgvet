---
name: chamada
description: Monta a "chamada" da PPGVET para o Instagram, um vídeo 9:16 curto de professor falando do curso, com legenda na altura do peito, logo PPGVET embaixo, transição para a arte de CTA no fim e música de fundo. Também serve para depoimento de aluno, que segue o mesmo formato. Use quando pedirem para fazer, montar ou editar uma chamada ou um depoimento de aluno, ou vídeos de professor ou aluno falando do curso para o Instagram.
disable-model-invocation: true
---

# Chamada (Instagram)

Depoimento de aluno usa este mesmo fluxo: no lugar do professor, o aluno; a pasta fica `chamadas/depoimentos/<ALUNO>/`.

**O plano desta skill:** para cada chamada do lote, a tomada escolhida, o tema, a arte de CTA e a música. Depois do ok, monta todas e entrega a revisão com a folha e a nota de cada uma. **Limpar depois da aprovação:** as folhas de quadros.

## Antes de começar
- Ler `${CLAUDE_PLUGIN_ROOT}/regras/nucleo.md` (regras de todas as skills), `${CLAUDE_PLUGIN_ROOT}/regras/marca.md` (marca e peças), `${CLAUDE_PLUGIN_ROOT}/regras/video.md` (técnica, motion e Instagram), `${CLAUDE_PLUGIN_ROOT}/regras/bancos-e-referencias.md` (referência, inserções, música e sons).
- `PY=$(cat ~/.ppgvet/python)` e `S="${CLAUDE_PLUGIN_ROOT}/scripts"`.
- Pasta das chamadas: a linha `chamadas:` de `"$PY" "$S/comum.py" --pastas`.
- O layout (legenda e logo) e o volume final da chamada são os desta skill, não os dos Reels; o resto segue `video.md`.

## O que preciso de você
Se a pessoa chamou sem o material (ou é a primeira vez), explicar em poucas linhas, com o caminho real das pastas dela (`--pastas`):
- **Os vídeos do celular** do professor (ou do aluno): em `chamadas/<PROFESSOR>/_originais/` ou o link do Drive.
- **A arte de CTA** da campanha (PNG 1080x1350), na pasta do professor. Sem ela a chamada não fecha: nunca inventar.
- **O curso e o tema** de cada chamada, e quantas são.
- Exemplo de pedido: *"monta as chamadas 2 e 3 da Paola, pós de Bovinos; os vídeos e a arte estão na pasta dela"*.

## O padrão
- 1080x1920, 30 fps. Fala do professor, sem cortes visíveis.
- Legenda: Montserrat Bold 78, branca com sombra, de 2 a 4 palavras por vez, centro em y=1100 (peito). **Nunca cobre o rosto.**
- Logo PPGVET (`acervo/logos/ppgvet/logo-ppgvet.png`), com 270 px de largura, em y=1430, centralizada.
- Fim: a arte sobe com borrão vertical (0,3 s) e fica 6 s na tela. A arte é o PNG 1080x1350 da campanha, que a pessoa entrega (nunca inventar), sobre um fundo borrado dela mesma.
- Música: regra de música de `bancos-e-referencias.md` (séria, sem vocal, fora das 10 últimas usadas e nunca repetida entre as chamadas do mesmo professor; nunca em loop). Fica mais baixa sob a voz e sobe na arte. Volume final ≈ -14 LUFS.

## Pastas
```
chamadas/<PROFESSOR>/
  _originais/            vídeos do celular, nunca mexer
  <arte>.png             CTA da campanha
  CHAMADA N/
    bruto/chamada N.mp4  tomada escolhida, já cortada e em BT.709
    transcricao.json  legenda.srt  roteiro.json  creditos.txt
    chamada <curso> N - <tema>.mp4
```
Na primeira chamada de um professor, criar essa estrutura e pedir para a pessoa pôr os vídeos em `_originais/` e a arte na pasta do professor.

## Passo a passo
1. **Bruto:** pegar a tomada certa em `_originais`, cortar a fala e, se for vídeo de iPhone HDR, converter para BT.709 (filtro em `video.md`, com `FF=$("$PY" "$S/comum.py" --ff)`). Salvar em `bruto/`.
2. **Legenda:** `"$PY" "$S/transcrever.py" "bruto/chamada N.mp4" legenda -- -dtw large.v3.turbo -nfa -ml 16 -sow -osrt -ojf`
   Isso gera `legenda.srt` (e um `legenda.json`, que não é usado).
   Corrigir os erros direto no `legenda.srt` (termos técnicos, números como "1 ml"): é ele que vai para o vídeo. O campo `correcoes` do roteiro é só anotação do que foi corrigido. Na dúvida sobre um nome, pesquisar a grafia certa antes (`nucleo.md`).
3. **Roteiro** (`roteiro.json`, com caminhos relativos à pasta da chamada):
   ```json
   {
    "bruto": "bruto/chamada 1.mp4",
    "inicio": 0.0, "fim": 83.2,
    "legenda": "legenda.srt",
    "arte": "../arte.png", "arte_duracao": 6.0,
    "musica": "musicas:beats-energetico.mp3",
    "saida": "chamada <curso> 1 - <tema>.mp4",
    "correcoes": {"1ml": "1 ml"}
   }
   ```
   Opcionais: `legenda_y` (padrão 1100), `marca_dagua` `{arquivo, largura, y}` e `audio` (número da faixa de áudio, padrão 1).
4. **Montar:** `"$PY" "$S/chamada.py" "CHAMADA N/roteiro.json"`. Se a saída já existir, o script para: usar outro nome `-vN`. Ele também escreve o `creditos.txt` com o link da música (vem do `.origem.txt` dela) e anota a música como usada.
5. **Conferir e dar nota** (`"$PY" "$S/folha.py" "<saída>.mp4" folha.jpg 4`), de 0 a 10 em cada critério; abaixo de 8, corrigir e montar de novo:
   - legenda nunca cobre o rosto (se cobrir, ajustar `legenda_y`) e está sem erro de grafia;
   - começo e fim da fala certos, sem corte visível;
   - transição para a arte e a arte inteira na tela;
   - música certa (sem vocal, sem repetir) e volume (≈ -14 LUFS).
