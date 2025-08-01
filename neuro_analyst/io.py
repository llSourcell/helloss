import mne
from typing import Union

def load(filepath: str) -> Union[mne.io.Raw, None]:
    """
    Smartly loads EEG data from various file formats.

    This function automatically detects the file type based on its extension
    and uses the appropriate MNE-Python function to load the data.

    Args:
        filepath (str): The absolute or relative path to the EEG data file.

    Returns:
        mne.io.Raw | None: An MNE Raw object if successful, otherwise None.

    Supported Formats:
        - .edf (European Data Format)
        - .bdf (BioSemi Data Format)
        - .fif (Elekta Neuromag)
        - .set (EEGLAB)
    """
    try:
        if filepath.endswith('.edf'):
            return mne.io.read_raw_edf(filepath, preload=True)
        elif filepath.endswith('.bdf'):
            return mne.io.read_raw_bdf(filepath, preload=True)
        elif filepath.endswith('.fif'):
            return mne.io.read_raw_fif(filepath, preload=True)
        elif filepath.endswith('.set'):
            return mne.io.read_raw_eeglab(filepath, preload=True)
        else:
            print(f"Error: Unsupported file format for: {filepath}")
            print("Supported formats are: .edf, .bdf, .fif, .set")
            return None
    except FileNotFoundError:
        print(f"Error: File not found at: {filepath}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while loading {filepath}: {e}")
        return None