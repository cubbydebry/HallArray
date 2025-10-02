import numpy as np
import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import re


# ==== Config ====
PORT = "/dev/tty.usbmodem14101"     # Change to serial port
BAUD = 115200                       # Change to baud rate
SAVE_FILE = "hall_data.csv"
PSD_FILE = "hall_psd.csv"
k = 30      # sensitivity mV per mT, 30 for A2 @3.3v, 60 for A1 @3.3v
N = 512     # buffer size for PSD
fs = 10.0   # sampling frequency in Hz

# ==== INIT ====
ser = serial.Serial(PORT, BAUD)
time.sleep(2) # Wait for connection

values = []
timestamps = []

# ==== PLOT ====
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8,6))
line_ts, = ax1.plot([], [], lw=1)
line_psd, = ax2.plot([], [], lw=1)

ax1.set_xlabel("Sample")
ax1.set_ylabel("B (Tesla)")
ax1.set_title("Hall Sensor Time Series")

ax2.set_title("Hall Sensor PSD")
ax2.set_xlabel("Frequency (Hz)")
ax2.set_ylabel("PSD (T^2/Hz)")
ax2.set_xscale("linear")
ax2.set_yscale("linear")
tiny = np.finfo(float).tiny
line_psd.set_data([1.0], [tiny])
ax2.set_xlim(0.9, 1.1)
ax2.set_ylim(tiny, 10 * tiny)

def update(frame):
    global values, timestamps

    while ser.in_waiting:
        line_bytes = ser.readline().decode("utf-8", errors="ignore").strip()
        match = re.search(r"Voltage:\s*(\d+)", line_bytes)
        if match:
            val = int(match.group(1))
            values.append(val)
            timestamps.append(time.time())

            # save line
            with open(SAVE_FILE, "a") as f:
                f.write(f"{timestamps[-1]},{val}\n")

    # Time series plot
    x = np.arange(len(values[-N:]))
    y = np.array(values[-N:])
    line_ts.set_data(x, y)
    ax1.set_xlim(0, N)
    y_lo, y_hi = float(y.min()), float(y.max())
    if np.isclose(y_lo, y_hi):
        pad = 1e-12
        y_lo -= pad; y_hi += pad;
    ax1.set_ylim(y_lo, y_hi)

    if len(values) < N/4:
        return line_ts, line_psd

    # Welch PSD
    B_T = np.array(values[-N:], dtype=float) / (k * 1000.0)
    nseg = min(256, (B_T.size // 2) * 2)
    if nseg < 16:
        return line_ts, line_psd
    
    f, Pxx = welch_psd(B_T, fs=fs, nperseg=nseg, overlap=0.5)
    if f.size > 1:
        # keep positive frequencies only
        mask = np.isfinite(f) & np.isfinite(Pxx) & (f > 0)
        if not np.any(mask):
            return line_ts, line_psd
        
        f_plot = f[mask]
        P_plot = Pxx[mask]
        
        eps = np.finfo(float).tiny
        P_plot = np.clip(P_plot, eps, None)

        line_psd.set_data(f_plot, P_plot)

        ax2.set_xlim(f_plot[0], f_plot[-1])

        p5 = np.percentile(P_plot, 5)
        med = np.median(P_plot)
        y_lo = max(p5, med * 1e-2, eps)
        y_hi = P_plot.max()
        if not np.isfinite(y_hi) or y_hi <= y_lo:
            y_hi = y_lo * 10
        ax2.set_ylim(y_lo, y_hi)

        if ax2.get_xscale() != "log":
            ax2.set_xscale("log")
        if ax2.get_yscale() != "log":
            ax2.set_yscale("log")

        np.savetxt(PSD_FILE, np.column_stack([f_plot, P_plot]),
                   delimiter=",", 
                   header="Frequency (Hz),PSD (T^2/Hz)", 
                   comments='' )
        
        return line_ts, line_psd
    
def welch_psd(x, fs, nperseg=256, overlap=0.5):
    step = int(nperseg * (1 - overlap))
    if len(x) < nperseg or step <= 0:
        return np.array([]), np.array([])
    window = np.hanning(nperseg)
    U = (window**2).sum()
    Pxx = []
    for i in range(0, len(x)-nperseg+1, step):
        seg = x[i:i+nperseg] - np.mean(x[i:i+nperseg])
        X = np.fft.rfft(seg * window)
        P = (np.abs(X)**2) / (fs * U) * 2.0
        Pxx.append(P)
    if not Pxx:
        return np.array([]), np.array([])
    Pxx = np.mean(Pxx, axis=0)
    if nperseg % 2 == 0:
        Pxx[0] /= 2; Pxx[-1] /= 2
    else:
        Pxx[0] /= 2
    f = np.fft.rfftfreq(nperseg, 1/fs)
    return f, Pxx

ani = animation.FuncAnimation(fig, update, interval=100, cache_frame_data=False)
plt.show()

ser.close()
