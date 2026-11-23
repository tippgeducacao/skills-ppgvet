---
name: instalar
description: Prepara o computador (Mac ou Windows) para as skills da PPGVET com o kit essencial (ffmpeg completo, whisper com o modelo em português e Python do pacote com yt-dlp) e confere o que falta quando algo dá erro. As partes pesadas (voz, motion com HyperFrames e animate, foto) ficam para quando uma skill precisar. Pergunta só onde guardar os vídeos. Use na primeira vez, quando uma skill disser para rodar o instalar, quando der erro de programa ou arquivo não encontrado, quando perguntarem "está tudo instalado?" ou quando a pessoa pedir para trocar a pasta dos vídeos.
---

# Instalar e conferir

Roda uma vez por computador e pode ser repetido sem estragar nada: o que já existe fica como está. Instala só o essencial (o estúdio de edição). As partes pesadas são instaladas quando uma skill precisa (passo 6). Tudo o que é da pessoa vai para `~/.ppgvet/`: configuração, Python do pacote e modelo do whisper. O pacote pode atualizar sem perder nada disso.

## 1. Python para rodar o instalador
- **Mac:** `python3 --version`. O Mac já vem com ele. Se pedir as "ferramentas de linha de comando", a pessoa aceita a instalação e roda de novo.
- **Windows:** `py --version` ou `python --version`. Se nenhum funcionar: `winget install -e --id Python.Python.3.12`. Conferir também o Git for Windows (`git --version`; se faltar, `winget install -e --id Git.Git`): as skills rodam os comandos no Git Bash. Depois de instalar qualquer um dos dois, a pessoa fecha e abre o Claude Code.

Daqui em diante, `PYS` é esse Python: `python3` no Mac, `py` no Windows.

## 2. Conferir o que já existe (não muda nada)
`PYS "${CLAUDE_PLUGIN_ROOT}/scripts/instalar.py" --conferir`

Se a pessoa só quis saber o que falta, ou veio por causa de um erro, explicar cada "falta" em uma linha (tabela abaixo) e só seguir para o passo 3 se ela pedir para instalar:

| falta | o que fazer |
|---|---|
| configuração, ffmpeg, whisper, modelo ou Python do pacote | seguir para o passo 3 (instalar) |
| `fora` (voz, motion, foto) | não é falta: parte sob demanda (passo 6) |
| peças padrão do pacote | o pacote veio incompleto: em `/plugin`, desinstalar e instalar de novo o `ppgvet@ppgvet` |
| pasta de trabalho | passo 3, escolhendo a pasta |

Se tudo estiver ok e o erro continuar, mostrar a mensagem de erro inteira e o comando que falhou.

## 3. Perguntar (caixa de pergunta, com a opção recomendada primeiro)
- **Pasta dos vídeos:** onde ficam os vídeos de trabalho e as entregas. O padrão é `Filmes/PPGVET` no Mac e `Vídeos/PPGVET` no Windows. Lá dentro, o kit cria `chamadas/`, `aulas-curriculares/`, `conferir-aula/`, `cortes-live/`, `edicoes/`, `musicas/` e `downloads/`. Se a configuração já tiver uma pasta, mostrar qual é e oferecer "manter".

Avisar que o essencial baixa ~1 GB (quase tudo é o modelo do whisper) e leva uns 10 a 20 min.

## 4. Instalar (em segundo plano)
`mkdir -p ~/.ppgvet && PYS "${CLAUDE_PLUGIN_ROOT}/scripts/instalar.py" --trabalho "<pasta>" > ~/.ppgvet/instalar.log 2>&1`
Homebrew, winget, pip e npm escrevem muito: a saída vai para o log, e no fim basta ler as últimas ~25 linhas (`tail -25 ~/.ppgvet/instalar.log`), que trazem a lista do que está ok. Erro: procurar a causa no log com `grep -n -i error`, sem ler o arquivo inteiro.
- **Mac sem Homebrew:** o script para e explica. A pessoa abre o app Terminal e cola o comando do site oficial https://brew.sh. Esse comando pede a senha do Mac, por isso o Claude não roda por ela. Depois, rodar o passo 4 de novo.
- **Windows:** o winget pode abrir uma janela pedindo permissão; a pessoa aceita. Se o ffmpeg não for encontrado logo depois de instalar, fechar e abrir o Claude Code e rodar de novo.

## 5. Mostrar o resultado
Mostrar a lista final com o que está ok e o que falta, e as pastas que o kit vai usar (`PY=$(cat ~/.ppgvet/python)` e depois `"$PY" "${CLAUDE_PLUGIN_ROOT}/scripts/comum.py" --pastas`). Conferir se a **atualização automática** está ligada: em `~/.claude/settings.json`, `extraKnownMarketplaces.ppgvet.autoUpdate` deve ser `true`. Se não estiver, ligar.

Por último, pedir para a pessoa fechar e abrir o Claude Code, para as skills carregarem.

## 6. Partes sob demanda
Quando um comando disser "Falta a parte 'X' do kit" (ou a pessoa pedir), avisar em uma linha e rodar em segundo plano, com o mesmo log:
`PY=$(cat ~/.ppgvet/python) && "$PY" "${CLAUDE_PLUGIN_ROOT}/scripts/instalar.py" --X >> ~/.ppgvet/instalar.log 2>&1`

| parte | o que instala | peso | quem usa |
|---|---|---|---|
| `--voz` | DeepFilterNet | ~0,4 GB | limpar ruído da voz |
| `--motion` | Node.js, Playwright, plugins HyperFrames e animate | ~0,6 GB | Reels com texto animado, animação de motion design |
| `--foto` | Real-ESRGAN e rembg | ~0,7 GB | `editar-foto`: ampliar e tirar fundo |

Os plugins do `--motion` (públicos, sem conta): o script instala sozinho se o comando `claude` existir. Se não existir, mostra os comandos `/plugin` para a pessoa digitar. Depois, `/reload-plugins`.
