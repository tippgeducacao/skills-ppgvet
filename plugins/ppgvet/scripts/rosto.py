"""Melhora rostos de uma foto com GFPGAN v1.4 (devolve 2x). Roda com o Python do GFPGAN: use imagem.py rosto."""
import sys
from pathlib import Path
import cv2
from gfpgan import GFPGANer

entrada, saida = sys.argv[1], sys.argv[2]
img = cv2.imread(entrada, cv2.IMREAD_COLOR)
assert img is not None, f"não abriu {entrada}"
r = GFPGANer(model_path=str(Path.home() / ".ppgvet" / "gfpgan" / "GFPGANv1.4.pth"),
             upscale=2, arch="clean", channel_multiplier=2, bg_upsampler=None)
_, rostos, final = r.enhance(img, has_aligned=False, only_center_face=False, paste_back=True)
assert final is not None, "nenhum rosto encontrado"
cv2.imwrite(saida, final)
print(f"{len(rostos)} rosto(s) -> {saida}")
