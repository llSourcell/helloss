import mne
import matplotlib.pyplot as plt
import seaborn as sns

# Set a modern, clean plotting style
sns.set_style("whitegrid")
sns.set_context("paper", font_scale=1.5)

def plot_psd(raw: mne.io.Raw, compare_with: mne.io.Raw = None, **kwargs):
    """
    Plots the Power Spectral Density (PSD) of a Raw object.

    Args:
        raw (mne.io.Raw): The raw EEG data.
        compare_with (mne.io.Raw, optional): Another raw object to overlay for comparison.
                                           Defaults to None.
    """
    plt.figure(figsize=(12, 6))
    ax = plt.gca()

    # Plot the primary raw object's PSD
    raw.plot_psd(ax=ax, show=False, color='blue', **kwargs)

    if compare_with:
        # Plot the comparison raw object's PSD in a different color
        compare_with.plot_psd(ax=ax, show=False, color='red', **kwargs)
        ax.lines[1].set_linestyle('--') # Differentiate the comparison plot
        plt.legend([ax.lines[0], ax.lines[1]], ['After Cleaning', 'Before Cleaning'])

    ax.set_title("Power Spectral Density")
    plt.tight_layout()
    plt.show()

def plot_evoked(epochs: mne.Epochs, **kwargs):
    """
    Creates a butterfly plot of evoked potentials.

    Args:
        epochs (mne.Epochs): The epoched EEG data.
    """
    evoked = epochs.average()
    evoked.plot(spatial_colors=True, gfp=True, **kwargs)
    plt.title("Evoked Potentials")
    plt.show()

def plot_ica_components(ica: mne.preprocessing.ICA, **kwargs):
    """
    Generates a standard plot of ICA component topographies.

    Args:
        ica (mne.preprocessing.ICA): The fitted ICA object.
    """
    ica.plot_components(**kwargs)
    plt.show()