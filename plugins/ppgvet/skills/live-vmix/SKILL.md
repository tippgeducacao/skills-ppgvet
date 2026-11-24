---
name: live-vmix
description: Pacote da live no vMix, num zip - moldura do Instagram (foto do professor, tema, pós), QR do cronograma (com UTM) e do certificado, links do chat e título da pós no topo da tela; live de uma ou duas pós. Use quando mandarem foto e tema da live, ou pedirem moldura, QR, links ou título da live.
---

# Live no vMix

Gera tudo o que a live precisa e entrega num zip com os nomes que o projeto do vMix usa: a pessoa joga na pasta e substitui. Modelo original no Drive › LIVE › OVERLAYS.

## Antes de começar
- Ler `${CLAUDE_PLUGIN_ROOT}/regras/nucleo.md` (regras de todas as skills).
- `PY=$(cat ~/.ppgvet/python)` e `S="${CLAUDE_PLUGIN_ROOT}/scripts"`. A moldura recorta a foto com a parte `foto` do kit (sob demanda) e usa o Google Chrome (ou o Edge) para desenhar.
- Pasta da live: `<lives>/live-<aaaa-mm-dd>-<slug>/`, com `<lives>` de `"$PY" "$S/comum.py" --pastas`.

## O que preciso de você
- **Foto do professor** (qualquer fundo; o script recorta) e o **tema da live**, escrito como vai aparecer.
- **A pós** (ou as duas, se a live for de duas pós). Sigla na tabela do `regras/marca.md`; não disse qual, perguntar.
- **Link do certificado** da Even3. Sem ele, o resto sai e o `.txt` avisa que falta.
- Exemplo: *"live de quinta sobre biosseguridade na granja, pós PS e SA, foto do professor anexa, certificado https://www.even3.com.br/..."*

## O plano desta skill
Uma tabela: tema (como vai aparecer), pós, slug, foto recebida (e se precisa recortar) e certificado. Esperar o ok; depois as seções 1 a 4 sem parar.

## 1. Nome curto (slug) da live
Minúsculo, palavras com hífen, sem acento nem número, a partir do tema ("As principais habilidades do líder de 2027" → `principais-habilidades-do-lider`). Vai na UTM `utm_content`. Se a live já tem link no gerador "Links com UTM" do sistema, reusar o mesmo nome.

## 2. Moldura do Instagram
```
"$PY" "$S/live_moldura.py" --foto <foto> --tema "<tema>" --pos <sigla>[,<sigla 2>] --saida <pasta>/moldura-insta-<slug>.png
```
- Recorta o fundo sozinho. Foto já sem fundo: `--sem-recorte`.
- Duas pós: os dois títulos lado a lado, no tamanho que cabe.
- Antes de entregar, olhar o PNG. Cabeça grande ou pequena demais: `--largura` (padrão 500 = ombros do modelo). Recorte ruim (cabelo, braço): avisar e pedir outra foto.
- Fixo no modelo (`acervo/live/moldura-insta.html`; exemplo vazio em `moldura-insta-exemplo.png`): fundo, faixa "ESTAMOS AO VIVO", "LINK NA BIO", janela do vídeo transparente e logo PPGVET em todas as pós, inclusive as da PPG (exceção escrita no `marca.md`).

## 3. QRs e links
```
"$PY" "$S/live_qr.py" --pos <sigla>[,<sigla 2>] --conteudo <slug> --certificado "<link Even3>" --pasta <pasta>
```
- Um QR de cronograma por pós (overlay 1920x1080 transparente, cartão no canto inferior direito, "Cronograma <pós>"), o do certificado ("Acesse o Certificado!") e `links-<slug>.txt` com o link do chat de cada pós e o certificado.
- Cronograma: `https://<site da pós>/pos-<sigla>?utm_source=youtube-ppgvet&utm_medium=social&utm_campaign=live&utm_content=<slug>#cronograma`. O QR leva `<slug>-qr-code`; o link do chat, não. O certificado vai sem UTM (site de fora). Domínio pela marca da pós: PPG → `site.ppgeducacao.com.br`, PPGVET → `site.ppgvet.com.br`.
- O QR sai da API pública do QRCode Monkey (sem chave), estilo circular preto, e o script lê o QR antes de salvar: se não ler o link certo, para.

## 4. Zip
```
"$PY" "$S/live_pacote.py" --pasta <pasta> --pos <sigla>[,<sigla 2>] --conteudo <slug>
```
| no zip | o quê |
|---|---|
| `QR/QR CRONOGRAMA.png` (e `QR CRONOGRAMA 2.png` com duas pós) | QR do cronograma |
| `OVERLAYS/QR CERTIFICADO.png` | QR do certificado |
| `OVERLAYS/MOLDURA INSTA.png` | moldura do Instagram |
| `OVERLAYS/TITULO.png` | título da pós no topo (duas pós: lado a lado) |
| `LINKS IMPORTANTES.txt` | links do chat e do certificado |

**Conferir e dar nota** de 0 a 10 antes de entregar: moldura (rosto inteiro, sem cortar cabelo nem ombro, tema sem erro de grafia), QRs (lidos pelo script, link certo de cada pós), título da pós (nome oficial, cabe na moldura "uma pessoa"). Abaixo de 8: corrigir. Entregar: abrir a pasta, dizer o caminho do zip e a nota em uma linha.

## Títulos das pós (acervo)
| arquivo | uso |
|---|---|
| `acervo/titulos-pos/titulo-pos-<sigla>.png` | título em 4x (cinza `#3A3A3A` e nome em magenta `#D24BA8`) |
| `acervo/titulos-pos/titulo-pos-<sigla>-branco.png` | todo branco (moldura do Instagram) |
| `acervo/live/titulos-overlay/titulo-live-<sigla>.png` | vMix: 1920x1080 transparente, título no topo (~88 px, a ~30 px do topo) |

Desenho: Montserrat, "PÓS GRADUAÇÃO | NOME", quebras de linha iguais às dos criativos, sem "MBA" (`marca.md`). **Pós nova ou nome mudou:** pôr a sigla e as linhas em `POS` do `scripts/live_titulos.py`, rodar `"$PY" "$S/live_titulos.py" <sigla>` e publicar o pacote (quem cuida do pacote).
