# Skills da PPGVET para o Claude Code

Um pacote só, o **ppgvet**, com as skills de vídeo e de foto da equipe, no padrão da PPGVET. Roda no Mac e no Windows, no Claude Code pelo terminal, pelo VS Code ou pela aba Code do app Claude para computador. O repositório é público: não ponha aqui senha, chave nem dado de aluno.

| skill | para quê | como pedir |
|---|---|---|
| `/ppgvet:chamada` | chamada de professor ou depoimento de aluno para o Instagram (9:16, legenda, logo, arte de CTA, música) | "monta a chamada 2 da Paola", "monta o depoimento do João" |
| `/ppgvet:aula-curricular` | aulas do Meet editadas em lote (abertura, cortes, moldura da pós, card do professor) e, no fim, a tabela de onde subir cada uma na Panda | cole as tarefas das aulas |
| `/ppgvet:conferir-aula` | confere aulas que alguém editou, sem assistir: intro, moldura, cartela, cortes, erros de fala | "confere as aulas da pasta entrada" |
| `/ppgvet:cortes-live` | live (arquivo ou link) vira 7 ou 8 posts 9:16, com o professor em foco e slide e quem pergunta como apoio; também a aula completa com abertura, sem as partes da live | "tira os cortes dessa live" + link |
| `/ppgvet:editar-video` | edição livre e Reels de fala com textos animados (HyperFrames, com o Studio no navegador), legenda, cor, música, compressão | "edita esse vídeo para Reels" |
| `/ppgvet:baixar-video` | baixar vídeo do YouTube, TikTok, Facebook, Reddit, Twitch, X, Instagram e outros ~1.700 sites | "baixa esse vídeo" + link |
| `/ppgvet:editar-foto` | foto como um fotógrafo: retoque de luz, cor, pele, nitidez e horizonte, recorte no tamanho de uso, ampliar, tirar o fundo, melhorar rosto borrado (este só no Mac) | "deixa essa foto profissional", "tira o fundo" |
| `/ppgvet:instalar` | prepara o computador (uma vez) e diz o que falta quando algo dá erro | "instala o kit", "está tudo instalado?" |

Não precisa digitar o comando: pedir com as próprias palavras basta. Em todas, o Claude mostra o plano, espera o ok, faz tudo, confere com nota e no fim mostra o resultado para aprovar ou pedir ajuste.

## Instalar (uma vez por computador)

