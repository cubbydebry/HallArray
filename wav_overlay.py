import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile

# --- Edit these paths ---
wav_paths = [
    "Data/SMBB-WEB_fast_200Hz.wav",
    "Data/SMBB-WEB_slow_200Hz.wav",
    "Data/SMBB-WEB_still_200Hz.wav"
]

# --- Load and plot ---
fig, axes = plt.subplots(len(wav_paths), 1, figsize=(10, 6), sharex=True)

for i, path in enumerate(wav_paths):
    sr, data = wavfile.read(path)
    # Convert to mono if stereo
    if data.ndim > 1:
        data = data.mean(axis=1)
    t = np.arange(len(data)) / sr
    axes[i].plot(t, data, linewidth=0.8)
    axes[i].set_ylabel(f"{path}")
    axes[i].grid(True, alpha=0.3)

axes[-1].set_xlabel("Time (s)")
plt.tight_layout()
plt.show()
