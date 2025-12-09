import matplotlib.pyplot as plt

# Data points
x = [0, 1.2, 2.0]  # walking speed (m/s)
y = [4.0634e-11, 2.7049e-11, 2.39935e-11]  # PSD power (1/Hz)

# Create plot
plt.figure(figsize=(7, 5))
plt.plot(x, y, marker='o', linestyle='-', linewidth=2, markersize=8)

# Labels and title
plt.title("Walking Speed vs PSD Power at 15.5 Hz Peak", fontsize=14)
plt.xlabel("Estimated Walking Speed (m/s)", fontsize=12)
plt.ylabel("PSD Power at 15.5 Hz (1/Hz)", fontsize=12)

# Optional grid and layout
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()

# Show or save
plt.show()
# plt.savefig("walking_speed_vs_power.png", dpi=300)
