import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# Function to compute PSD and plot
def compute_psd_from_xls(file_path, sheet_name, output_file=None):
    # Step 1: Load the time series data from the Excel file
    # Assuming 'Time' is the column with timestamps and 'Magnetometer' is the data
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Check if the columns 'Time' and 'Magnetometer' exist
    if 'Time (s)' not in df.columns or 'Absolute field (µT)' not in df.columns:
        print("Error: The required columns ('Time (s)', 'Absolute field (µT)') are not in the data.")
        return

    # Step 2: Extract the time and magnetometer data
    time = df['Time (s)'].values
    magnetometer_data = df['Absolute field (µT)'].values

    # Step 3: Compute the sampling frequency (assuming uniform time intervals)
    dt = np.mean(np.diff(time))  # Time difference between samples
    fs = 1 / dt  # Sampling frequency

    # Step 4: Compute the Power Spectral Density (PSD) using Welch's method
    # nperseg is the number of points per segment; this can be adjusted
    f, Pxx = signal.welch(magnetometer_data, fs=fs, nperseg=1024)

    # Step 5: Plot the PSD
    plt.figure(figsize=(10, 6))
    plt.semilogy(f, Pxx)
    plt.title('Power Spectral Density of Magnetometer Data')
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Power Spectral Density [V**2/Hz]')
    plt.grid(True)
    plt.show()

    # Step 6: Optionally save the PSD to a new Excel file
    if output_file:
        psd_df = pd.DataFrame({'Frequency [Hz]': f, 'PSD [V**2/Hz]': Pxx})
        psd_df.to_excel(output_file, index=False)
        print(f"PSD data saved to {output_file}")

# Example usage
file_path = 'magnetometer_data.xlsx'  # Change to your file path
sheet_name = 'Sheet1'  # If your data is in a specific sheet
output_file = 'psd_output.xlsx'  # Optional, specify if you want to save the results

compute_psd_from_xls('Data/Train Home Magnetometer 2025-10-13 14-32-34.xls', 'Raw Data', output_file)
