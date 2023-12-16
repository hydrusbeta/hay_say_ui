from billiard.process import current_process
from celery import Celery, bootsteps
from click import Option
from dash import Input, Output, State, CeleryManager, callback

import download.Downloader as Downloader
import plotly_celery_common as pcc
import util

# Set up a background callback manager
REDIS_URL = 'redis://redis:6379/0'
celery_app = Celery(__name__, broker=REDIS_URL, backend=REDIS_URL)
background_callback_manager = CeleryManager(celery_app)

# Add a command-line argument that lets the user select specific architectures to register with the celery worker
celery_app.user_options['worker'].add(
    Option(('--include_architecture',), multiple=True, default=pcc.architecture_map.keys(), show_default=True,
           help='Add an architecture for which the download callback will be registered'))


# Add a boot step to use the command-line argument
class ArchitectureSelection(bootsteps.Step):
    def __init__(self, parent, include_architecture, **options):
        super().__init__(parent, **options)
        selected_architectures = pcc.select_architecture_tabs(include_architecture)

        # Create background callbacks for the "Download Selected Models" button in each Tab. First, define a generator
        # for the callback:
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
                prevent_initial_call=True,
            )
            def begin_downloading(set_progress, _, character_names):
                print("begin_downloading: " + str(current_process().index), flush=True)
                if not util.internet_available():
                    return 'No internet connection detected', '0', tab.downloadable_character_options(), [], tab.characters, ''
                num_characters = str(len(character_names))
                errors = ''
                for index, character_name in enumerate(character_names):
                    set_progress((str(index), num_characters, 'downloading ' + character_name + '...'))
                    character_model_info, multi_speaker_model_info = tab.get_model_infos_for_character(character_name)
                    errors += Downloader.try_download_character(tab.id, character_model_info, multi_speaker_model_info)
                if errors:
                    errors = 'One or more errors have occurred. Please send the software maintainers the following ' \
                             'information as well as any recent output in the Command Prompt/terminal: ' + errors
                # Report any errors and reset the progress bar, checklist, and character dropdown. Also activate the
                # spinner.
                return errors, '0', tab.downloadable_character_options(), [], tab.characters, ''

            return begin_downloading

        # Now use the generator to instantiate the callback for each Tab.
        # Celery will be able to see and automatically register the callback methods stored in download_callbacks.
        self.download_callbacks = [generate_download_callback(tab) for tab in selected_architectures]
        # Fun bit of trivia: using a background callback generator like that was only possible starting a few months
        # ago. A bug that interfered with it was fixed in March: https://github.com/plotly/dash/issues/2221


celery_app.steps['worker'].add(ArchitectureSelection)
