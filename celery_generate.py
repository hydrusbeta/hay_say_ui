import json
import traceback
import datetime
from http.client import HTTPConnection
from numbers import Number

import click
from billiard.process import current_process
from celery import Celery, bootsteps
from click import Option
from dash import html, Input, Output, State, callback, CeleryManager

from hay_say_common.cache import Stage, CACHE_MIMETYPE, TIMESTAMP_FORMAT
from plotly_celery_common import *

# Set up a background callback manager
REDIS_URL = 'redis://redis:6379/1'
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
        cache = select_cache_implementation(cache_implementation)

        @callback(
            output=[Output('message', 'children'),
                    Output('generate-button', 'children')],  # To activate the spinner
            inputs=[Input('generate-button', 'n_clicks'),
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
                  [State(item, 'value') for sublist in [tab.input_ids for tab in selected_architectures] for item in sublist], # Add every architecture's inputs as States to the callback:
            running=[(Output('generate-message', 'hidden'), False, True)],
            progress=Output('generate-message', 'children'),
            progress_default='Waiting in queue...',
            background=True,
            manager=background_callback_manager,
            prevent_initial_call=True
        )
        def generate(set_progress, clicks, session_data, user_text, selected_file, semitone_pitch, debug_pitch,
                     reduce_noise, crop_silence, reduce_metallic_noise, auto_tune_output, output_speed_adjustment,
                     *args):
            print("generate: " + str(current_process().index), flush=True)
            if clicks is not None:
                try:
                    set_progress('generating...')
                    selected_tab_object = get_selected_tab_object(args[0:len(selected_architectures)])
                    relevant_inputs = get_inputs_for_selected_tab(selected_tab_object, args[len(selected_architectures):])
                    hash_preprocessed = preprocess_if_needed(selected_file, semitone_pitch, debug_pitch, reduce_noise,
                                                             crop_silence, session_data)
                    hash_output = process(user_text, hash_preprocessed, selected_tab_object, relevant_inputs,
                                          session_data)
                    hash_postprocessed = postprocess(hash_output, reduce_metallic_noise, auto_tune_output,
                                                     output_speed_adjustment, session_data)
                    highlight_first = True
                except Exception as e:
                    return 'An error has occurred. Please send the software maintainers the following information as ' \
                           'well as any recent output in the Command Prompt/terminal (please review and remove any ' \
                           'private info before sending!): \n\n' + \
                           traceback.format_exc(), 'Generate!'
            else:
                highlight_first = False
            sorted_hashes = cache.get_hashes_sorted_by_timestamp(Stage.POSTPROCESSED, session_data['id'])
            first_output = [
                prepare_postprocessed_display(sorted_hashes[0], session_data,
                                              highlight=highlight_first)] if sorted_hashes else []
            remaining_outputs = [prepare_postprocessed_display(hash_postprocessed, session_data) for hash_postprocessed
                                 in
                                 reversed(sorted_hashes[1:])]
            return remaining_outputs + first_output, 'Generate!'

        def get_selected_tab_object(hidden_states):
            # Get the tab that is *not* hidden (i.e. hidden == False)
            return {hidden: tab for hidden, tab in zip(hidden_states, selected_architectures)}.get(False)

        def get_inputs_for_selected_tab(tab_object, args):
            all_inputs = [item for sublist in [tab.input_ids for tab in selected_architectures] for item in sublist]
            indices_of_relevant_inputs = [index for index, item in enumerate(all_inputs) if
                                          item in tab_object.input_ids]
            return [args[i] for i in indices_of_relevant_inputs]

        def preprocess_if_needed(selected_file, semitone_pitch, debug_pitch, reduce_noise, crop_silence, session_data):
            if selected_file is None:
                hash_preprocessed = None
            else:
                hash_preprocessed = preprocess(cache, selected_file, semitone_pitch, debug_pitch, reduce_noise,
                                               crop_silence, session_data)
            return hash_preprocessed

        def process(user_text, hash_preprocessed, tab_object, relevant_inputs, session_data):
            """Send a JSON payload to a container, instructing it to perform processing"""

            hash_output = compute_next_hash(hash_preprocessed, user_text, relevant_inputs)
            payload = construct_payload(user_text, hash_preprocessed, tab_object, relevant_inputs, hash_output)

            host = tab_object.id + '_server'
            port = tab_object.port
            send_payload(payload, host, port)

            # Uncomment this for local testing only. It writes a mock output file by copying the input file.
            # data_preprocessed, sr_preprocessed = cache.read_audio_from_cache(Stage.PREPROCESSED, session_data['id'],
            #                                                                  hash_preprocessed)
            # cache.save_audio_to_cache(Stage.OUTPUT, session_data['id'], hash_output, data_preprocessed, sr_preprocessed)

            verify_output_exists(hash_output, session_data)
            write_output_metadata(hash_preprocessed, user_text, hash_output, tab_object, relevant_inputs, session_data)
            return hash_output

        def construct_payload(user_text, hash_preprocessed, tab_object, relevant_inputs, hash_output):
            return {
                'Inputs': {
                    'User Text': user_text,
                    'User Audio': hash_preprocessed
                },
                'Options': tab_object.construct_input_dict(*relevant_inputs),
                'Output File': hash_output
            }

        def send_payload(payload, host, port):
            connection = HTTPConnection(host + ':' + str(port))
            headers = {'Content-type': 'application/json'}
            connection.request('POST', '/generate', json.dumps(payload), headers)
            response = connection.getresponse()
            code = response.status

            if code != 200:
                # Something went wrong, so throw an Exception.
                # The Exception will be caught in the generate() method and displayed to the user.
                message = extract_message(response)
                raise Exception(message)

        def extract_message(response):
            json_response = json.loads(response.read().decode('utf-8'))
            base64_encoded_message = json_response['message']
            return base64.b64decode(base64_encoded_message).decode('utf-8')

        def verify_output_exists(hash_output, session_data):
            try:
                cache.read_audio_from_cache(Stage.OUTPUT, session_data['id'], hash_output)
            except Exception as e:
                raise Exception("Payload was sent, but output file was not produced.") from e

        def write_output_metadata(hash_preprocessed, user_text, hash_output, tab_object, relevant_inputs, session_data):
            output_metadata = cache.read_metadata(Stage.OUTPUT, session_data['id'])

            output_metadata[hash_output] = {
                'Inputs': {
                    'Preprocessed File': hash_preprocessed,
                    'User Text': user_text
                },
                'Options': tab_object.construct_input_dict(*relevant_inputs),
                'Time of Creation': datetime.datetime.now().strftime(TIMESTAMP_FORMAT)
            }
            cache.write_metadata(Stage.OUTPUT, session_data['id'], output_metadata)

        def postprocess(hash_output, reduce_metallic_noise, auto_tune_output, output_speed_adjustment, session_data):
            # Convert data types to something more digestible
            reduce_metallic_noise, auto_tune_output = convert_to_bools(reduce_metallic_noise, auto_tune_output)
            output_speed_adjustment = float(
                output_speed_adjustment)  # Dash's Range Input supplies a string, so cast to float

            # Check whether the postprocessed file already exists
            hash_postprocessed = compute_next_hash(hash_output, reduce_metallic_noise, auto_tune_output,
                                                   output_speed_adjustment)
            if cache.file_is_already_cached(Stage.POSTPROCESSED, session_data['id'], hash_postprocessed):
                return hash_postprocessed

            # Perform postprocessing
            data_output, sr_output = cache.read_audio_from_cache(Stage.OUTPUT, session_data['id'], hash_output)
            data_postprocessed, sr_postprocessed = postprocess_bytes(data_output, sr_output, reduce_metallic_noise,
                                                                     auto_tune_output, output_speed_adjustment)

            # write the postprocessed data to file
            cache.save_audio_to_cache(Stage.POSTPROCESSED, session_data['id'], hash_postprocessed, data_postprocessed,
                                      sr_postprocessed)

            # write metadata file
            write_postprocessed_metadata(hash_output, hash_postprocessed, reduce_metallic_noise, auto_tune_output,
                                         output_speed_adjustment, session_data)

            return hash_postprocessed

        def postprocess_bytes(bytes_output, sr_output, reduce_metallic_noise, auto_tune_output,
                              output_speed_adjustment):
            # todo: implement this
            return bytes_output, sr_output

        def write_postprocessed_metadata(hash_output, hash_postprocessed, reduce_metallic_noise, auto_tune_output,
                                         output_speed_adjustment, session_data):
            processing_options, user_text, hash_preprocessed = get_process_info(hash_output, session_data)
            selected_file, preprocess_options = get_preprocess_info(hash_preprocessed, session_data)

            postprocessed_metadata = cache.read_metadata(Stage.POSTPROCESSED, session_data['id'])
            postprocessed_metadata[hash_postprocessed] = {
                'Inputs': {
                    'User File': selected_file,
                    'User Text': user_text
                },
                'Preprocessing Options': preprocess_options,
                'Processing Options': processing_options,
                'Postprocessing Options': {
                    'Reduce Metallic Noise': reduce_metallic_noise,
                    'Auto Tune Output': auto_tune_output,
                    'Adjust Output Speed': output_speed_adjustment
                },
                'Time of Creation': datetime.datetime.now().strftime(TIMESTAMP_FORMAT)
            }
            cache.write_metadata(Stage.POSTPROCESSED, session_data['id'], postprocessed_metadata)

        def get_process_info(hash_output, session_data):
            output_metadata = cache.read_metadata(Stage.OUTPUT, session_data['id'])
            processing_options = output_metadata.get(hash_output).get('Options')
            user_text = output_metadata.get(hash_output).get('Inputs').get('User Text')
            hash_preprocessed = output_metadata.get(hash_output).get('Inputs').get('Preprocessed File')
            return processing_options, user_text, hash_preprocessed

        def get_preprocess_info(hash_preprocessed, session_data):
            if hash_preprocessed is None:
                selected_file = None
                preprocess_options = None
            else:
                preprocess_metadata = cache.read_metadata(Stage.PREPROCESSED, session_data['id'])
                preprocess_options = preprocess_metadata.get(hash_preprocessed).get('Options')
                hash_raw = preprocess_metadata.get(hash_preprocessed).get('Raw File')

                raw_metadata = cache.read_metadata(Stage.RAW, session_data['id'])
                selected_file = raw_metadata.get(hash_raw).get('User File')
            return selected_file, preprocess_options

        def prepare_postprocessed_display(hash_postprocessed, session_data, highlight=False):
            # todo: color-code the architecture or something to make it easier to tell the difference.
            bytes_postprocessed = cache.read_file_bytes(Stage.POSTPROCESSED, session_data['id'], hash_postprocessed)

            metadata = cache.read_metadata(Stage.POSTPROCESSED, session_data['id'])[hash_postprocessed]
            selected_file = metadata['Inputs']['User File']
            user_text = metadata['Inputs']['User Text']
            if metadata['Preprocessing Options']:
                semitone_pitch = metadata['Preprocessing Options']['Semitone Pitch']
                reduce_noise = metadata['Preprocessing Options']['Reduce Noise']
                crop_silence = metadata['Preprocessing Options']['Crop Silence']
            else:  # i.e. There was no input audio to preprocess
                semitone_pitch = 'N/A'
                reduce_noise = False
                crop_silence = False
            inputs = metadata['Processing Options']
            output_speed_adjustment = metadata['Postprocessing Options']['Adjust Output Speed']
            reduce_metallic_noise = metadata['Postprocessing Options']['Reduce Metallic Noise']
            auto_tune_output = metadata['Postprocessing Options']['Auto Tune Output']
            timestamp = metadata['Time of Creation']

            display = html.Div([
                html.Div(style={'height': '30px'}),  # todo: There's got to be a better way to add spacing
                html.Table([
                    html.Tr(
                        # This table entry serves the special purpose of alerting screen readers that generation is complete.
                        html.Td('New Output Generated:' if highlight else '', role='status' if highlight else None,
                                colSpan=2)
                    ),
                    html.Tr(
                        html.Td(
                            html.Audio(src=prepare_src_attribute(bytes_postprocessed, CACHE_MIMETYPE), controls=True),
                            colSpan=2)
                    ),
                    html.Tr([
                        html.Td('Inputs:', className='output-label'),
                        html.Td((selected_file or 'None')
                                + ((' | ' + user_text[0:20]) if user_text is not None else ''),
                                className='output-value')
                    ]),
                    html.Tr([
                        html.Td('Pre-processing Options:', className='output-label'),
                        html.Td('Pitch adjustment = ' + str(semitone_pitch) + (
                            ' semitone(s)' if semitone_pitch != 'N/A' else '')
                                + (' | Reduce Noise' if reduce_noise else '')
                                + (' | Crop Silence' if crop_silence else ''), className='output-value')
                    ]),
                    html.Tr([
                        html.Td('Processing Options:', className='output-label'),
                        html.Td(prettify_inputs(inputs), className='output-value')
                    ]),
                    html.Tr([
                        html.Td('Post-processing Options:', className='output-label'),
                        html.Td('Output Speed factor = ' + str(output_speed_adjustment)
                                + (' | Reduce Metallic Sound' if reduce_metallic_noise else '')
                                + (' | Auto Tune Output' if auto_tune_output else ''), className='output-value')
                    ]),
                    html.Tr([
                        html.Td('Creation Time:', className='output-label'),
                        html.Td(timestamp, className='output-value')
                    ]),
                ], className='output-table-highlighted' if highlight else 'output-table'),
                html.Div(style={'height': '30px'}),  # todo: There's got to be a better way to add spacing
            ], className='centered')
            return display

        def prettify_inputs(inputs):
            result = ''
            for key in inputs.keys():
                if isinstance(inputs[key], str):
                    result = result + key + " = " + inputs[key] + ' | '
                elif isinstance(inputs[key], bool):
                    result = result + ((key + ' | ') if inputs[key] else '')
                elif isinstance(inputs[key], Number):
                    result = result + key + ' = ' + str(inputs[key]) + ' | '
                else:
                    result = result + key + ' = ' + str(inputs[key]) + ' | '
            if result.endswith(' | '):
                result = result[:-3]
            return result


celery_app.steps['worker'].add(CacheSelection)
