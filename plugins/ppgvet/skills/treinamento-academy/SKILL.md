---
name: treinamento-academy
description: Edita treinamentos para o PPGVET Academy (time comercial, embaixadores, ferramentas como Manychat ou CRM). Põe a intro PPGVET no começo, corta os erros (recomeço, repetição, gaguejo longo, conversa de bastidor, pausa longa) e encaixa na moldura do Academy - tela compartilhada do Meet na moldura com a tela grande e a câmera à direita; só câmera (Meet em tela cheia ou câmera do estúdio) no bloco centralizado. Sem legenda e sem música. Use quando pedirem edição "estilo treinamento", "treinamento para o Academy", "treinamento do comercial" ou mandarem gravações de treinamento.
---

# Treinamento para o PPGVET Academy

## Antes de começar
- Ler `${CLAUDE_PLUGIN_ROOT}/regras/edicao.md` (ambiente e regras gerais) e `${CLAUDE_PLUGIN_ROOT}/regras/marca.md` (marca e peças).
- `PY=$(cat ~/.ppgvet/python)` e `S="${CLAUDE_PLUGIN_ROOT}/scripts"`.
- Pasta: a linha `treinamentos:` de `"$PY" "$S/comum.py" --pastas` (aqui `<treinos>`). As gravações ficam na raiz dela, os prontos em `<treinos>/prontos/` e o trabalho de cada treinamento (transcrição e `treinamento.json`) em `<treinos>/trabalho/<nome>/`.

## O que preciso de você
Se a pessoa chamou sem o material, explicar em poucas linhas:
- **As gravações:** o arquivo do Meet ("… - Recording.mp4") ou da câmera do estúdio, na pasta `<treinos>` (mostrar o caminho real), ou o link do Drive (baixar com a skill `baixar-video` ou pelo conector do Google Drive, se houver).
- **O que é cada treinamento:** o assunto e para quem (ex.: "vendas dia 1, time comercial"). Se uma gravação vira mais de um treinamento, ou se dois dias viram um só, dizer onde dividir.
- Exemplo de pedido: *"edita esses dois treinamentos pro Academy: o de marketing do dia 1 e o de vendas do dia 2"* + link ou arquivos.

## O plano desta skill
Uma tabela, uma linha por treinamento: gravação, fonte (`meet` ou `camera`), nome do arquivo final, duração bruta e prevista, e os erros mais longos que vão sair (com o minuto). As dúvidas vão nele: onde dividir, duas câmeras do estúdio (qual usar: a que mostra o rosto de frente; sem como decidir, perguntar), trecho que parece erro mas pode ser conteúdo. Depois do ok, as seções 1 a 4 rodam para cada treinamento sem parar.

**Limpar depois da aprovação:** as subpastas de `<treinos>/trabalho/` e as folhas de quadros. Ficam a gravação original, o treinamento pronto e o `treinamento.json` (para refazer).

## O padrão
- **Abertura:** `acervo/intro/PPGVET.mov`, sempre. Fim: sem nada, acaba na última fala.
- **Moldura** (o script troca sozinho no meio do vídeo):
  - tela compartilhada do Meet: `acervo/molduras-aula/PADRÃO.png` (tela grande à esquerda, câmera à direita: o layout do Meet já coincide com as caixas);
  - só câmera (Meet em tela cheia ou câmera do estúdio): `acervo/molduras/moldura-aula-ppgvet-ppg-16x9.png`, câmera no bloco centralizado.
- **Sem** legenda, música, card de nome ou CTA.
- **Nome:** minúsculo-com-hífen, do geral ao específico: `treinamento-academy-<assunto>[-<parte>]` (ex.: `treinamento-academy-vendas-dia-1`).

## 1. Transcrever (em segundo plano, cerca de 4 min por hora)
`"$PY" "$S/transcrever.py" "<gravação>" treino --leitura -- -mc 0 -sns -osrt`

## 2. Achar os erros (ler a transcrição inteira: escolher cortes é a tarefa)
Sai:
- **antes do começo e depois do fim:** teste de som, espera, "já está gravando?", despedida técnica;
- **recomeço:** "deixa eu falar de novo", "corta", "vou começar de novo", "errei": sai a tentativa ruim, fica a última boa;
- **repetição:** a mesma frase dita duas ou três vezes seguidas: fica a melhor (em geral a última);
- **gaguejo longo, tosse, interrupção** (alguém entra, celular toca) e **pausa sem fala acima de ~3 s** (procurar buracos no tempo do `.srt`);
- **conversa de bastidor:** "abre aí a outra tela", "tá aparecendo?", quando não ensina nada.

Fica: pausa natural, "né", "então" e piada que faz parte da fala. Na dúvida, fica (e vai no plano).

Atalho para achar recomeço: `grep -n -i -E "de novo|corta|recome|errei|desculpa|perdão|pera|peraí|deixa eu|vou repetir|não, não" treino.leitura.txt` e ler em volta. Não picotar: um erro curto (menos de ~1 s) só sai se atrapalhar o entendimento.

## 3. treinamento.json e conferir
Os `trechos` são o que **fica**, em ordem; o que está entre eles sai.
```json
{"bruto": "Treinamento comercial - 2026_11_19 - Recording.mp4",
 "nome": "treinamento-academy-vendas-dia-1", "fonte": "meet",
 "trechos": [
  {"inicio": "00:02:10,000", "fim": "00:14:05,000", "primeira_frase": "Bom dia, pessoal, hoje a gente vai falar", "ultima_frase": "e é isso que faz o cliente confiar"},
  {"inicio": "00:14:20,000", "fim": "00:41:30,000", "primeira_frase": "Então, o segundo ponto é a prospecção", "ultima_frase": "Valeu, pessoal, até a próxima"}]}
```
- `bruto` é relativo a `<treinos>` (ou um caminho completo). `fonte`: `meet` (gravação do Meet, com ou sem tela compartilhada) ou `camera` (câmera do estúdio ou celular: tudo no bloco centralizado).
- Copiar as frases da transcrição (5 palavras ou mais). O tempo pode ser aproximado: o script ouve 25 s em volta e acha a palavra exata.
- `"$PY" "$S/treinamento.py" treinamento.json --pontos` mostra onde cada corte caiu, o que viria logo depois e os momentos com tela compartilhada. Conferir sozinho: nenhuma emenda come fala de conteúdo e nenhum erro ficou. Algo errado: ajustar e rodar de novo.

## 4. Montar (em segundo plano)
`"$PY" "$S/treinamento.py" treinamento.json` → `<treinos>/prontos/<nome>.mp4` (já existe: `-v2`). Intro, trechos com fade de 30 ms no áudio, moldura certa a cada momento, voz a -16 LUFS, 1920x1080 a 30 fps, teto de 2 Mbps.

## 5. Conferir, dar nota e entregar
Para cada treinamento: folha de quadros (`"$PY" "$S/folha.py" <pronto>.mp4 folha.jpg 60`) e, nas emendas, o começo e o fim transcritos de novo. Nota de 0 a 10; abaixo de 8, corrigir e montar de novo:
- começo: intro e logo depois a primeira fala de conteúdo;
- emendas: nenhum erro ficou, nenhuma fala comida, sem pulo estranho de imagem;
- moldura: tela compartilhada com a tela grande e a câmera à direita; só câmera no bloco centralizado; nada da tela cortado;
- fim: acaba na última fala, sem silêncio;
- volume (≈ -16 LUFS) e duração coerente.

No fim, uma tabela: treinamento (arquivo em `<treinos>/prontos/`), duração, quanto saiu de erro, nota e observação.
