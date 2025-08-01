
import pytest
import mne
import os
from neuro_analyst.io import load

# MNE includes sample datasets. We can use one for testing.
# This ensures our tests are reproducible and don't depend on local user files.
@pytest.fixture(scope="session")
def sample_eeg_filepath(tmpdir_factory):
    """Fixture to get the path to a sample EEG file from MNE."""
    # Use a temporary directory to avoid cluttering the user's home directory
    temp_dir = tmpdir_factory.mktemp("data")
    sample_data_folder = mne.datasets.sample.data_path()
    sample_fif_file = os.path.join(sample_data_folder, 'MEG', 'sample', 'sample_audvis_raw.fif')
    # For this test, we'll just pretend it's an edf for the sake of the example
    # In a real scenario, we would have actual sample files of each type.
    new_filepath = os.path.join(str(temp_dir), "test.fif")
    # Create a dummy file for the test
    mne.io.read_raw_fif(sample_fif_file).save(new_filepath, overwrite=True)
    return new_filepath

def test_load_fif_successfully(sample_eeg_filepath):
    """Tests that a valid .fif file is loaded correctly."""
    raw = load(sample_eeg_filepath)
    assert raw is not None
    assert isinstance(raw, mne.io.BaseRaw)

def test_load_unsupported_format():
    """Tests that an unsupported file format returns None."""
    # Create a dummy text file
    filepath = "test.txt"
    with open(filepath, "w") as f:
        f.write("hello")
    raw = load(filepath)
    assert raw is None
    os.remove(filepath)

def test_load_file_not_found():
    """Tests that a non-existent file returns None."""
    raw = load("non_existent_file.edf")
    assert raw is None
