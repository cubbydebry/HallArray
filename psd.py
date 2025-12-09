import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from tkinter import Tk, filedialog, Button, Label
from tkinter.ttk import Combobox

# Function to compute PSD and plot
def compute_psd_from_xls(file_path, sheet_name, time_column, magnetometer_column, output_file=None):
    # Step 1: Load the time series data from the Excel file
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Check if the specified columns exist
    if time_column not in df.columns or magnetometer_column not in df.columns:
        print(f"Error: The required columns ('{time_column}', '{magnetometer_column}') are not in the data.")
        return

    # Step 2: Extract the time and magnetometer data
    time = df[time_column].values
    magnetometer_data = df[magnetometer_column].values

    # Step 3: Compute the sampling frequency (assuming uniform time intervals)
    dt = np.mean(np.diff(time))  # Time difference between samples
    fs = 1 / dt  # Sampling frequency

    # Step 4: Compute the Power Spectral Density (PSD) using Welch's method
    f, Pxx = signal.welch(magnetometer_data, fs=fs, nperseg=1024)

    # Step 5: Plot the raw data on its own figure
    fig1, ax1 = plt.subplots(figsize=(12, 6))

    # Plot the raw data on the first figure
    ax1.plot(time, magnetometer_data, color='tab:blue', label='Raw Magnetometer Data')
    ax1.set_ylabel(f'{magnetometer_column} (µT)', color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.set_title('Magnetometer Raw Data')
    ax1.set_xlabel('Time (s)')

    # Explicitly set the xlim to display all the data in the top plot
    ax1.set_xlim([time[0], time[-1]])  # Show the full time range
    ax1.grid(True)

    # Add scale markings to the top plot
    ax1.xaxis.set_major_locator(plt.MaxNLocator(integer=True, prune='both'))  # Integer ticks for time
    ax1.yaxis.set_major_locator(plt.MaxNLocator(integer=True))  # Integer ticks for y-axis

    # Show the first plot
    plt.show()

    # Step 6: Plot the PSD on a separate subplot (bottom plot)
    fig2, ax2 = plt.subplots(figsize=(12, 6))

    # Plot the PSD on the second figure
    ax2.semilogy(f, Pxx, color='tab:orange', label='Power Spectral Density')

    # Dynamically set the xlim to show a zoomed-in frequency range
    max_freq = f[-1]  # Maximum frequency from the PSD
    zoom_limit = min(max_freq, 100)  # Set a reasonable zoom limit (e.g., 0-100 Hz, or the maximum frequency)
    ax2.set_xlim(0, zoom_limit)  # Zoom in to 0 - 100 Hz or adjust depending on your data

    # Ensure the PSD plot fills up the window
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('Power Spectral Density [V**2/Hz]', color='tab:orange')
    ax2.tick_params(axis='y', labelcolor='tab:orange')
    ax2.set_title('Power Spectral Density')

    # Adjust y-axis for better visualization of the log scale
    ax2.set_ylim([min(Pxx), max(Pxx)])  # Ensure the y-axis shows the full range of the PSD

    # Add scale markings to the bottom plot
    ax2.xaxis.set_major_locator(plt.MaxNLocator(integer=True, prune='both'))  # Integer ticks for frequency
    ax2.yaxis.set_major_locator(plt.LogLocator(base=10.0, subs='auto', numticks=10))  # Log scale for PSD

    ax2.grid(True)
    plt.tight_layout()

    # Show the second plot
    plt.show()

    # Step 7: Optionally save the PSD to a new Excel file
    if output_file:
        psd_df = pd.DataFrame({'Frequency [Hz]': f, 'PSD [V**2/Hz]': Pxx})
        psd_df.to_excel(output_file, index=False)
        print(f"PSD data saved to {output_file}")

# Function to open a file dialog and select the Excel file, sheet, and columns
def select_file_and_columns():
    # Initialize Tkinter window
    root = Tk()
    root.withdraw()  # Hide the root window initially

    # Step 1: Open file dialog to choose the Excel file
    file_path = filedialog.askopenfilename(
        title="Select the Excel file",
        filetypes=[("Excel files", "*.xls"), ("Excel files", "*.xlsx")]
    )
    if not file_path:
        print("No file selected. Exiting.")
        return

    # Step 2: Read the Excel file to get the sheet names
    xls = pd.ExcelFile(file_path)
    sheet_names = xls.sheet_names

    # Show the Tkinter window for dropdown selection
    root.deiconify()

    # Step 3: Add a label and dropdown for sheet selection
    sheet_label = Label(root, text="Select Sheet:")
    sheet_label.pack(padx=10, pady=5)
    sheet_name_var = Combobox(root, values=sheet_names)
    sheet_name_var.set(sheet_names[0])  # Set default value to the first sheet
    sheet_name_var.pack(padx=10, pady=5)

    # Step 4: Read the selected sheet to get the columns
    df = pd.read_excel(file_path, sheet_name=sheet_name_var.get())
    columns = df.columns.tolist()

    # Step 5: Add labels and dropdowns for time and magnetometer columns
    time_label = Label(root, text="Select Time Column:")
    time_label.pack(padx=10, pady=5)
    time_column_var = Combobox(root, values=columns)
    time_column_var.set(columns[0])  # Set default value to the first column
    time_column_var.pack(padx=10, pady=5)

    magnetometer_label = Label(root, text="Select Magnetometer Column:")
    magnetometer_label.pack(padx=10, pady=5)
    magnetometer_column_var = Combobox(root, values=columns)
    magnetometer_column_var.set(columns[1])  # Set default value to the second column
    magnetometer_column_var.pack(padx=10, pady=5)

    # Step 6: Submit button to proceed
    def on_submit():
        sheet_name = sheet_name_var.get()
        time_column = time_column_var.get()
        magnetometer_column = magnetometer_column_var.get()

        # Ask the user for the output file name (optional)
        output_file = filedialog.asksaveasfilename(title="Save PSD Data", defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])

        # Call the function to compute and plot PSD
        compute_psd_from_xls(file_path, sheet_name, time_column, magnetometer_column, output_file)

        root.destroy()  # Destroy the Tkinter window after submission

    # Submit button
    submit_button = Button(root, text="Submit", command=on_submit)
    submit_button.pack(padx=10, pady=10)

    # Run the Tkinter event loop
    root.mainloop()

# Run the file selector
select_file_and_columns()
