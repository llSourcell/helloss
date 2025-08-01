import jinja2
import plotly.io as pio
import plotly.graph_objects as go
from datetime import datetime
import mne
import os
import base64
from io import BytesIO
from .plotting import plot_psd

# Updated HTML template to include more details
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Neuro-Analyst Cleaning Report</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 2em; background-color: #f8f9fa; color: #212529; }
        h1, h2, h3 { color: #343a40; border-bottom: 1px solid #dee2e6; padding-bottom: 0.5em; }
        .container { max-width: 1200px; margin: auto; background: white; padding: 2em; box-shadow: 0 0 10px rgba(0,0,0,0.05); border-radius: 8px; }
        .section { margin-bottom: 2em; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5em; }
        .card { background: #f8f9fa; padding: 1.5em; border-radius: 5px; }
        .plot { margin-top: 1em; }
        ul { padding-left: 20px; }
        li { margin-bottom: 0.5em; }
        code { background: #e9ecef; padding: 0.2em 0.4em; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Neuro-Analyst Cleaning Report</h1>
        <div class="grid">
            <div class="card"><b>Original File:</b><br>{{ original_filename }}</div>
            <div class="card"><b>Report Date:</b><br>{{ date }}</div>
        </div>

        <div class="section">
            <h2>Configuration Used</h2>
            <div class="grid">
                {% for key, value in config.items() %}
                <div class="card"><code>{{ key }}</code>: {{ value }}</div>
                {% endfor %}
            </div>
        </div>

        <div class="section">
            <h2>Power Spectral Density (PSD)</h2>
            <p>Comparison of the PSD before and after cleaning. The 60Hz powerline noise should be visibly reduced.</p>
            <div class="plot">{{ psd_plot }}</div>
        </div>

        <div class="section">
            <h2>Bad Channel Interpolation</h2>
            <p>Found and interpolated <b>{{ num_bad_channels }}</b> bad channels:</p>
            {% if bad_channels %}
                <ul>{% for ch in bad_channels %}<li>{{ ch }}</li>{% endfor %}</ul>
            {% else %}
                <p>No bad channels were detected.</p>
            {% endif %}
        </div>

        <div class="section">
            <h2>ICA Artifact Rejection</h2>
            <p>Rejected <b>{{ num_eog_components }}</b> EOG (eye) and <b>{{ num_emg_components }}</b> EMG (muscle) components.</p>
            <h3>EOG Components Rejected</h3>
            <div class="plot">{{ eog_components_plot }}</div>
            <h3>EMG Components Rejected</h3>
            <!-- EMG plot will go here -->
        </div>

        <div class="section">
            <h2>Signal Comparison (Sample)</h2>
            <p>Comparing a 10-second snippet of channel <code>{{ sample_channel }}</code> before and after cleaning.</p>
            <div class="plot">{{ signal_plot }}</div>
        </div>
    </div>
</body>
</html>
"""

def generate_html_report(original_raw, cleaned_raw, config, bad_channels_found, ica_results):
    """
    Generates an interactive HTML report comparing raw and cleaned data.
    """
    # --- 1. Prepare data for the template ---
    ica = ica_results['ica_object']
    eog_indices = ica_results['eog_indices']
    emg_indices = ica_results['emg_indices']

    template_vars = {
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'original_filename': original_raw.filenames[0] if original_raw.filenames else 'N/A',
        'config': config,
        'num_bad_channels': len(bad_channels_found),
        'bad_channels': bad_channels_found,
        'num_eog_components': len(eog_indices),
        'num_emg_components': len(emg_indices),
    }

    # --- 2. Generate plots ---

    # PSD plot
    fig_psd = plot_psd(cleaned_raw, compare_with=original_raw)
    tmpfile = BytesIO()
    fig_psd.savefig(tmpfile, format='png')
    encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
    template_vars['psd_plot'] = f'<img src="data:image/png;base64,{encoded}">'

    # Signal comparison plot
    ch_to_plot = 'Cz' if 'Cz' in original_raw.ch_names else original_raw.ch_names[0]
    template_vars['sample_channel'] = ch_to_plot
    time_slice = (0, 10)
    orig_data, times = original_raw.get_data(picks=[ch_to_plot], start=original_raw.time_as_index(time_slice[0])[0], stop=original_raw.time_as_index(time_slice[1])[0], return_times=True)
    clean_data, _ = cleaned_raw.get_data(picks=[ch_to_plot], start=cleaned_raw.time_as_index(time_slice[0])[0], stop=cleaned_raw.time_as_index(time_slice[1])[0], return_times=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=orig_data.flatten(), mode='lines', name='Original'))
    fig.add_trace(go.Scatter(x=times, y=clean_data.flatten(), mode='lines', name='Cleaned'))
    fig.update_layout(title=f'Signal on Channel {ch_to_plot}', xaxis_title='Time (s)', yaxis_title='Amplitude')
    template_vars['signal_plot'] = pio.to_html(fig, full_html=False)

    # ICA components plot
    if eog_indices:
        fig_eog = ica.plot_components(picks=eog_indices, show=False)
        tmpfile = BytesIO()
        fig_eog.savefig(tmpfile, format='png')
        encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
        template_vars['eog_components_plot'] = f'<img src="data:image/png;base64,{encoded}">'
    else:
        template_vars['eog_components_plot'] = "<p>No EOG components were detected or rejected.</p>"

    # --- 3. Render and save the HTML ---
    template = jinja2.Template(HTML_TEMPLATE)
    html_content = template.render(template_vars)
    report_filename = f"na_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    report_path = os.path.join(os.getcwd(), report_filename)
    with open(report_path, "w") as f:
        f.write(html_content)

    return report_path