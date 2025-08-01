
Getting Started
===============

This guide will walk you through the basic usage of Neuro-Analyst OS.

Installation
------------

First, make sure you have all the required dependencies installed:

.. code-block:: bash

   pip install -r requirements.txt

Then, install the library itself:

.. code-block:: bash

   python setup.py install

Your First Analysis
-------------------

Let's walk through a simple analysis of some sample EEG data.

1. **Load the data**

   The first step is to load your data into a `mne.io.Raw` object. The `na.load()` function makes this easy:

   .. code-block:: python

      import neuro_analyst as na

      # Replace with the path to your data file
      raw = na.load('path/to/your/data.edf')

2. **Clean the data**

   Next, use the `na.clean()` function to run the automated preprocessing pipeline. This will filter the data, remove bad channels, and use ICA to remove artifacts.

   .. code-block:: python

      cleaned_raw = na.clean(raw)

   This will also generate an interactive HTML report that you can use to inspect the cleaning process.

3. **Visualize the results**

   Finally, you can use the plotting functions to visualize the cleaned data. For example, you can plot the Power Spectral Density (PSD) before and after cleaning to see the effect of the filters:

   .. code-block:: python

      na.plot_psd(cleaned_raw, compare_with=raw)

That's it! In just a few lines of code, you have taken raw EEG data and turned it into a clean, analyzable dataset.
