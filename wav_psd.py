import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal
from scipy.io import wavfile
from tkinter import Tk, filedialog, Button, Label
from tkinter.ttk import Combobox
from matplotlib.ticker import MaxNLocator, LogLocator

# --- Helpers ---

def _to_float32(x: np.ndarray) -> np.ndarray:
    """
    Convert common WAV dtypes to float32 in approximately [-1, 1].
    Falls back to unit-norm scaling if dtype is unusual.
    """
    if np.issubdtype(x.dtype, np.floating):
        return x.astype(np.float32)
    if x.dtype == np.int16:
        return x.astype(np.float32) / 32768.0
    if x.dtype == np.int32:
        return x.astype(np.float32) / 2147483648.0
    if x.dtype == np.uint8:
        return (x.astype(np.float32) - 128.0) / 128.0
    # Fallback: scale by max abs to avoid division by zero
    max_abs = float(np.max(np.abs(x))) or 1.0
    return x.astype(np.float32) / max_abs

# --- Core PSD function for WAV ---

def compute_psd_from_wav(
    file_path: str,
    channel_idx: int = 0,
    output_file: str | None = None,
    nperseg: int = 128000,
    zoom_hz: float = 5000.0
) -> None:
    """
    Load one channel from a WAV file and compute/plot its PSD using Welch's method.
    Optionally save PSD to .xlsx or .csv.
    """
    # Step 1: Read the WAV
    fs, data = wavfile.read(file_path)           # fs in Hz, data shape: (N,) or (N, C)
    data = _to_float32(data)

    # Step 2: Select one channel
    if data.ndim == 1:
        channel_data = data
        ch_label = "Mono"
    else:
        n_channels = data.shape[1]
        channel_idx = int(np.clip(channel_idx, 0, n_channels - 1))
        channel_data = data[:, channel_idx]
        ch_label = f"Channel {channel_idx} of {n_channels}"

    # Step 3: Build a time axis from the WAV sample rate
    time = np.arange(len(channel_data), dtype=np.float64) / fs

    # Step 4: Compute the PSD with Welch
    seg = int(min(nperseg, len(channel_data)))
    if seg < 256:
        seg = max(64, seg)  # keep a small but valid segment size
    noverlap = seg // 2

    f, Pxx = signal.welch(
        channel_data,
        fs=fs,
        window="hann",
        nperseg=seg,
        noverlap=noverlap,
        detrend="constant",
        scaling="density",  # PSD units: amplitude^2/Hz; here amplitude is normalized
        average="mean",
    )

    # Step 5: Plot raw waveform
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(time, channel_data, label=f'Raw Audio ({ch_label})')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Amplitude (normalized)')
    ax1.set_title(os.path.basename(file_path))
    ax1.xaxis.set_major_locator(MaxNLocator(integer=True, prune='both'))
    ax1.grid(True)
    fig1.tight_layout()
    plt.show()

    # Step 6: Plot PSD
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    ax2.semilogy(f, Pxx, label='Power Spectral Density')
    max_freq = f[-1]  # Nyquist
    zoom_limit = min(max_freq, float(zoom_hz))
    ax2.set_xlim(0, zoom_limit)

    # Safe y-lims for log scale
    positive = Pxx[Pxx > 0]
    if positive.size:
        ax2.set_ylim(positive.min(), positive.max())

    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('PSD [1/Hz]')  # amplitude is normalized; so unit^2/Hz -> 1/Hz
    ax2.set_title(f'PSD — {ch_label}')
    ax2.xaxis.set_major_locator(MaxNLocator(integer=True, prune='both'))
    ax2.yaxis.set_major_locator(LogLocator(base=10.0, numticks=10))
    ax2.grid(True, which='both')
    fig2.tight_layout()
    plt.show()

    # Step 7: Optional export
    if output_file:
        psd_df = pd.DataFrame({'Frequency [Hz]': f, 'PSD [1/Hz]': Pxx})
        ext = os.path.splitext(output_file)[1].lower()
        if ext == ".csv":
            psd_df.to_csv(output_file, index=False)
        else:
            # Default to .xlsx if not CSV
            if ext != ".xlsx":
                output_file = os.path.splitext(output_file)[0] + ".xlsx"
            psd_df.to_excel(output_file, index=False)
        print(f"PSD data saved to {output_file}")

# --- Tkinter: pick WAV + channel ---

def select_wav_and_channel():
    # Initialize Tkinter window
    root = Tk()
    root.withdraw()  # Hide initially

    # Step 1: Choose WAV
    file_path = filedialog.askopenfilename(
        title="Select a WAV file",
        filetypes=[("WAV files", "*.wav")]
    )
    if not file_path:
        print("No file selected. Exiting.")
        return

    # Peek to determine channel count
    try:
        fs, data = wavfile.read(file_path)
    except Exception as e:
        print(f"Could not read WAV: {e}")
        return

    # Build channel list
    if data.ndim == 1:
        channel_options = ["Mono (0)"]
    else:
        n_channels = data.shape[1]
        # Friendly names for first few channels; falls back to Ch N
        names = ["Left", "Right", "Center", "LFE", "Rear Left", "Rear Right"]
        channel_options = []
        for i in range(n_channels):
            label = names[i] if i < len(names) else f"Ch {i}"
            channel_options.append(f"{label} ({i})")

    # Show UI
    root.deiconify()
    Label(root, text="Select Channel:").pack(padx=10, pady=(10, 5))
    channel_var = Combobox(root, values=channel_options, state="readonly")
    channel_var.set(channel_options[0])
    channel_var.pack(padx=10, pady=5)

    def on_submit():
        sel = channel_var.get()
        # parse index inside parentheses
        idx = int(sel.split("(")[-1].rstrip(")"))
        output_file = filedialog.asksaveasfilename(
            title="Save PSD Data",
            defaultextension=".xlsx",
            filetypes=[("Excel file", "*.xlsx"), ("CSV file", "*.csv")]
        )
        compute_psd_from_wav(file_path, channel_idx=idx, output_file=output_file)
        root.destroy()

    Button(root, text="Generate PSD", command=on_submit).pack(padx=10, pady=10)
    root.mainloop()

# Run the selector
if __name__ == "__main__":
    select_wav_and_channel()
