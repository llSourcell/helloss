
# neuro_analyst/utils.py

# This file is reserved for utility functions, such as:
# - Configuration management
# - Helper functions used across multiple modules
# - Logging setup

def get_default_config():
    """Returns the default configuration for the cleaning pipeline."""
    return {
        # Filter settings
        "l_freq": 1.0,          # High-pass filter frequency
        "h_freq": 40.0,         # Low-pass filter frequency
        "notch_freqs": [60.0],  # Powerline noise frequency

        # Bad channel detection (correlation-based)
        "bad_channel_corr_threshold": 0.8, # Lower correlation threshold to be marked bad

        # ICA settings
        "ica_n_components": 15,       # Number of ICA components
        "ica_random_state": 97,       # for reproducibility

        # Artifact detection thresholds
        "eog_threshold": "auto",      # MNE's automated threshold
        "emg_threshold": "auto",      # MNE's automated threshold
    }
