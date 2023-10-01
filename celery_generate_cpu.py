import click
from celery import Celery, bootsteps
from click import Option
from dash import Input, Output, State, callback, CeleryManager
from hay_say_common.cache import cache_implementation_map

from generator import generate_and_prepare_postprocessed_display
from plotly_celery_common import *

# Set up a background callback manager
REDIS_URL = 'redis://redis:6379/2'
celery_app = Celery(__name__, broker=REDIS_URL, backend=REDIS_URL)
background_callback_manager = CeleryManager(celery_app)

# Add a command-line argument for selecting the cache implementation
celery_app.user_options['worker'].add(
    Option(('--cache_implementation',), default='file', show_default=True,
           type=click.Choice(cache_implementation_map.keys(), case_sensitive=False),
           help='Selects an implementation for the audio cache, e.g. saving them to files or to a database.'))

# Add a command-line argument that lets the user select specific architectures to register with the celery worker
celery_app.user_options['worker'].add(
    Option(('--include_architecture',), multiple=True, default=architecture_map.keys(), show_default=True,
           help='Add an architecture for which the download callback will be registered'))


# Add a boot step to use the command-line argument
class CacheSelection(bootsteps.Step):
    def __init__(self, parent, cache_implementation, include_architecture, **options):
        super().__init__(parent, **options)
        selected_architectures = select_architecture_tabs(include_architecture)

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


celery_app.steps['worker'].add(CacheSelection)
