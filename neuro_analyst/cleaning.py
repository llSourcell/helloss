import mne
import numpy as np
from mne.preprocessing import ICA, create_eog_epochs
from mne.time_frequency import psd_array_welch

from .reporting import generate_html_report
from .utils import get_default_config

def _find_emg_components(ica, raw, emg_threshold):
    """
    Finds EMG artifacts by analyzing the frequency spectrum of ICA components.

    This method identifies components with unusually high power in the typical
    EMG frequency range (30-100 Hz).

    Args:
        ica (mne.preprocessing.ICA): The fitted ICA object.
        raw (mne.io.Raw): The raw data, used to get the ICA sources.
        emg_threshold (float | str): The z-score threshold to use for identifying
                                     EMG components. If 'auto', a default of 2.0 is used.

    Returns:
        tuple[list, list]: A tuple containing the indices of the identified EMG
                           components and their corresponding z-scores.
    """
    sources = ica.get_sources(raw).get_data()
    sfreq = raw.info['sfreq']

    # Compute PSD for each component
    psds, freqs = psd_array_welch(sources, sfreq=sfreq, fmin=1, fmax=100, n_fft=int(sfreq))

    # Calculate power in the EMG frequency band
    emg_band = (freqs >= 30) & (freqs <= 100)
    emg_power = np.mean(psds[:, emg_band], axis=1)

    # Identify components with high power using a z-score
    z_scores = (emg_power - np.mean(emg_power)) / np.std(emg_power)

    if isinstance(emg_threshold, str) and emg_threshold == 'auto':
        emg_threshold = 2.0

    emg_indices = np.where(z_scores > emg_threshold)[0].tolist()
    emg_scores = z_scores[emg_indices].tolist()

    return emg_indices, emg_scores

def clean(
    raw: mne.io.Raw,
    config: dict = None,
    generate_report: bool = True
) -> mne.io.Raw:
    # ... (previous code remains the same)
    if config is None:
        config = get_default_config()

    cleaned_raw = raw.copy()
    original_raw = raw.copy()

    if not cleaned_raw.get_montage():
        try:
            montage = mne.channels.make_standard_montage('standard_1020')
            cleaned_raw.set_montage(montage, on_missing='warn')
        except Exception as e:
            print(f"Warning: Could not set standard_1020 montage: {e}")

    cleaned_raw.filter(l_freq=config['l_freq'], h_freq=config['h_freq'], fir_design='firwin')
    cleaned_raw.notch_filter(freqs=config['notch_freqs'])

    bad_channels = mne.preprocessing.find_bad_channels_lof(cleaned_raw)
    if bad_channels:
        cleaned_raw.info['bads'] = bad_channels
        cleaned_raw.interpolate_bads()

    ica = ICA(
        n_components=config['ica_n_components'],
        random_state=config['ica_random_state']
    )
    ica.fit(cleaned_raw)

    eog_indices, eog_scores = ica.find_bads_eog(cleaned_raw, threshold=config['eog_threshold'])
    emg_indices, emg_scores = _find_emg_components(ica, cleaned_raw, config['emg_threshold'])

    ica.exclude = eog_indices + emg_indices

    ica.apply(cleaned_raw)

    if generate_report:
        print("Generating validation report...")
        report_path = generate_html_report(
            original_raw=original_raw,
            cleaned_raw=cleaned_raw,
            config=config,
            bad_channels_found=bad_channels,
            ica_results={
                'eog_indices': eog_indices, 'eog_scores': eog_scores,
                'emg_indices': emg_indices, 'emg_scores': emg_scores,
                'ica_object': ica
            }
        )
        print(f"Report saved to: {report_path}")

    return cleaned_raw