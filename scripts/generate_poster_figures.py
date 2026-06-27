# -*- coding: utf-8 -*-
"""Generate/copy final high-severity figures for the poster."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_FIG = ROOT / "outputs" / "figuras"
POSTER_FIG = ROOT / "relatorios" / "poster" / "figuras"
POSTER_FIG.mkdir(parents=True, exist_ok=True)

POSTER_FILES = [
    "01_distribuicao_desfecho.png",
    "02_cramers_v_desfecho.png",
    "02_heatmap_temporal_gravidade.png",
    "05_scatter_suporte_confianca_alta.png",
    "07_estratos_uso_solo.png",
    "08_mineracao_por_ano.png",
    "09_comparacao_alta_baixa_fatal.png",
    "10_cobertura_regras.png",
]


def main():
    subprocess.run([sys.executable, str(ROOT / "scripts" / "generate_figures.py")], check=True)
    for name in POSTER_FILES:
        src = OUT_FIG / name
        if not src.exists():
            raise FileNotFoundError(src)
        shutil.copy2(src, POSTER_FIG / name)
        print(f"[OK] {name}")
    print("[OK] Figuras finais do poster atualizadas.")


if __name__ == "__main__":
    main()