**Precisa ter:** o Claude Code (no terminal, no VS Code ou na aba **Code** do app Claude para computador), com plano Pro ou acima, e o `git` (não precisa de conta no GitHub). No Mac, se o git faltar, o próprio sistema oferece instalar na primeira vez. No Windows, instalar o **Git for Windows** antes (`winget install Git.Git` ou https://git-scm.com/downloads/win): sem ele o pacote não baixa e os comandos das skills não rodam. O resto o kit instala.

**1. Colar o link no Claude Code** e pedir:
> instala as skills da PPGVET: https://github.com/tippgeducacao/skills-ppgvet

O Claude adiciona o pacote, liga a atualização automática e instala o kit, seguindo a seção "Para o Claude", lá embaixo. No fim, você fecha e abre o Claude Code.

À mão, no Claude Code:
```
/plugin marketplace add https://github.com/tippgeducacao/skills-ppgvet
/plugin install ppgvet@ppgvet
```
Depois: `/plugin` → **Marketplaces** → **ppgvet** → ligar auto-update; fechar e abrir o Claude Code; e pedir *"instala o kit"*.

**2. O kit** (~4 GB, de 20 a 40 min; o Claude pergunta só onde guardar os vídeos):

| ferramenta | para quê |
|---|---|
| ffmpeg completo | cortar, montar, legenda, cor |
| whisper + modelo em português | transcrição no próprio computador |
| Python do pacote (com OpenCV, rembg e yt-dlp) | rodar os scripts, retocar e tirar fundo, baixar vídeos |
| Real-ESRGAN | ampliar imagem |
| GFPGAN (só no Mac) | melhorar rosto borrado |
| DeepFilterNet | limpar ruído da voz |
| Node.js, Playwright e os plugins **HyperFrames** e **animate** | textos animados nos Reels e animações de motion design |

No Mac, se faltar o Homebrew, o Claude pede para você colar no Terminal o comando do site https://brew.sh, porque esse comando pede a senha do Mac.

## Atualizações
São automáticas, desde que o auto-update esteja ligado. Depois de cada mudança publicada no GitHub, inclusive skill nova, o Claude Code baixa a versão nova sozinho, em até ~10 minutos depois da primeira mensagem da sessão. Aparece "Plugin updated", e a versão nova vale na próxima vez que o Claude Code abrir (ou na hora, com `/reload-plugins`).

## Onde fica cada coisa
| o quê | onde |
|---|---|
| skills, scripts e peças padrão da casa (logos PPGVET, PPG e podcasts, intro, logos 3D, molduras, card sem nome, fontes) | dentro do pacote (não editar: quem cuida do pacote publica as mudanças) |
| configuração de cada pessoa, Python do pacote, modelo do whisper | `~/.ppgvet/` no computador de cada um |
| vídeos de trabalho, entregas, músicas baixadas (`musicas/`), downloads e referências de aula aprovadas | a pasta escolhida no kit (padrão: `Filmes/PPGVET` no Mac, `Vídeos/PPGVET` no Windows) |

O card com o nome do professor é gerado na hora, a partir do card sem nome. Música, som e efeito não vêm no pacote: cada pessoa baixa quando precisa (onde e como: regras de edição).

## Problemas
- Uma skill deu erro de programa ou de arquivo não encontrado: pedir *"confere a instalação"*.
- As skills não aparecem: rodar `/plugin` e ver se o `ppgvet@ppgvet` está instalado e ligado.
- A atualização não chega: em `/plugin` → **Marketplaces** → **ppgvet**, conferir se o auto-update está ligado, ou atualizar na hora com `/plugin marketplace update ppgvet`.

## Para o Claude (instalação pedida pela pessoa)
Tudo numa ida só; a pessoa só fecha e abre o Claude Code no fim.
1. **Git:** `git --version`. Se faltar: no Mac, esse mesmo comando dispara a instalação das ferramentas de linha de comando (a pessoa clica em Instalar e espera); no Windows, `winget install -e --id Git.Git` e pedir para a pessoa fechar e abrir o Claude Code antes de seguir.
2. **Pacote:** se o comando `claude` existir no terminal: `claude plugin marketplace add https://github.com/tippgeducacao/skills-ppgvet` e `claude plugin install ppgvet@ppgvet`. Use o link `https://`: ele não precisa de chave SSH nem de conta. Se o `claude` não existir, pedir para a pessoa digitar os comandos com `/plugin` (seção "Instalar") e seguir quando ela disser que foi.
3. **Atualização automática**, que vem desligada em marketplace de terceiros: em `~/.claude/settings.json`, na entrada `extraKnownMarketplaces.ppgvet` que o comando criou, pôr `"autoUpdate": true`.
4. **Kit**, sem esperar reiniciar: o caminho do pacote instalado é o `installPath` de `ppgvet@ppgvet` em `~/.claude/plugins/installed_plugins.json`. Abrir `<installPath>/skills/instalar/SKILL.md` e seguir os passos dele, usando `<installPath>` no lugar de `${CLAUDE_PLUGIN_ROOT}`.
5. No fim, pedir para a pessoa fechar e abrir o Claude Code, para as skills carregarem.

## Para quem cuida do pacote
- **Publicar:** commit e `./publicar.sh` (roda os testes dos scripts, valida o pacote e dá push). Sem número de versão no `plugin.json`, cada commit é uma versão nova, e a equipe recebe sozinha.
- **Organização:** tudo em `plugins/ppgvet/`. As regras que valem para todas as skills de vídeo ficam num lugar só, `regras/edicao.md` (ambiente, arquivo e versões, como trabalhar, PC e tokens, conteúdo, técnica, motion, padrão Instagram, música), e a marca em `regras/marca.md` (marcas, peças, siglas e molduras). Cada skill traz só o próprio passo a passo. Regra nova que vale para todas: entra em `edicao.md`, não na skill.
- **Skill nova:** criar `plugins/ppgvet/skills/<nome>/SKILL.md`; chega sozinha para todo mundo.
- **Ferramenta nova no kit:** acrescentar em `scripts/instalar.py` e fazer a skill que depende dela avisar "rode o instalar" quando faltar (quem já instalou precisa rodar de novo).
- **Peças no repositório:** só as gerais da marca, em `acervo/`. O detector de rosto (YuNet, licença MIT) fica em `modelos/`. Música, som e efeito não entram: as licenças (Pixabay, Mixkit) não permitem redistribuir o arquivo solto.
- **Referência de aula aprovada** por alguém (`<conferir>/referencias/<SIGLA>.jpg`): pôr em `acervo/aulas-referencia/` e publicar.
