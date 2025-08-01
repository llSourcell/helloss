""
Command-line interface for Neuro-Analyst OS.
"""
import argparse
import sys
import os
from pathlib import Path
from typing import Optional

import mne

from . import __version__
from .io import load
from .cleaning import clean
from .plotting import plot_psd, plot_evoked, plot_ica_components
from .reporting import generate_html_report
from .utils import get_config, set_config

def main(args: Optional[list] = None) -> int:
    """Run the Neuro-Analyst OS command-line interface.
    
    Parameters
    ----------
    args : list, optional
        Command-line arguments. If None, uses sys.argv[1:].
        
    Returns
    -------
    int
        Exit code (0 for success, non-zero for error).
    """
    parser = argparse.ArgumentParser(
        description="Neuro-Analyst OS: An opinionated EEG preprocessing and analysis library.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Global arguments
    parser.add_argument(
        '--version', 
        action='version', 
        version=f'Neuro-Analyst OS v{__version__}'
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Clean EEG data')
    clean_parser.add_argument(
        'input_file', 
        type=str, 
        help='Path to the input EEG file (supports .edf, .bdf, .fif, .set, .vhdr)'
    )
    clean_parser.add_argument(
        '-o', '--output', 
        type=str, 
        default='cleaned_eeg.fif',
        help='Output file path for the cleaned data (default: %(default)s)'
    )
    clean_parser.add_argument(
        '--l-freq', 
        type=float, 
        default=get_config('l_freq'),
        help='High-pass filter cutoff frequency in Hz (default: %(default).1f)'
    )
    clean_parser.add_argument(
        '--h-freq', 
        type=float, 
        default=get_config('h_freq'),
        help='Low-pass filter cutoff frequency in Hz (default: %(default).1f)'
    )
    clean_parser.add_argument(
        '--notch', 
        type=float, 
        nargs='+',
        default=get_config('notch_freqs'),
        help='Notch filter frequencies in Hz (default: %(default)s)'
    )
    clean_parser.add_argument(
        '--ica-components', 
        type=int, 
        default=get_config('ica_n_components'),
        help='Number of ICA components to extract (default: %(default)d)'
    )
    clean_parser.add_argument(
        '--no-report', 
        action='store_true',
        help='Disable HTML report generation'
    )
    
    # Plot command
    plot_parser = subparsers.add_parser('plot', help='Plot EEG data')
    plot_parser.add_argument(
        'input_file', 
        type=str, 
        help='Path to the EEG file'
    )
    plot_parser.add_argument(
        '--type', 
        type=str, 
        choices=['psd', 'sensors', 'ica'],
        default='psd',
        help='Type of plot to generate (default: %(default)s)'
    )
    plot_parser.add_argument(
        '--output', 
        type=str, 
        help='Output file path for the plot (default: display interactively)'
    )
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_parser.add_argument(
        '--list', 
        action='store_true',
        help='List all configuration settings'
    )
    config_parser.add_argument(
        '--get', 
        type=str,
        help='Get a specific configuration value by key'
    )
    config_parser.add_argument(
        '--set', 
        nargs=2,
        metavar=('KEY', 'VALUE'),
        help='Set a configuration value'
    )
    
    # Parse arguments
    if args is None:
        args = sys.argv[1:]
    
    if not args:
        parser.print_help()
        return 0
    
    args = parser.parse_args(args)
    
    # Handle commands
    if args.command == 'clean':
        return handle_clean(args)
    elif args.command == 'plot':
        return handle_plot(args)
    elif args.command == 'config':
        return handle_config(args)
    else:
        parser.print_help()
        return 0

def handle_clean(args) -> int:
    """Handle the 'clean' command."""
    try:
        # Load the EEG data
        print(f"Loading EEG data from {args.input_file}...")
        raw = load(args.input_file)
        
        # Clean the data
        print("Cleaning EEG data...")
        raw_clean, report = clean(
            raw,
            l_freq=args.l_freq,
            h_freq=args.h_freq,
            notch_freqs=args.notch,
            ica_n_components=args.ica_components,
            generate_report=not args.no_report
        )
        
        # Save the cleaned data
        print(f"Saving cleaned data to {args.output}...")
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        raw_clean.save(output_path, overwrite=True)
        
        print("\nCleaning completed successfully!")
        print(f"- Original file: {args.input_file}")
        print(f"- Cleaned file: {output_path.absolute()}")
        
        if not args.no_report and 'report_path' in report:
            print(f"- HTML report: {report['report_path']}")
        
        return 0
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

def handle_plot(args) -> int:
    """Handle the 'plot' command."""
    try:
        # Load the EEG data
        print(f"Loading EEG data from {args.input_file}...")
        raw = load(args.input_file)
        
        # Generate the requested plot
        if args.type == 'psd':
            print("Generating PSD plot...")
            fig = plot_psd(raw, show=False)
            title = 'Power Spectral Density'
        elif args.type == 'sensors':
            print("Generating sensor layout plot...")
            fig = raw.plot_sensors(show_names=True, show=False)
            title = 'Sensor Layout'
        elif args.type == 'ica':
            print("Generating ICA components plot...")
            # This is a simplified example; in a real implementation, you'd fit ICA first
            ica = mne.preprocessing.ICA(n_components=15, random_state=42)
            ica.fit(raw)
            fig = ica.plot_components(show=False)
            title = 'ICA Components'
        else:
            print(f"Error: Unknown plot type '{args.type}'", file=sys.stderr)
            return 1
        
        # Save or show the plot
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(output_path, bbox_inches='tight')
            print(f"Plot saved to {output_path.absolute()}")
        else:
            import matplotlib.pyplot as plt
            plt.suptitle(title)
            plt.tight_layout()
            plt.show()
        
        return 0
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

def handle_config(args) -> int:
    """Handle the 'config' command."""
    try:
        if args.list:
            # List all configuration settings
            import json
            print(json.dumps(get_config(), indent=4))
        elif args.get:
            # Get a specific configuration value
            value = get_config(args.get)
            if value is not None:
                print(f"{args.get} = {value}")
            else:
                print(f"No configuration found for '{args.get}'", file=sys.stderr)
                return 1
        elif args.set:
            # Set a configuration value
            key, value = args.set
            # Try to convert value to appropriate type
            try:
                # Try to convert to int
                value = int(value)
            except ValueError:
                try:
                    # Try to convert to float
                    value = float(value)
                except ValueError:
                    # Try to convert to bool
                    if value.lower() == 'true':
                        value = True
                    elif value.lower() == 'false':
                        value = False
                    # Otherwise, keep as string
            
            set_config(key, value)
            print(f"Set {key} = {value}")
        else:
            print("No action specified. Use --list, --get, or --set.", file=sys.stderr)
            return 1
        
        return 0
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
