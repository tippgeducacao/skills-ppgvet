# Moldes de prompt (inglês no Flow; explicar ao usuário em português)

Trocar o que está entre `<>`. Sempre conferir o roteiro do pedido: o que ele pede, se segue.

Por que os moldes são assim ([doc do Google para imagem](https://aistudio.google.com/docs/image-generation), conferida em 24/11/2026, e os prompts mais usados do repositório público awesome-nano-banana-pro-prompts):
- Descrever como diretor de fotografia: assunto, lugar, luz (fonte, direção, temperatura), câmera (altura, lente, abertura), composição e acabamento. Adjetivo solto ("bonito", "premium") não guia; número guia.
- Para manter o mascote igual, mandar até 5 imagens dele (corpo e closes) e dizer o que cada imagem é.
- Uma mudança por edição, sempre com "mantenha todo o resto igual".
- A IA nunca escreve marca, rótulo ou texto: logo e texto entram na edição, no computador.
- Toda imagem e vídeo do Google sai com marca d'água invisível (SynthID). Gerar só mascote, produto e cenário fictício, nunca pessoa que pareça aluno, professor ou equipe (`regras/nucleo.md`).

## 1. Cenário · Nano Banana Pro · 9:16 · x2
Anexar: nada (cena anexada prende o ângulo da câmera). Para ter opções, mandar 2 ou 3 cenários
num pedido, um prompt cada, variando luz, hora ou ângulo ("uma imagem para cada, não misture"):
x2 do mesmo prompt sai quase igual.

```
Premium photorealistic CGI render, vertical 9:16, of <lugar do setor, ex.: a modern, bright and clean poultry laboratory>, completely empty of people and animals.
Scene: <fundo com 2 ou 3 detalhes do setor>. In the <posição, ex.: center of the floor / right side of the desk>, <onde o produto vai ficar: an empty white pedestal at waist height / a clear empty area>, where a product will be placed. Clear empty floor space on the <left/right>, where a character about <1 m> tall will stand.
Lighting: <fonte e direção, ex.: soft daylight from large windows on the left>, about <5600> K, soft shadows, gentle reflections on the floor, <clima: bright and cheerful / warm and cozy>.
Camera: eye level, frontal <medium-wide> shot, 35 mm cinema lens, f/4, static, the whole <floor / desk> visible, the empty spots in the lower two thirds of the frame and open space above.
Color grading: rich but natural colors, clean commercial look.
Avoid: people, animals, any text, letters, logos or signage on walls or objects, cartoon look.
```
- Âncora de escala no cenário (pedestal na altura da cintura, mesa) evita mascote do tamanho do produto.
- Espaço livre para o produto e para o mascote LADO A LADO, nunca um na frente do outro.
- Quer mudar altura/ângulo? Descrever em números ("a crane about 4 meters high, looking down at 20 degrees"), sem anexar a cena antiga.

## 2. Produto sem foto boa · Nano Banana Pro
A IA nunca escreve a marca. Gerar a embalagem lisa; o Claude aplica a logo verdadeira (mockup).
```
Premium studio product photograph of <tipo: a 15 kg laminated stand-up feed bag / a glass vaccine vial>, front view, standing upright, on a pure white seamless background. Design: <cores e formas tiradas do material da marca>; the large center area of the front is plain and completely empty, reserved for a logo. Lighting: soft three-point studio light, gentle shadow under it, realistic material. Camera: straight front view, 85 mm lens, the whole product visible with space around it.
Avoid: any text, letters, numbers, logos or symbols; extra products; people; cartoon look.
```

## 3. Editar uma imagem (sem perder a original)
Começo obrigatório: editar no Flow substitui a imagem.
```
Crie uma imagem nova a partir da imagem 1; não substitua nem altere a original, mantenha as duas.
Using the provided image, change only <X> to <Y>. Keep everything else in the image exactly the same, preserving the original style, lighting and composition.
```
Uma edição por vez. Letra pequena piora a cada edição: logo e texto o Claude troca aqui.

## 4. Vídeo · Veo 3.1 Quality · 9:16 · x2 · 3 elementos
Anexar nesta ordem: 1) cenário · 2) folha do mascote · 3) produto.

