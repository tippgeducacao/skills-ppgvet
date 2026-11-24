# Vídeo: técnica, motion e Instagram

Lido pelas skills de vídeo, junto com o `nucleo.md`.

## Técnica
- **Corte:** na fronteira da palavra (~60 ms antes, ~100 ms depois), com fade de áudio de 30 ms. Silêncio longo vira uma pausa curta.
- **Cor:**
  - iPhone HDR (`arib-std-b67`/`smpte2084`): converter para BT.709 antes de misturar, com `zscale=t=linear:npl=520,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,eq=gamma=1.06`;
  - etiquetar toda saída com `-colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv`.
- **Áudio da câmera:** medir cada canal (`"$FF" -i X -af "pan=mono|c0=c0,volumedetect" -f null -` e depois `c1`). A câmera Sony grava o microfone só num lado; se um lado estiver mudo (~-80 dB), duplicar o canal bom.
- **Ruído na voz** (zumbido, ar-condicionado, sala): `"$PY" "$S/limpar_voz.py" base.mov voz.wav` (DeepFilterNet 3, local) e mixar essa voz no lugar do áudio original. Só quando o ruído incomoda. Antes do lote, gerar uma prévia de um trecho (antes e depois) para a pessoa ouvir.
- **Câmera que se mexe** (zoom lento, soco, pan, seguir rosto): sempre em fração de pixel, nunca com o `zoompan` do ffmpeg (ele arredonda a posição e o movimento treme, chega a andar para trás). No ffmpeg, `perspective` com `eval=frame` (molde: `zoom_suave` do `post.py`); em quadros, `cv2.warpAffine` com `INTER_CUBIC` (molde: `patrocinador_final.py`).
  - **Seguir rosto (tracking):** nunca a posição crua do detector (vibra junto com o erro dele). Zona morta de ~6% da largura (a câmera fica parada enquanto a pessoa mexe pouco) e suavização de ~0,8 s, como um operador que acompanha com atraso (0,4 s ainda dá tranco com palestrante andando no palco; medido em 24/11/2026). Medida de aceite: nenhum quadro parado no meio do movimento e a 2ª diferença da trilha até ~0,25 px por quadro (0,05 só com a pessoa quase parada).
  - **Posição por quadro:** calcular o recorte para cada quadro de saída, nunca por tempo (`sendcmd`): com a fonte a 30 qps e a saída a 29,97, alguns quadros perdem a atualização e a câmera trava.
- **Volume:** voz a -16 LUFS. A música fica fixa e baixa sob a voz, do começo ao fim, com entrada suave, e **sobe** na logo ou no CTA final (a vinheta perde o som próprio). Os scripts já fazem a mixagem, cada um no seu padrão: Reels com fundo a -33 LUFS (17 dB abaixo da voz) e -15,5 LUFS na vinheta; posts de cortes com fundo a ~-35 LUFS; chamada com final a ~-14 LUFS. Nunca subir o fundo acima disso; na dúvida, mais baixo.

## Motion (textos e cartões animados)
- Texto na tela, cartões e inserções são animados no HyperFrames, em nível profissional e na identidade da marca. PNG com fade no ffmpeg não basta.
- Curvas, durações e coreografia: `oficio/motion.md`. Nada cobre nem encosta no rosto. O corte e a fala continuam no ffmpeg.
- **O roteiro do motion entra no plano** (cada texto, cartão e caixinha, com o momento): aprovado o plano, renderizar direto. Na revisão do fim, oferecer o Studio do HyperFrames no navegador para ajuste fino. Na nota, entram também ritmo, leitura e marca.
- Animação de motion design do zero (explicativo, história): plugin **animate**.

## Padrão Instagram vertical (Reels e Stories)
- **Arquivo:** 1080x1920 (9:16), MP4 H.264 + AAC (até 48 kHz, 128 kbps), fps fixo entre 23 e 60 (30, ou o da câmera, como 29,97), `-movflags +faststart`, vídeo até 25 Mbps, de 3 s a 15 min, até 300 MB. Doc oficial da Meta, conferida em 13/11/2026: [IG User Media](https://developers.facebook.com/documentation/instagram-platform/instagram-graph-api/reference/ig-user/media) e [Reels Publishing API](https://developers.facebook.com/documentation/video-api/guides/reels-publishing).
- **Prévia no feed** = recorte 4:5 central (y 285 a 1635). Rosto, texto e logo ficam dentro dele.
- **Margem livre:** nenhum texto nem logo nos 250 px de cima e nos 250 px de baixo.
- **Anúncio pago** (zona segura da Meta): além disso, 14% de cima, 35% de baixo e 6% dos lados sem texto nem logo. Vídeo orgânico não precisa.
- **Faixas dos Reels** (o `hf.py` já usa), de cima para baixo: rosto até ~y 900; legenda no peito, logo abaixo do queixo (topo em y 915), com contorno escuro; caixinha e cartões de y 1035 a ~1390; logo com 210 px de largura, de y 1470 a 1604. A chamada e os posts de cortes têm o layout deles (está em cada skill).
- **Ritmo dos Reels:** o zoom muda no máximo a cada 5 s; os outros cortes ficam como jump cut no mesmo plano.
