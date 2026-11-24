# Núcleo (vale para todas as skills)

Cada skill traz só o próprio passo a passo; o que vale para todas está aqui. Por assunto, lidos só quando a skill manda: `marca.md` (marca, peças, pós), `video.md` (corte, cor, áudio, motion, Instagram), `bancos-e-referencias.md` (referência, inserções, música e sons).

## Ambiente
- `PY=$(cat ~/.ppgvet/python)`, `S=<pasta scripts do pacote>` (a skill mostra o caminho) e `FF=$("$PY" "$S/comum.py" --ff)`, o ffmpeg completo (tem zscale, legenda e texto; o `ffprobe` fica na mesma pasta). Se `~/.ppgvet/python` não existir, rodar a skill `instalar` primeiro.
- **Parte do kit sob demanda:** o kit instala só o essencial (ffmpeg, whisper, Python do pacote). Se um comando disser "Falta a parte 'X' do kit", avisar em uma linha o que vai baixar e quanto pesa, rodar `"$PY" "$S/instalar.py" --X` em segundo plano e repetir o comando. Sem pedir ok de novo. Se já der para saber no plano (Reels com motion, limpar voz), pôr o download no plano. Depois de `--motion`, rodar `/reload-plugins` para as skills `hyperframes` e `animate` aparecerem.
- Pastas desta pessoa: `"$PY" "$S/comum.py" --pastas` (chamadas, aulas, conferir, cortes, edicoes, musicas, downloads).
- Nos roteiros: `acervo:<caminho>` é uma peça do pacote (`acervo:logos-animadas/encerramento-ppgvet-vertical.mp4`) e `musicas:<arquivo>` é uma música da pasta `musicas/` da pessoa.

## Arquivo e versões
- **Original nunca é mexido.** Tudo sai em arquivo novo.
- **Versão nova nunca sobrescreve:** `-v2`, `-v3`… Versão com defeito: avisar e perguntar antes de apagar.
- **Nome de arquivo:** minúsculo, com hífen, do geral ao específico (`assunto-tema-v1.mp4`). Exceções: a aula curricular usa o título da tarefa, e a chamada usa o padrão de pastas dela (`CHAMADA N/`, `chamada <curso> N - <tema>.mp4`).
- **Menor, mas nunca mais feio:** compressão para site ou WhatsApp é H.264 `-crf 23 -preset slow -movflags +faststart`, conferindo que não piorou.
- **Organização:** o trabalho fica na pasta padrão do tipo (`--pastas`), com o nome padrão; a entrega vai onde a skill diz. Nada solto fora disso.
- **Máquina limpa:** antes de baixar ou criar uma peça, procurar no `acervo/` do pacote e nas pastas da pessoa (não duplicar). Trabalho longo ou em etapas: `NOTAS.md` na pasta do trabalho (estado, decisões, próximo passo), apagado quando o trabalho termina.

## Como trabalhar
0. **Primeira vez ou pedido sem material:** antes do plano, explicar em poucas linhas o que a skill precisa, onde pôr (o caminho real da pasta da pessoa) e um exemplo de pedido, pela seção "O que preciso de você" da skill. Se o material já veio, só perguntar o que faltar, no plano.
1. **Plano, uma vez:** antes de começar, mostrar o que vai ser feito (cada skill diz o que o plano dela inclui) e perguntar o que falta saber. Esperar o ok.
2. **Depois do ok, fazer tudo sem parar:** o lote inteiro, um atrás do outro. As dúvidas vão no plano; parar no meio só se surgir uma que a pessoa precisa decidir.
3. **Conferir e dar nota** a cada entrega: nota de 0 a 10 em cada critério da skill, mais acabamento geral. Abaixo de 8: corrigir sozinho e conferir de novo. O que vale para todo vídeo:
   - folha de quadros durante todo o tempo de cada gráfico (nada cobre nem encosta no rosto);
   - começo e fim transcritos de novo;
   - volume: `"$FF" -i out.mp4 -af loudnorm=print_format=summary -f null -` (voz ≈ -16 LUFS, pico ≤ -1,5 dBTP) e os dois canais no mesmo nível.
4. **Revisão no fim:** tudo pronto de uma vez (folha de quadros, nota de cada vídeo em uma linha e o que foi feito) para a pessoa aprovar ou pedir ajuste. Ajuste vira versão nova (`-v2`).
5. **Limpar depois da aprovação:** apagar só o que a própria skill criou de intermediário (cada skill lista): `tmp/` e `hf/` dos Reels, `posts/.tmp-post/` dos cortes, transcrições de trabalho, folhas de quadros e prévias. **Nunca** o original, a entrega, a legenda usada no vídeo nem os roteiros (`.json`), que servem para refazer.

- **Não inventar visual, texto, marca nem nome de pessoa:** perguntar no plano. Nome do curso, arte de CTA e grafia de nome vêm da pessoa ou de fonte confiável.
- **Perguntas** em caixas de opção (AskUserQuestion): até 4 por vez, a recomendada primeiro, cada uma compreensível sozinha. Texto que só a pessoa escreve (título, CTA, nome): opção "manter como está" e o texto vem no "Other".
- **IA generativa** (imagem, vídeo, voz, som): só em último caso, com aprovação da pessoa, e nunca fingindo aluno, professor ou sede.
- **Doc oficial:** ferramenta, formato de rede social ou plataforma segue a documentação oficial, conferida na hora quando o detalhe pode ter mudado (limite, formato, licença). Dizer qual doc foi usada.

## PC e tokens
- **PC:** todo render e transcrição dos scripts roda com prioridade baixa (`nice` no Mac, "abaixo do normal" no Windows): com o computador livre, usa a CPU toda e vai rápido; com a pessoa usando, cede a vez e nada trava. Comando pesado rodado direto, fora dos scripts (`npx hyperframes render`), vai com `nice -n 10` na frente no Mac. Não usar `taskpolicy -b` (prende nos núcleos econômicos e deixa lento mesmo com a máquina livre). O que demora vai em segundo plano. Um whisper por vez (ele já usa todos os núcleos); dá para renderizar um vídeo enquanto transcreve o próximo. Nunca vários renders pesados ao mesmo tempo.
- **Tokens** (quase tudo roda no computador, então quase nada precisa passar pela conversa):
  - comando sem progresso na saída (os scripts já saem em silêncio; ffmpeg com `-v error -nostats`, yt-dlp com `--quiet --no-warnings`, pip com `-q`). Saída longa: só o fim (`| tail -5`);
  - vídeo se olha por folha de quadros (`"$PY" "$S/folha.py" video.mp4 folha.jpg [a cada N s]`), nunca quadro a quadro;
  - transcrição, log e texto grande se buscam com `grep` ou se leem por trecho; inteiros só quando ler a fala é a tarefa (escolher cortes, conferir aula);
  - não reler arquivo já lido nem colar log ou JSON grande na resposta;
  - resposta curta: o que foi feito, onde está, a nota e o que precisa de decisão.

## Conteúdo
- **Grafia:** na dúvida sobre um nome (doença, toxina, fármaco, raça, técnica, pessoa, marca, software), **pesquisar a grafia certa** em fonte confiável antes de escrever. Nunca chutar o que o whisper ouviu (exemplo: "NASCE" era NASEM).
