import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import re


# ==== Config ====
PORT = "/dev/tty.usbmodem14201"   # Change to serial port
BAUD = 115200           # Change to baud rate
SAVE_FILE = "hall_data.csv"

# ==== INIT ====
ser = serial.Serial(PORT, BAUD)
time.sleep(2) # Wait for connection

values = []
timestamps = []

# Plot Setup
fig, ax = plt.subplots()
line, = ax.plot([], [], lw=1)
ax.set_ylim(0, 3500)
ax.set_xlim(0, 100)
ax.set_xlabel("Sample")
ax.set_ylabel("Voltage (mV)")
ax.set_title("Hall Sensor Live Data")

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


    # Plot only last 100 samples
    if len(values) > 100:
        values = values[-100:]
        timestamps = timestamps[-100:]

    line.set_data(range(len(values)), values)
    return line,

ani = animation.FuncAnimation(fig, update, interval=100, cache_frame_data=False)
plt.show()

ser.close()
