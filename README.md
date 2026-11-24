# Skills da PPGVET para o Claude Code

> **Claude:** se pediram para instalar estas skills, siga a seção [Para o Claude](#para-o-claude-instalação-pedida-pela-pessoa) até o fim: pacote, atualização automática e kit.

Um pacote só, o **ppgvet**, com as skills de vídeo e de foto da equipe, no padrão da PPGVET. Roda no Mac e no Windows, no Claude Code pelo terminal, pelo VS Code ou pela aba Code do app Claude para computador. O repositório é público: não ponha aqui senha, chave nem dado de aluno.

| skill | para quê | como pedir |
|---|---|---|
| `/ppgvet:chamada` | chamada de professor ou depoimento de aluno para o Instagram (9:16, legenda, logo, arte de CTA, música) | "monta a chamada 2 da Marina", "monta o depoimento do João" |
| `/ppgvet:aula-curricular` | aulas do Meet editadas em lote (abertura, cortes, moldura da pós, card do professor) e, no fim, a tabela de onde subir cada uma na Panda | cole as tarefas das aulas |
| `/ppgvet:treinamento-academy` | treinamento para o PPGVET Academy: intro PPGVET, erros cortados e a moldura do Academy (tela grande com a câmera ao lado, ou só a câmera centralizada) | "edita esse treinamento pro Academy" + arquivo ou link |
| `/ppgvet:conferir-aula` | confere aulas que alguém editou, sem assistir: intro, moldura, cartela, cortes, erros de fala | "confere as aulas da pasta entrada" |
| `/ppgvet:cortes-live` | live (arquivo ou link) vira 7 ou 8 posts 9:16, com o professor em foco e slide e quem pergunta como apoio; também a aula completa com abertura, sem as partes da live | "tira os cortes dessa live" + link |
| `/ppgvet:editar-video` | edição livre e Reels de fala com textos animados (HyperFrames, com o Studio no navegador), legenda, cor, música, compressão | "edita esse vídeo para Reels" |
| `/ppgvet:baixar-video` | baixar vídeo do YouTube, TikTok, Facebook, Reddit, Twitch, X, Instagram e outros ~1.700 sites | "baixa esse vídeo" + link |
| `/ppgvet:live-vmix` | pacote da live no vMix num zip: moldura do Instagram, QR do cronograma (com UTM) e do certificado, links do chat e título da pós no topo; live de uma ou duas pós | "monta a live de quinta, pós PS, tema X" + foto do professor |
| `/ppgvet:patrocinador-podcast` | vídeo de boas-vindas a patrocinador de podcast com o mascote: prompts de Nano Banana e Veo para o Google Flow, conferência de cada geração e edição final com cartela e logos | "vídeo de boas-vindas da <empresa> no SuinoCast" |
| `/ppgvet:aulas-da-semana` | carrossel "Aulas da semana" do Instagram: capa e uma lâmina por aula (pós, dia, horário, professor com foto, tema), com cores e nomes oficiais e conferência medida | "faz o carrossel da semana" + a lista das aulas e a pasta das fotos |
| `/ppgvet:copy` | texto de marketing: legenda do Instagram, texto das artes, mensagem de WhatsApp e texto de anúncio (proposta para o tráfego), com 2 ou 3 versões para escolher e conferência medida | "legenda do carrossel da live de quinta, pós PS" + os fatos e o link do gerador |
| `/ppgvet:designer` | arte estática (post, carrossel, story, criativo de professor, anúncio) com referência nas artes da equipe, plano antes e conferência medida (cor, fonte, contraste, área segura, texto) | "post para o feed da pós de Suínos" + a foto e o objetivo |
| `/ppgvet:motion` (pela porta `video`) | peça animada sozinha: abertura, vinheta, logo ou texto animado, explicativo; quadros-chave aprovados antes de animar, som e conferência | "vinheta de 5 s com a logo da PPGVET para o YouTube" |
| `/ppgvet:editar-foto` | foto como um fotógrafo: retoque de luz, cor, pele, nitidez e horizonte, recorte no tamanho de uso, ampliar, tirar o fundo | "deixa essa foto profissional", "tira o fundo" |
| `/ppgvet:instalar` | prepara o computador (uma vez) e diz o que falta quando algo dá erro | "instala o kit", "está tudo instalado?" |

Não precisa digitar o comando: pedir com as próprias palavras basta. Em todas, o Claude mostra o plano, espera o ok, faz tudo, confere com nota e no fim mostra o resultado para aprovar ou pedir ajuste.

## Instalar (uma vez por computador)

**Precisa ter:** o Claude Code (no terminal, no VS Code ou na aba **Code** do app Claude para computador), com plano Pro ou acima, e o `git` (não precisa de conta no GitHub). No Mac, se o git faltar, o próprio sistema oferece instalar na primeira vez. No Windows, instalar o **Git for Windows** antes (`winget install Git.Git` ou https://git-scm.com/downloads/win): sem ele o pacote não baixa e os comandos das skills não rodam. O resto o kit instala.

**1. Colar o link no Claude Code** e pedir:
> instala as skills da PPGVET seguindo o README: https://github.com/tippgeducacao/skills-ppgvet

O Claude adiciona o pacote, liga a atualização automática e instala o kit essencial, seguindo a seção "Para o Claude", lá embaixo. Ele pede permissão antes de cada instalação: é só permitir. No fim, você fecha e abre o Claude Code. Se ele parar depois de adicionar o pacote, peça *"instala o kit"*.

À mão, no Claude Code:
```
/plugin marketplace add https://github.com/tippgeducacao/skills-ppgvet
/plugin install ppgvet@ppgvet
```
Depois: `/plugin` → **Marketplaces** → **ppgvet** → ligar auto-update; fechar e abrir o Claude Code; e pedir *"instala o kit"*.

**2. O kit essencial**, o estúdio de edição (~1 GB, de 10 a 20 min; o Claude pergunta só onde guardar os vídeos):

| ferramenta | para quê |
|---|---|
| ffmpeg completo | cortar, montar, legenda, cor |
| whisper + modelo em português | transcrição no próprio computador |
| Python do pacote (com OpenCV, yt-dlp e foto HEIC do iPhone) | rodar os scripts, baixar vídeos |

**Sob demanda:** o resto é instalado sozinho na primeira vez que uma skill precisar. O Claude avisa antes, em uma linha.

| parte | para quê | peso |
|---|---|---|
| voz (DeepFilterNet) | limpar ruído da voz | ~30 MB |
| motion (Node.js, Playwright, HyperFrames, animate) | textos animados nos Reels e animações de motion design | ~0,6 GB |
| foto (Real-ESRGAN, rembg) | ampliar imagem, tirar fundo | ~0,7 GB e ~1 GB de modelo na 1ª vez |

No Mac, se faltar o Homebrew, o Claude pede para você colar no Terminal o comando do site https://brew.sh, porque esse comando pede a senha do Mac.

## Atualizações
São automáticas, desde que o auto-update esteja ligado. Depois de cada mudança publicada no GitHub, inclusive skill nova, o Claude Code baixa a versão nova sozinho, em até ~10 minutos depois da primeira mensagem da sessão. Aparece "Plugin updated", e a versão nova vale na próxima vez que o Claude Code abrir (ou na hora, com `/reload-plugins`).

## Onde fica cada coisa
| o quê | onde |
|---|---|
| skills, scripts e peças padrão da casa (logos PPGVET, PPG e podcasts, intro, logos 3D, molduras, card sem nome, fontes) | dentro do pacote (não editar: quem cuida do pacote publica as mudanças) |
| configuração de cada pessoa, Python do pacote, modelo do whisper | `~/.ppgvet/` no computador de cada um |
| vídeos de trabalho, entregas, músicas baixadas (`musicas/`), downloads e referências de aula aprovadas | a pasta escolhida no kit (padrão: `Filmes/PPGVET` no Mac, `Vídeos/PPGVET` no Windows) |

O card com o nome do professor é gerado na hora, a partir do card sem nome. Efeitos sonoros básicos vêm no pacote (`acervo/sons/`, só gerados por nós ou CC0; origem em `sons/ORIGEM.md`). Música e outros efeitos não: cada pessoa baixa quando precisa (onde e como: `regras/bancos-e-referencias.md`).

## Problemas
- Uma skill deu erro de programa ou de arquivo não encontrado: pedir *"confere a instalação"*.
- As skills não aparecem: rodar `/plugin` e ver se o `ppgvet@ppgvet` está instalado e ligado.
- A atualização não chega: em `/plugin` → **Marketplaces** → **ppgvet**, conferir se o auto-update está ligado, ou atualizar na hora com `/plugin marketplace update ppgvet`.

## Para o Claude (instalação pedida pela pessoa)
Tudo numa ida só; a pessoa só fecha e abre o Claude Code no fim.
1. **Git:** `git --version`. Se faltar: no Mac, esse mesmo comando dispara a instalação das ferramentas de linha de comando (a pessoa clica em Instalar e espera); no Windows, `winget install -e --id Git.Git` e pedir para a pessoa fechar e abrir o Claude Code antes de seguir.
2. **Pacote:** se o comando `claude` existir no terminal: `claude plugin marketplace add https://github.com/tippgeducacao/skills-ppgvet` e `claude plugin install ppgvet@ppgvet`. Use o link `https://`: ele não precisa de chave SSH nem de conta. Se o `claude` não existir, pedir para a pessoa digitar os comandos com `/plugin` (seção "Instalar") e seguir quando ela disser que foi.
3. **Atualização automática**, que vem desligada em marketplace de terceiros: em `~/.claude/settings.json`, na entrada `extraKnownMarketplaces.ppgvet` que o comando criou, pôr `"autoUpdate": true`.
4. **Kit essencial**, sem esperar reiniciar: o caminho do pacote instalado é o `installPath` de `ppgvet@ppgvet` em `~/.claude/plugins/installed_plugins.json`. Abrir `<installPath>/skills/instalar/SKILL.md` e seguir os passos dele, usando `<installPath>` no lugar de `${CLAUDE_PLUGIN_ROOT}`.
5. No fim, pedir para a pessoa fechar e abrir o Claude Code, para as skills carregarem.

## Para quem cuida do pacote
- **Publicar:** commit e `./publicar.sh` (roda os testes dos scripts, valida o pacote e dá push). Sem número de versão no `plugin.json`, cada commit é uma versão nova, e a equipe recebe sozinha.
- **Organização:** tudo em `plugins/ppgvet/`. As regras ficam em `regras/`, um assunto por arquivo: `nucleo.md` (vale para todas: ambiente, arquivo e versões, como trabalhar, perguntas, IA, PC e tokens, grafia), `video.md` (corte, cor, áudio, motion, padrão Instagram), `bancos-e-referencias.md` (referência, inserções, música e sons) e `marca.md` (marcas, peças, siglas e molduras). Cada skill traz só o próprio passo a passo e lê só os arquivos de que precisa. Regra nova que vale para todas: entra no `nucleo.md`; de um assunto, no arquivo dele.
- **Skill nova:** criar `plugins/ppgvet/skills/<nome>/SKILL.md`; chega sozinha para todo mundo.
- **Testes do comportamento** (`plugins/ppgvet/evals/`, formato do `claude plugin eval`): a skill certa abre pelo pedido natural e pede o material que falta em vez de inventar. Rodar quando mudar uma descrição de skill, a porta `video` ou o "O que preciso de você": `cd plugins/ppgvet && claude plugin eval . --ablation none --model sonnet` (um caso por skill e os de comportamento; custa uso do plano, por isso fora do `publicar.sh`). Skill nova: um caso `disparo-<nome>` com o pedido como a equipe falaria.
- **Ferramenta nova:** se toda skill usa, vai no essencial (`instalar()` em `scripts/instalar.py`; quem já instalou roda de novo). Se é de poucas, vira parte sob demanda: entra em `partes()` do `instalar.py` e em `PARTES` do `comum.py`, e o script que usa chama `falta_parte("<parte>")` quando faltar.
- **Peças no repositório:** só as gerais da marca, em `acervo/`. O detector de rosto (YuNet, licença MIT) fica em `modelos/`. Modelos baixados pelo instalar, fora do repositório: BiRefNet (tirar fundo, MIT) e 4xNomosWebPhoto_esrgan (ampliar foto, de Phhofm, [OpenModelDB](https://openmodeldb.info/models/4x-NomosWebPhoto-esrgan), licença CC-BY 4.0: este crédito é a atribuição pedida). Som só se for gerado por `scripts/sons.py` ou CC0 de verdade, com a linha em `acervo/sons/ORIGEM.md`. Música e sons de Pixabay, Mixkit e afins não entram: as licenças não permitem redistribuir o arquivo solto.
