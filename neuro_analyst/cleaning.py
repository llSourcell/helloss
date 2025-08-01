
import mne
import numpy as np
from mne.preprocessing import ICA, create_eog_epochs
from mne.time_frequency import psd_array_welch
import logging

from .reporting import generate_html_report
from .utils import get_default_config

# Set up a logger for the library
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
if not log.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    log.addHandler(ch)

def _find_emg_components(ica, raw, emg_threshold):
    # ... (previous code remains the same)
    sources = ica.get_sources(raw).get_data()
    sfreq = raw.info['sfreq']
    psds, freqs = psd_array_welch(sources, sfreq=sfreq, fmin=1, fmax=100, n_fft=int(sfreq))
    emg_band = (freqs >= 30) & (freqs <= 100)
    emg_power = np.mean(psds[:, emg_band], axis=1)
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
    log.info("Starting EEG cleaning pipeline...")
    if config is None:
        config = get_default_config()
        log.info("Using default configuration.")
    else:
        log.info(f"Using custom configuration: {config}")

    cleaned_raw = raw.copy()
    original_raw = raw.copy()

    if not cleaned_raw.get_montage():
        log.warning("No montage found. Attempting to set standard_1020 montage.")
        try:
            montage = mne.channels.make_standard_montage('standard_1020')
            cleaned_raw.set_montage(montage, on_missing='warn')
        except Exception as e:
            log.error(f"Failed to set montage: {e}")

    log.info(f"Applying band-pass filter ({config['l_freq']}-{config['h_freq']} Hz)...")
    cleaned_raw.filter(l_freq=config['l_freq'], h_freq=config['h_freq'], fir_design='firwin')

    log.info(f"Applying notch filter ({config['notch_freqs']} Hz)...")
    cleaned_raw.notch_filter(freqs=config['notch_freqs'])

    log.info("Detecting bad channels...")
    bad_channels = mne.preprocessing.find_bad_channels_lof(cleaned_raw)
    if bad_channels:
        log.info(f"Found {len(bad_channels)} bad channels: {bad_channels}")
        cleaned_raw.info['bads'] = bad_channels
        cleaned_raw.interpolate_bads()
    else:
        log.info("No bad channels detected.")

    log.info("Fitting ICA to remove artifacts...")
    try:
        ica = ICA(
            n_components=config['ica_n_components'],
            random_state=config['ica_random_state']
        )
        ica.fit(cleaned_raw)

        log.info("Finding EOG and EMG artifacts...")
        eog_indices, eog_scores = ica.find_bads_eog(cleaned_raw, threshold=config['eog_threshold'])
        emg_indices, emg_scores = _find_emg_components(ica, cleaned_raw, config['emg_threshold'])
        ica.exclude = eog_indices + emg_indices

        log.info(f"Applying ICA. Excluding {len(ica.exclude)} components.")
        ica.apply(cleaned_raw)

    except Exception as e:
        log.error(f"ICA failed: {e}. Skipping ICA step.")
        ica = None # Ensure ica object exists for the report

    if generate_report:
        log.info("Generating HTML report...")
        report_path = generate_html_report(
            original_raw=original_raw,
            cleaned_raw=cleaned_raw,
            config=config,
            bad_channels_found=bad_channels,
            ica_results={
                'eog_indices': eog_indices if 'ica' in locals() and ica else [],
                'emg_indices': emg_indices if 'ica' in locals() and ica else [],
                'ica_object': ica if 'ica' in locals() else None
            }
        )
        log.info(f"Report saved to: {report_path}")

    log.info("Cleaning pipeline finished.")
    return cleaned_raw
