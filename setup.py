from setuptools import setup, find_packages

# Read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='neuro_analyst',
    version='0.1.0',
    packages=find_packages(),
    author='Your Name', # Replace with your name
    author_email='your.email@example.com', # Replace with your email
    description='An automated EEG preprocessing library.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/neuro-analyst-os', # Replace with your repo URL
    install_requires=[
        'mne',
        'numpy',
        'scipy',
        'pandas',
        'scikit-learn',
        'plotly',
        'jinja2',
        'matplotlib',
        'seaborn',
        'pytest'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.8',
)