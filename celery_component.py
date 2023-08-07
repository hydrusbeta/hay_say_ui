from dash import Input, Output, State, CeleryManager, callback
import os
from celery import Celery
import download.Downloader as Downloader
from main import architecture_map

# Set up a background callback manager
MESSAGE_BROKER = os.environ.get('REDIS_URL', 'redis://localhost:6379')
celery_app = Celery(__name__, broker=MESSAGE_BROKER, backend=MESSAGE_BROKER)
background_callback_manager = CeleryManager(celery_app)

# Create background callbacks for the "Download Selected Models" button in each Tab. Ideally, this callback would simply
# be defined in AbstractTab. However, Celery does not support using class methods as tasks. So instead, we must
# instantiate the callback for each of the Tabs at the module level. See
# https://github.com/celery/celery/discussions/7085.


# First, define a generator for the callback:
def generate_download_callback(tab):
    @callback(
        output=[Output(tab.id + '-download-text', 'children'),
                Output(tab.id + '-download-progress', 'value'),
                Output(tab.id + '-download-checklist', 'options'),
                Output(tab.id + '-download-checklist', 'value', allow_duplicate=True),
                Output(tab.input_ids[0], 'options'),  # character dropdown,
                Output(tab.id + '-download-progress-spinner', 'children')],
        inputs=[Input(tab.id + '-download-button', 'n_clicks'),
                State(tab.id + '-download-checklist', 'value')],
        running=[(Output(tab.id + '-download-button', 'hidden'), True, False),
                 (Output(tab.id + '-cancel-download-button', 'hidden'), False, True),
                 (Output(tab.id + '-download-text', 'hidden'), False, True),
                 (Output(tab.id + '-download-progress-container', 'hidden'), False, True),
                 (Output(tab.id + '-download-checklist', 'options'),
                  tab.downloadable_character_options(disabled=True),
                  tab.downloadable_character_options(disabled=False))],
        cancel=[Input(tab.id + '-cancel-download-button', 'n_clicks')],
        progress=[Output(tab.id + '-download-progress', 'value'),
                  Output(tab.id + '-download-progress', 'max'),
                  Output(tab.id + '-download-text', 'children')],
        background=True,
        manager=background_callback_manager,
        prevent_initial_call=True
    )
    def begin_downloading(set_progress, _, character_names):
        num_characters = str(len(character_names))
        for index, character_name in enumerate(character_names):
            set_progress((str(index), num_characters, 'downloading ' + character_name + '...'))
            character_model_info, multi_speaker_model_info = tab.get_model_infos_for_character(character_name)
            Downloader.download_character(tab.id, character_model_info, multi_speaker_model_info)
        # Reset the progress bar, checklist, and character dropdown. Also activate the spinner
        return '', '0', tab.downloadable_character_options(), [], tab.characters, ''

    return begin_downloading


# Now use the generator to instantiate the callback for each Tab.
# Celery will be able to see and automatically register the callback methods stored in download_callbacks.
download_callbacks = [generate_download_callback(tab) for tab in architecture_map.values()]


# Fun bit of trivia: using a background callback generator like that was only possible starting a few months ago. A bug
# that interfered with it was fixed in March: https://github.com/plotly/dash/issues/2221