```
Crie 2 versões deste vídeo vertical 9:16, usando as 3 imagens anexadas como referências dos elementos (não como quadro inicial nem final): imagem 1 = o cenário, imagem 2 = o mascote (à esquerda o corpo inteiro; à direita, closes de detalhes do MESMO personagem), imagem 3 = o produto.

Setting (image 1): the same <lugar>, exactly as image 1: <3 ou 4 detalhes que precisam ficar>. No other people or animals.

Character (image 2): <bloco do mascote, seção 6>. The close-ups on the right of image 2 only show details of this same character; they never appear as separate objects. He looks exactly like image 2 in every frame. <posição: he stands on the floor to the LEFT of the <produto>, side by side, a clear gap as wide as his own body between them, on the same ground line, the top of his head at about <âncora visível>; neither behind nor in front of it>.

<Produto> (image 3): one <produto> exactly like image 3, <cores e texto principal>, sharp and unchanged. <Onde fica / como chega>. It stays fully visible, label facing the camera, never covered by the character.

Premium photorealistic CGI commercial, rendered like a high-end 3D animation film: physically based materials, global illumination, soft natural shadows, <material do mascote: fine individual feathers / subsurface scattering on the pink skin and ears, fine hairs>, <material do produto: realistic glass with refractions / realistic plastic with soft reflections>, gentle depth of field, rich but natural color grading, lively, natural and expressive motion, one continuous shot.
Static camera for the whole shot, locked off on a tripod: the camera never moves, never zooms, never pans; the framing stays exactly the same from the first to the last frame.
[00:00-00:02] <uma ação>
[00:02-00:04] <uma ação>
[00:04-00:06] <uma ação; olhar com DIREÇÃO: "lowers his head toward the bag… his eyes point down at it">
[00:06-00:08] <gesto final: vira para a câmera, sorri e acena com o membro de FORA (lado oposto ao produto), "exactly like the <pose> in image 2"; o outro fica parado; "he stays in the same spot, does not walk or turn toward the <produto>">

Audio: the soundtrack contains only <ambiente: a quiet room tone / a soft breeze> and these sound effects: SFX: <som 1> at 00:0X, <som 2> at 00:0Y. The whole clip has no musical instruments, no melody, no voices and no animal sounds.
```
- Fast só para testar o prompt; Quality na versão que vai para a edição.
- Uma ação por trecho de 2 s. Ação demais num trecho = bagunça.
- Descrever o que existe, não o que não existe (exceto a linha final do áudio, que funciona).

## 5. Corrigir um detalhe · Omni 1.1 Flash (modo edição)
Anexar: 1) o vídeo ORIGINAL do Flow (nunca o editado pelo Claude) · 2) a folha com o detalhe certo
(ou um close só dele).
```
Edit the attached video. Keep everything exactly the same: the timing, every movement, the camera, the framing, the light, the colors, the product and the sound. Change only <o erro, ex.: his right arm from 00:05 to 00:08: it must end in a white feathered wing exactly like image 2, never a hand>.
```
Funcionou num vídeo de O Aviário (asa que virou mão voltou a ser asa, o resto igual, até o áudio). O Claude
confere quadro a quadro se só aquilo mudou.

## 6. Bloco do mascote (Character)
Escrever "a <bicho> standing upright like a person, wearing a white space suit" e **nunca
"astronaut"** quando ele está sem capacete (a palavra puxa capacete de vidro).

**SuinoCast (porco)**
```
a young pink pig standing upright like a person, about one meter tall, with a realistic pig face exactly like image 2 (not a cartoon face), the same open smile as image 2 frozen, his jaw never moves and he is completely silent; pink ears with brown spots; a white space suit with a Brazilian flag patch on one shoulder and the small SuinoCast patch on the chest box, only the small patches shown in image 2, no large lettering anywhere on the suit. All four limbs end in real pig trotters with cloven hooves exactly like the close-ups in image 2: pink skin with fine hairs, two large toes with dark brown tips; no fingers, no thumbs, no human hands, no shoes. He holds his helmet under his left arm the whole time.
```
Aceno do porco: "he raises his right arm beside his head, lifting the sleeve of his suit; the trotter at the end of this arm waves gently from the wrist; both legs stay on the ground" (falar "foot" ou "front trotter" fez ele levantar a perna).

**O Aviário (galinha)**
```
a white hen standing upright like a person, with a red comb and wattles, a yellow beak and a white feathered face, wearing a white space suit with a Brazilian flag patch on one shoulder and the small "o aviário podcast" logo on the chest box exactly as in image 2 (never PPGVET, no large lettering anywhere on the suit). His head is bare and uncovered: comb and neck feathers in the open air, coming out of the empty metal collar ring; never any helmet, glass dome, bubble or visor. His arms end in soft white feathered WINGS exactly like image 2, never hands, never fingers, never gloves. Yellow chicken feet. His beak stays still; he never talks and is completely silent.
```
Aceno da galinha: "waves one open wing: the wing rises beside his head and the white feathers spread and wave gently, never like a hand or a glove".

**+Rúmen e PetFood**: escrever o bloco na 1ª vez, a partir do mascote (o que termina cada membro,
patches, capacete), e guardar aqui.
