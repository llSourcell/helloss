
import pytest
import mne
import os
import numpy as np
from neuro_analyst.cleaning import clean
from neuro_analyst.io import load

@pytest.fixture(scope="session")
def sample_eeg_filepath(tmpdir_factory):
    """Fixture to get the path to a sample EEG file from MNE."""
    sample_data_folder = mne.datasets.sample.data_path()
    sample_fif_file = os.path.join(sample_data_folder, 'MEG', 'sample', 'sample_audvis_raw.fif')
    # Use a temporary directory for the test file
    temp_dir = tmpdir_factory.mktemp("data")
    new_filepath = os.path.join(str(temp_dir), "test_raw.fif")
    raw = mne.io.read_raw_fif(sample_fif_file, preload=True)
    raw.pick_types(meg=False, eeg=True, stim=True, eog=True) # Pick only EEG and EOG channels for simplicity
    raw.save(new_filepath, overwrite=True)
    return new_filepath

def test_clean_runs_successfully(sample_eeg_filepath):
    """Tests that the cleaning pipeline runs without crashing and returns a Raw object."""
    raw = load(sample_eeg_filepath)
    assert raw is not None, "Failed to load the sample file."

    # Make a copy of the original data for comparison
    original_data = raw.get_data()

    # Run the cleaning process
    cleaned_raw = clean(raw, generate_report=False) # Disable report for this test

    assert cleaned_raw is not None
    assert isinstance(cleaned_raw, mne.io.BaseRaw)

    # Check that the data has actually been modified
    cleaned_data = cleaned_raw.get_data()
    assert not np.array_equal(original_data, cleaned_data), "Cleaning process did not modify the data."

    # Check that the number of channels is the same
    assert len(raw.ch_names) == len(cleaned_raw.ch_names)
