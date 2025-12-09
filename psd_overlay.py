#!/usr/bin/env python3
"""
overlay_psd_interactive.py
Overlay three PSD Excel files (frequency vs PSD) on one interactive plot.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ------------------------------------------------------------
# User-configurable section
# ------------------------------------------------------------
files = {
    "Still": "Out/BB_still_psd_128k.xlsx",
    "Slow":  "Out/BB_slow_psd_128k.xlsx",
    "Fast":  "Out/BB_fast_psd_128k.xlsx",
}
title = "Baseball Path PSD Speed Comparison"
fmin, fmax = 0, 500       # frequency limits (set to None to disable)
use_log_y = False          # set True for log y-axis
# ------------------------------------------------------------

def load_psd(path: Path):
    """Auto-detect frequency and PSD columns."""
    df = pd.read_excel(path)
    df = df.dropna(axis=1, how='all')
    cols = list(df.columns)
    lower = {c: str(c).lower() for c in cols}

    freq_candidates = [c for c in cols if any(k in lower[c] for k in ["freq", "hz", "f("])]
    psd_candidates  = [c for c in cols if any(k in lower[c] for k in ["psd", "power", "density", "/hz"])]

    num_cols = [c for c in cols if np.issubdtype(df[c].dropna().dtype, np.number)]
    freq_col = freq_candidates[0] if freq_candidates else num_cols[0]
    psd_col  = psd_candidates[0] if psd_candidates else num_cols[1]

    f = pd.to_numeric(df[freq_col], errors='coerce')
    p = pd.to_numeric(df[psd_col],  errors='coerce')
    mask = f.notna() & p.notna()
    f, p = f[mask].to_numpy(), p[mask].to_numpy()
    order = np.argsort(f)
    return f[order], p[order]

# ------------------------------------------------------------
# Load and plot all PSDs
# ------------------------------------------------------------
plt.figure(figsize=(10, 5.5))
for label, fname in files.items():
    f, p = load_psd(Path(fname))
    if fmin is not None or fmax is not None:
        mask = (f >= (fmin or -np.inf)) & (f <= (fmax or np.inf))
        f, p = f[mask], p[mask]
    plt.plot(f, p, label=label)

plt.title(title)
plt.xlabel("Frequency (Hz)")
plt.ylabel("Power Spectral Density")
if use_log_y:
    plt.yscale("log")
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.show()  # opens interactive matplotlib window
