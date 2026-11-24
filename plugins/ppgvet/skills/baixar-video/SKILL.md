---
name: baixar-video
description: Baixa vídeo do YouTube, TikTok, Facebook, Reddit, Twitch, X, Vimeo, LinkedIn, Instagram (Reels e vídeo) e outros ~1.700 sites, com o yt-dlp, para a pasta de downloads, para usar como referência ou para editar material da própria PPGVET (live, aula, vídeo do canal). Use quando pedirem para baixar um vídeo, um Reels ou uma live a partir de um link.
disable-model-invocation: true
---

# Baixar vídeo

## Antes de começar
- Ler `${CLAUDE_PLUGIN_ROOT}/regras/nucleo.md` (regras de todas as skills).
- `PY=$(cat ~/.ppgvet/python)`, `S="${CLAUDE_PLUGIN_ROOT}/scripts"` e `FF=$("$PY" "$S/comum.py" --ff)`.
- Pasta: a linha `downloads:` de `"$PY" "$S/comum.py" --pastas` (aqui chamada de `<downloads>`).
- **Para que serve:** referência de estilo ou material da própria PPGVET. Vídeo baixado de rede social não entra em post nosso (inserção de banco livre: `bancos-e-referencias.md`), e da referência se copia o estilo (ritmo, transição, texto), nunca o conteúdo nem a marca (`bancos-e-referencias.md`).
- **Nunca pedir nem digitar senha.** Se o site pedir login, usar direto a sessão do navegador ("Conteúdo que pede login"): a pessoa pediu o download, não precisa perguntar de novo.

## O que preciso de você
Se a pessoa chamou sem o material (ou é a primeira vez), explicar em poucas linhas, com o caminho real das pastas dela (`--pastas`):
- **O link** do vídeo e **para quê** (referência de estilo ou material nosso para editar).
- Opcional: só um trecho (início e fim) ou só o áudio.
- Exemplo de pedido: *"baixa essa live do YouTube, só de 10:00 a 25:00"*.

## YouTube, TikTok, Facebook, Reddit, Twitch e outros sites
```
"$PY" -m yt_dlp --quiet --no-warnings --print after_move:filepath --ffmpeg-location "$FF" -S "res:1080,ext:mp4" --merge-output-format mp4 \
  -o "<downloads>/%(uploader)s - %(title).80s.%(ext)s" "<link>"
```
- Só o áudio (para transcrever): `-x --audio-format mp3` no lugar de `-S … --merge-output-format mp4`.
- Só um trecho: `--download-sections "*00:10:00-00:12:30"`.
- Twitch: vale para vídeo salvo (VOD), clipe e live em andamento (a live grava até a pessoa parar ou a live acabar).
- Site suportado? `"$PY" -m yt_dlp --list-extractors | grep -i <site>`. Kwai, Threads e Spotify não estão na lista.
- Se der erro de "versão antiga", atualizar: `"$PY" -m pip install -U yt-dlp`. Os sites mudam sempre e o yt-dlp acompanha.

## Conteúdo que pede login
Post privado, grupo do Facebook ou bloqueio do Instagram ou do TikTok para quem não está logado. Rodar de novo o mesmo comando com `--cookies-from-browser chrome` (no Windows, começar por `firefox`: o Chrome novo no Windows não deixa o yt-dlp ler os cookies), que usa a sessão do navegador onde a pessoa já está logada, sem senha. Se der erro ou ela não estiver logada no Chrome, tentar `safari` (Mac), `edge` (Windows) e `firefox`. Se nenhum funcionar, pedir para a pessoa entrar no site pelo navegador e tentar de novo. No Mac, o sistema pode pedir permissão para acessar o navegador: a pessoa aceita. Nunca guardar nem copiar o arquivo de cookies.

## Instagram
- Reels e vídeo: o mesmo comando do yt-dlp com o link (`instagram.com/reel/…` ou `/p/…`).
- O Instagram bloqueia quase todo download sem login. Se der "login required", "401" ou "Please wait a few minutes", usar a sessão do navegador ("Conteúdo que pede login").
- Post só de foto ou carrossel de fotos: o yt-dlp baixa só vídeo. A pessoa salva a imagem pelo navegador ou tira um print.
- Listar o perfil inteiro não funciona: o yt-dlp marca essa parte do Instagram como quebrada. Pedir os links dos posts.

## Depois de baixar
- Dizer onde o arquivo ficou, a duração e a resolução (`ffprobe` na mesma pasta do `$FF`).
- Arquivo de referência: guardar ao lado um `.origem.txt` com o link e a data.
