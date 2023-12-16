import click
import numpy
from celery import Celery, bootsteps
from click import Option
from dash import Input, Output, State, callback, CeleryManager, ctx

import hay_say_common as hsc
import main
import plotly_celery_common as pcc
from generator import generate_and_prepare_postprocessed_display

# Set up a background callback manager
REDIS_URL = 'redis://redis:6379/2'
celery_app = Celery(__name__, broker=REDIS_URL, backend=REDIS_URL)
background_callback_manager = CeleryManager(celery_app)

# Add a command-line argument for selecting the cache implementation
celery_app.user_options['worker'].add(
    Option(('--cache_implementation',), default='file', show_default=True,
           type=click.Choice(hsc.cache.cache_implementation_map.keys(), case_sensitive=False),
           help='Selects an implementation for the audio cache, e.g. saving them to files or to a database.'))

# Add a command-line argument that lets the user select specific architectures to register with the celery worker
celery_app.user_options['worker'].add(
    Option(('--include_architecture',), multiple=True, default=pcc.architecture_map.keys(), show_default=True,
           help='Add an architecture for which the download callback will be registered'))


# Add a boot step to use the command-line argument
class CacheSelection(bootsteps.Step):
    def __init__(self, parent, cache_implementation, include_architecture, **options):
        super().__init__(parent, **options)
        selected_architectures = pcc.select_architecture_tabs(include_architecture)

        @callback(
            output=[Output('message', 'children'),
                    Output('generate-button-cpu', 'children')],  # To activate the spinner
            inputs=[Input('generate-button-cpu', 'n_clicks'),
                    State('session', 'data'),
                    State('text-input', 'value'),
                    State('file-dropdown', 'value'),
                    State('semitone-pitch', 'value'),
                    State('debug-pitch', 'value'),
                    State('reduce-noise', 'value'),
                    State('crop-silence', 'value'),
                    State('reduce-metallic-sound', 'value'),
                    State('auto-tune-output', 'value'),
                    State('adjust-output-speed', 'value')] +
                   [State(tab.id, 'hidden') for tab in selected_architectures] +
                   [State(item, 'value') for sublist in   # Add every architecture's inputs as States to the callback
                    [tab.input_ids for tab in selected_architectures]
                    for item in sublist],
            running=[(Output('generate-message', 'hidden'), False, True)],
            progress=Output('generate-message', 'children'),
            progress_default='Waiting in queue...',
            background=True,
            manager=background_callback_manager,
        )
        def generate_with_cpu(set_progress, clicks, session_data, user_text, selected_file, semitone_pitch, debug_pitch,
                              reduce_noise, crop_silence, reduce_metallic_noise, auto_tune_output,
                              output_speed_adjustment, *args):
            gpu_id = ''
            message = 'generating on CPU...'
            return generate_and_prepare_postprocessed_display(clicks, set_progress, message, cache_implementation,
                                                              gpu_id, session_data, selected_architectures, user_text,
                                                              selected_file, semitone_pitch, debug_pitch, reduce_noise,
                                                              crop_silence, reduce_metallic_noise, auto_tune_output,
                                                              output_speed_adjustment, args)

        @callback(
            [Output('hardware-selector', 'options')] +
            [Output('hardware-selector', 'value')],
            [State('hardware-selector', 'value')] +
            [Input(tab.id + main.TAB_BUTTON_PREFIX, 'n_clicks') for tab in selected_architectures],
        )
        def hide_unused_tabs(current_hardware_selection, *_):
            if current_hardware_selection is None:
                hardware_options = [[]]
                hardware_selection = ['CPU']
            else:
                hidden_states = [not (tab.id + main.TAB_BUTTON_PREFIX == ctx.triggered_id) for tab in selected_architectures]
                selected_tab = get_selected_tab_object(hidden_states)
                hardware_options = [selected_tab.hardware_options]
                hardware_selection = ['CPU'] if 'GPU' not in numpy.squeeze(hardware_options) else [
                    current_hardware_selection]
            return hardware_options + hardware_selection

        def get_selected_tab_object(hidden_states):
            # Get the tab that is *not* hidden (i.e. hidden == False)
            return {hidden: tab for hidden, tab in zip(hidden_states, selected_architectures)}.get(False)


celery_app.steps['worker'].add(CacheSelection)
