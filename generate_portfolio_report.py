import mne
import neuro_analyst as na
import os

# --- 1. Use the MNE sample dataset ---
print("Using MNE sample dataset...")
sample_data_folder = mne.datasets.sample.data_path()
sample_raw_path = os.path.join(sample_data_folder, 'MEG', 'sample', 'sample_audvis_raw.fif')

# --- 2. Load the raw data ---
print(f"Loading data from: {sample_raw_path}")
raw = mne.io.read_raw_fif(sample_raw_path, preload=True)

# --- 3. Select EEG and EOG channels ---
raw.pick(['eeg', 'eog'])

# --- 4. Clean the data and generate the report ---
print("Running the cleaning pipeline to generate the report...")
print("Channels in raw object before cleaning:", raw.ch_names)
cleaned_raw = na.clean(raw, generate_report=True)

print("\nPortfolio report generated successfully!")
print("The HTML report (na_report_*.html) is the centerpiece of your portfolio.")