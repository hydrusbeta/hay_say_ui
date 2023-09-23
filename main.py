import argparse
import base64
import hashlib
import json
import re
import traceback
import uuid
from datetime import datetime
from http.client import HTTPConnection
from numbers import Number

import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output, State, ctx, callback
from dash.exceptions import PreventUpdate

import download.Downloader as Downloader
import hay_say_common.cache
import model_migrator as Migrator
from architectures.controllable_talknet.ControllableTalknetTab import ControllableTalknetTab
from architectures.rvc.RvcTab import RvcTab
from architectures.so_vits_svc_3.SoVitsSvc3Tab import SoVitsSvc3Tab
from architectures.so_vits_svc_4.SoVitsSvc4Tab import SoVitsSvc4Tab
from architectures.so_vits_svc_5.SoVitsSvc5Tab import SoVitsSvc5Tab
from hay_say_common import *
from hay_say_common.cache import Stage, CACHE_MIMETYPE, TIMESTAMP_FORMAT

# todo: so-vits output is much louder than controllable talknet. Should the output volume be equalized?

SHOW_INPUT_OPTIONS_LABEL = 'Show pre-processing options'
SHOW_OUTPUT_OPTIONS_LABEL = 'Show post-processing options'
TAB_BUTTON_PREFIX = '-tab-button'
TAB_CELL_SUFFIX = '-tab-cell'


def construct_main_interface(tab_buttons, tabs_contents, enable_session_caches):
    return [
        html.Div([
            dcc.Store(id='session', storage_type='session', data={'id': uuid.uuid4().hex if enable_session_caches else None}),
            html.H1('Hay Say'),
            html.H2('A Unified Interface for Pony Voice Generation', className='subtitle'),
            html.H2('Input'),
            dcc.Textarea(id='text-input', placeholder="Enter some text you would like a pony to say."),
            html.P('And/or provide a voice recording that you would like to ponify:'),
            dcc.Upload([html.Div('Drag and drop file or click to Upload...')], id='file-picker', multiple=True),
            dcc.Loading(
                html.Table([
                    html.Tr(
                        html.Td(
                            html.Div('Selected File:')
                        )
                    ),
                    html.Tr(
                        html.Td(
                            html.Div(
                                dbc.Select(id='file-dropdown', className='file-dropdown'),
                                id='dropdown-container'
                            )
                        )
                    ),
                    html.Tr(
                        html.Td(
                            html.Div(html.Audio(src=None, controls=True, id='input-playback', hidden=True))
                        )
                    )],
                    className='spaced-table'
                ),
                type='default',
                parent_className='dropdown-container-loader'
            ),
            html.H2('Preprocessing'),
            dcc.Checklist([SHOW_INPUT_OPTIONS_LABEL], id='show-preprocessing-options', value=[], inputStyle={'margin-right': '10px'}),
            # For future ref, this is how you do a vertical checklist with spacing, in case I want to try doing that again:
            # dcc.Checklist(['Debug pitch', 'Reduce noise', 'Crop Silence'], ['Debug pitch'], id='test', labelStyle={'display': 'block', 'margin': '20px'}),
            html.Table([
                html.Tr(
                    html.Td("Note: There are currently no options available. Adding pre-processing options is on the to-do list!",
                            colSpan=2, className='centered')
                ),
                html.Tr([
                    html.Td('Adjust pitch of voice recording (semitones)', className='option-label'),
                    html.Td(dcc.Input(id='semitone-pitch', type='number', min=-25, max=25, step=1, value=0))
                ], hidden=True),
                html.Tr([
                    html.Td('Debug pitch', className='option-label'),
                    html.Td(dcc.Checklist([''], id='debug-pitch'))
                ], hidden=True),
                html.Tr([
                    html.Td('Reduce noise', className='option-label'),
                    html.Td(dcc.Checklist([''], id='reduce-noise'))
                ], hidden=True),
                html.Tr([
                    html.Td('Crop silence at beginning and end', className='option-label'),
                    html.Td(dcc.Checklist([''], id='crop-silence'))
                ], hidden=True),
                html.Tr(
                    html.Td(
                        html.Button("Preview", id='preview'),
                        colSpan=2, className='centered'),
                    hidden=True
                ),
                html.Tr(
                    html.Td(
                        html.Div(
                            html.Audio(src=None, controls=True, id='preprocess_playback'),
                            className='centered'),
                        colSpan=2
                    ), hidden=True
                )], id='preprocessing-options', className='spaced-table'
            ),
            html.Br(),
            html.Hr(),
            html.H2('AI Architecture'),
            html.P("Now pick an AI architecture and tweak its settings to your liking:"),
            html.Table(
                html.Tr(tab_buttons), className='tab-table-header'
            ),
            html.Div([
                html.Table(
                    tabs_contents,
                    className='tab-table spaced-table'
                ),
                html.Table([
                    html.H2('Postprocessing'),
                    dcc.Checklist([SHOW_OUTPUT_OPTIONS_LABEL], id='show-output-options', value=[], inputStyle={'margin-right': '10px'})
                    ],
                ),
                html.Table([
                    html.Tr(
                        html.Td("Note: There are currently no options available. Adding post-processing options is on the to-do list!",
                                colSpan=2, className='centered')
                    ),
                    html.Tr([
                        html.Td('Reduce Metallic Sound', className='option-label'),
                        html.Td(dcc.Checklist([''], id='reduce-metallic-sound'), colSpan=2)
                    ], hidden=True),
                    html.Tr([
                        html.Td('Auto-tune output', className='option-label'),
                        html.Td(dcc.Checklist([''], id='auto-tune-output'), colSpan=2)
                    ], hidden=True),
                    html.Tr([
                        html.Td('Adjust speed of output', className='option-label'),
                        html.Td(html.Div('20', id='output-speed-adjustment')),
                        html.Td(dcc.Input(type='range', min=0.25, max=4, value="1", id='adjust-output-speed', step='0.01')),
                    ], hidden=True)],
                    id='postprocessing-options',
                    className='spaced-table'
                ),
                html.Table(
                    html.Tr(
                        html.Td(
                            dcc.Loading(
                                html.Button('Generate!', id='generate-button'),
                                type='default'  # circle, graph, cube, circle, dot, default
                            ),
                        ),
                    ),
                    className='generate-table'
                ),
            ], className='box-div'),
            html.Br(),
            html.Hr(),
            html.H2('Output'),
            # todo: hide this delete button if there's nothing to delete?
            html.Button('Delete all generated audio', id='delete-postprocessed'),
            html.Div(id='message'),
        ], id='hay-say-outer-div', className='outer-div')
    ]


def register_main_callbacks(available_tabs, cache):
    @callback(
        Output('message', 'children', allow_duplicate=True),
        Input('delete-postprocessed', 'n_clicks'),
        State('session', 'data'),
        prevent_initial_call=True
    )
    def delete_all_postprocessed(_, session_data):
        cache.delete_all_files_at_stage(Stage.POSTPROCESSED, session_data['id'])
        return ''

    @callback(
        [Output(tab.id, 'hidden') for tab in available_tabs] +
        [Output(tab.id + TAB_CELL_SUFFIX, 'className') for tab in available_tabs],
        [Input(tab.id + TAB_BUTTON_PREFIX, 'n_clicks') for tab in available_tabs]
    )
    def hide_unused_tabs(*_):
        return [not (tab.id + TAB_BUTTON_PREFIX == ctx.triggered_id) for tab in available_tabs] + \
            ['tab-cell' if not tab.id + TAB_BUTTON_PREFIX == ctx.triggered_id else 'tab-cell-selected'
             for tab in available_tabs]

    @callback(
        Output('output-speed-adjustment', 'children'),
        Input('adjust-output-speed', 'value')
    )
    def adjust_output_speed(adjustment):
        # cast to float first, then round to 2 decimal places
        return "{:3.2f}".format(float(adjustment))

    @callback(
        Output('preprocessing-options', 'hidden'),
        Input('show-preprocessing-options', 'value')
    )
    def show_preprocessing_options(value):
        return SHOW_INPUT_OPTIONS_LABEL not in value

    @callback(
        [Output('file-dropdown', 'options'),
         Output('file-dropdown', 'value'),
         Output('dropdown-container', 'hidden')],
        Input('file-picker', 'contents'),
        State('file-picker', 'filename'),
        State('session', 'data'),
    )
    def upload_file(file_contents_list, filename_list, session_data):
        if file_contents_list is None:  # initial load of page
            return update_dropdown(None, session_data)
        else:
            for file_contents, filename in zip(file_contents_list, filename_list):
                filename = append_index_if_needed(filename, session_data)
                raw_array, raw_samplerate = get_audio_from_src_attribute(file_contents, 'utf-8')
                save_raw_audio_to_cache(filename, raw_array, raw_samplerate, session_data)
            return update_dropdown(filename_list[0], session_data)

    def append_index_if_needed(filename, session_data):
        # Appends an index to the end of the filename, like 'my file.wav (2)', if the file already exists.
        # todo: I think putting something after the extension might break stuff. Do this instead: 'my file (2).wav'
        raw_metadata = cache.read_metadata(Stage.RAW, session_data['id'])
        similar_filenames = [value['User File']
                             for value in raw_metadata.values()
                             if value['User File'].startswith(filename)
                             and (re.match(r' \([0-9]+\)', value['User File'][
                                                           len(filename):])  # file with same name but ending with ' (#)'
                                  or not value['User File'][len(filename):])]  # file with exactly the same name
        index = 1
        while filename in similar_filenames:
            index += 1
            filename = filename + ' (' + str(index) + ')'
        return filename

    def save_raw_audio_to_cache(filename, raw_array, raw_samplerate, session_data):
        hash_raw = hashlib.sha256(raw_array).hexdigest()[:20]
        if cache.file_is_already_cached(Stage.RAW, session_data['id'], hash_raw):
            pass
        else:
            cache.save_audio_to_cache(Stage.RAW, session_data['id'], hash_raw, raw_array, raw_samplerate)
            write_raw_metadata(hash_raw, filename, session_data)

    def write_raw_metadata(hash_80_bits, filename, session_data):
        raw_metadata = cache.read_metadata(Stage.RAW, session_data['id'])
        raw_metadata[hash_80_bits] = {
            'User File': filename,
            'Time of Creation': datetime.now().strftime(TIMESTAMP_FORMAT)
        }
        cache.write_metadata(Stage.RAW, session_data['id'], raw_metadata)

    def update_dropdown(filename, session_data):
        raw_metadata = cache.read_metadata(Stage.RAW, session_data['id'])
        filenames = [value['User File'] for value in raw_metadata.values()]
        currently_selected_file = filename if filename else filenames[0] if filenames else None
        hidden = currently_selected_file is None
        return filenames, currently_selected_file, hidden

    @callback(
        [Output('input-playback', 'src'),
         Output('input-playback', 'hidden')],
        Input('file-dropdown', 'value'),
        State('session', 'data'),
    )
    def update_playback(selected_file, session_data):
        if selected_file is None:
            return None, True
        metadata = cache.read_metadata(Stage.RAW, session_data['id'])
        reverse_lookup = {metadata[key]['User File']: key for key in metadata}
        hash_raw = reverse_lookup[selected_file]
        bytes_raw = cache.read_file_bytes(Stage.RAW, session_data['id'], hash_raw)
        src = prepare_src_attribute(bytes_raw, CACHE_MIMETYPE)
        return src, False

    @callback(
        Output('postprocessing-options', 'hidden'),
        Input('show-output-options', 'value')
    )
    def show_postprocessing_options(value):
        return SHOW_OUTPUT_OPTIONS_LABEL not in value

    @callback(
        [Output('message', 'children'),
         Output('generate-button', 'children')],  # To activate the spinner
        Input('generate-button', 'n_clicks'),
        [State('session', 'data'),
         State('text-input', 'value'),
         State('file-dropdown', 'value'),
         State('semitone-pitch', 'value'),
         State('debug-pitch', 'value'),
         State('reduce-noise', 'value'),
         State('crop-silence', 'value'),
         State('reduce-metallic-sound', 'value'),
         State('auto-tune-output', 'value'),
         State('adjust-output-speed', 'value')]
        + [State(tab.id, 'hidden') for tab in available_tabs]
        # Add every architecture's inputs as States to the callback:
        + [State(item, 'value') for sublist in [tab.input_ids for tab in available_tabs] for item in sublist]
    )
    def generate(clicks, session_data, user_text, selected_file, semitone_pitch, debug_pitch, reduce_noise,
                 crop_silence, reduce_metallic_noise, auto_tune_output, output_speed_adjustment, *args):
        if clicks is not None:
            try:
                selected_tab_object = get_selected_tab_object(args[0:len(available_tabs)])
                relevant_inputs = get_inputs_for_selected_tab(selected_tab_object, args[len(available_tabs):])
                hash_preprocessed = preprocess_if_needed(selected_file, semitone_pitch, debug_pitch, reduce_noise,
                                                         crop_silence, session_data)
                hash_output = process(user_text, hash_preprocessed, selected_tab_object, relevant_inputs, session_data)
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
            prepare_postprocessed_display(sorted_hashes[0], session_data, highlight=highlight_first)] if sorted_hashes else []
        remaining_outputs = [prepare_postprocessed_display(hash_postprocessed, session_data) for hash_postprocessed in
                             reversed(sorted_hashes[1:])]
        return remaining_outputs + first_output, 'Generate!'

    def preprocess_if_needed(selected_file, semitone_pitch, debug_pitch, reduce_noise, crop_silence, session_data):
        if selected_file is None:
            hash_preprocessed = None
        else:
            hash_preprocessed = preprocess(selected_file, semitone_pitch, debug_pitch, reduce_noise, crop_silence,
                                           session_data)
        return hash_preprocessed

    def preprocess(filename, semitone_pitch, debug_pitch, reduce_noise, crop_silence, session_data):
        # Get hashes and determine file locations. Delegate actual preprocessing work to preprocess_file
        # filename must not be None.

        debug_pitch, reduce_noise, crop_silence = convert_to_bools(debug_pitch, reduce_noise, crop_silence)

        hash_raw = lookup_filehash(filename, session_data)
        hash_preprocessed = compute_next_hash(hash_raw, semitone_pitch, debug_pitch, reduce_noise, crop_silence)
        preprocess_file(hash_raw, hash_preprocessed, semitone_pitch, debug_pitch, reduce_noise,
                        crop_silence, session_data)
        return hash_preprocessed

    def lookup_filehash(selected_file, session_data):
        raw_metadata = cache.read_metadata(Stage.RAW, session_data['id'])
        reverse_lookup = {raw_metadata[key]['User File']: key for key in raw_metadata}
        return reverse_lookup.get(selected_file)

    def preprocess_file(hash_raw, hash_preprocessed, semitone_pitch, debug_pitch, reduce_noise, crop_silence,
                        session_data):
        # Handle file operations and write to metadata file. Delegate actual preprocessing work to preprocess_bytes

        if cache.file_is_already_cached(Stage.PREPROCESSED, session_data['id'], hash_preprocessed):
            return

        data_raw, sr_raw = cache.read_audio_from_cache(Stage.RAW, session_data['id'], hash_raw)
        data_preprocessed, sr_preprocessed = preprocess_bytes(data_raw, sr_raw, semitone_pitch, debug_pitch,
                                                              reduce_noise, crop_silence)
        cache.save_audio_to_cache(Stage.PREPROCESSED, session_data['id'], hash_preprocessed, data_preprocessed,
                                  sr_preprocessed)
        write_preprocessed_metadata(hash_raw, hash_preprocessed, semitone_pitch, debug_pitch, reduce_noise,
                                    crop_silence, session_data)

    def preprocess_bytes(bytes_raw, sr_raw, semitone_pitch, debug_pitch, reduce_noise, crop_silence):
        # todo: implement this
        return bytes_raw, sr_raw

    def write_preprocessed_metadata(hash_raw, hash_preprocessed, semitone_pitch, debug_pitch,
                                    reduce_noise, crop_silence, session_data):
        preprocessed_metadata = cache.read_metadata(Stage.PREPROCESSED, session_data['id'])
        preprocessed_metadata[hash_preprocessed] = {
            'Raw File': hash_raw,
            'Options':
                {
                    'Semitone Pitch': semitone_pitch,
                    'Debug Pitch': debug_pitch,
                    'Reduce Noise': reduce_noise,
                    'Crop Silence': crop_silence
                },
            'Time of Creation': datetime.now().strftime(TIMESTAMP_FORMAT)
        }
        cache.write_metadata(Stage.PREPROCESSED, session_data['id'], preprocessed_metadata)

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
            'Time of Creation': datetime.now().strftime(TIMESTAMP_FORMAT)
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
            'Time of Creation': datetime.now().strftime(TIMESTAMP_FORMAT)
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
                    html.Td(html.Audio(src=prepare_src_attribute(bytes_postprocessed, CACHE_MIMETYPE), controls=True),
                            colSpan=2)
                ),
                html.Tr([
                    html.Td('Inputs:', className='output-label'),
                    html.Td((selected_file or 'None')
                            + ((' | ' + user_text[0:20]) if user_text is not None else ''), className='output-value')
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

    @callback(
        Output('generate-button', 'disabled'),
        [Input('text-input', 'value'),
         Input('file-dropdown', 'value')] +
        [Input(tab.id, 'hidden') for tab in available_tabs] +
        [Input(tab.input_ids[0], 'value') for tab in available_tabs]
    )
    def disable_generate_button(user_text, selected_file, *hidden_states_and_character_selections):
        # todo: don't disable the generate button. Instead, highlight the requirements text and whatever the user is
        #  missing in red.
        hidden_states = hidden_states_and_character_selections[:len(available_tabs)]
        character_selections = hidden_states_and_character_selections[len(available_tabs):]
        tab_object = get_selected_tab_object(hidden_states)
        if tab_object is None:
            return True
        else:
            index = hidden_states.index(False)
            selected_character = character_selections[index]
            return not tab_object.meets_requirements(user_text, selected_file, selected_character)

    # todo: disable the preview button if no audio file is selected.
    @callback(
        Output('preprocess_playback', 'src'),
        Input('preview', 'n_clicks'),
        State('session', 'data'),
        State('file-dropdown', 'value'),
        State('semitone-pitch', 'value'),
        State('debug-pitch', 'value'),
        State('reduce-noise', 'value'),
        State('crop-silence', 'value'),
    )
    def generate_preview(_, session_data, selected_file, semitone_pitch, debug_pitch, reduce_noise, crop_silence):
        if selected_file is None:
            raise PreventUpdate

        hash_preprocessed = preprocess(selected_file, semitone_pitch, debug_pitch, reduce_noise, crop_silence)

        # return src
        bytes_preprocessed = cache.read_file_bytes(Stage.PREPROCESSED, session_data['id'], hash_preprocessed)
        hash_raw = lookup_filehash(selected_file)
        return prepare_src_attribute(bytes_preprocessed, CACHE_MIMETYPE)


def prepare_src_attribute(src_bytes, mimetype):
    binary_contents = b'data:' + mimetype.encode('utf-8') + b',' + base64.b64encode(src_bytes)
    return binary_contents.decode('utf-8')


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


def get_selected_tab_object(hidden_states):
    # Get the tab that is *not* hidden (i.e. hidden == False)
    return {hidden: tab for hidden, tab in zip(hidden_states, available_tabs)}.get(False)


def get_inputs_for_selected_tab(tab_object, args):
    all_inputs = [item for sublist in [tab.input_ids for tab in available_tabs] for item in sublist]
    indices_of_relevant_inputs = [index for index, item in enumerate(all_inputs) if item in tab_object.input_ids]
    return [args[i] for i in indices_of_relevant_inputs]


def postprocess_bytes(bytes_output, sr_output, reduce_metallic_noise, auto_tune_output, output_speed_adjustment):
    # todo: implement this
    return bytes_output, sr_output


def compute_next_hash(current_hash, *args):
    # concatenate current_hash with all the remaining arguments and then take the hash
    # current_hash can be None.
    base_string = str(current_hash).join([str(item) for item in args])
    return hashlib.sha256(base_string.encode('utf-8')).hexdigest()[:20]


def convert_to_bools(*args):
    # intended for converting a list of checklist items from ['']/None to True/False, respectively
    return [arg is not None for arg in args]

def construct_tab_buttons(available_tabs):
    return [html.Td(
        html.Button(tab.label, id=tab.id + TAB_BUTTON_PREFIX, className='tab-button'),
        className='tab-cell', id=tab.id + TAB_CELL_SUFFIX)
        for tab in available_tabs]


def construct_tabs_interface(available_tabs, enable_model_management):
    tab_buttons = construct_tab_buttons(available_tabs)
    tabs_contents = [tab.tab_contents(enable_model_management) for tab in available_tabs]
    return tab_buttons, tabs_contents


architecture_map = {'ControllableTalkNet': ControllableTalknetTab(),
                    'SoVitsSvc3': SoVitsSvc3Tab(),
                    'SoVitsSvc4': SoVitsSvc4Tab(),
                    'SoVitsSvc5': SoVitsSvc5Tab(),
                    'Rvc': RvcTab()}

cache_implementation_map = {'mongo': hay_say_common.cache.MongoImpl,
                            'file': hay_say_common.cache.FileImpl}


def parse_arguments():
    parser = argparse.ArgumentParser(prog='Hay Say', description='A Unified Interface for Pony Voice Generation.')
    parser.add_argument('--update_model_lists_on_startup', action='store_true', default=False, help='Causes Hay Say to download the latest model lists so that all the latest models appear in the character download menus.')
    parser.add_argument('--enable_model_management', action='store_true', default=False, help='Enables the user to download and delete models.')
    parser.add_argument('--enable_session_caches', action='store_true', default=False, help='Maintain separate caches for each session. If not enabled, a single cache is used for all sessions.')
    parser.add_argument('--cache_implementation', default='file', choices=cache_implementation_map.keys(), help='Selects an implementation for the audio cache, e.g. saving them to files or to a database.')
    parser.add_argument('--migrate_models', action='store_true', default=False, help='Automatically move models from the model pack directories and custom model directory to the new models directory when Hay Say starts.')
    parser.add_argument('--architectures', nargs='*', choices=architecture_map.keys(), default=architecture_map.keys(), help='Selects which architectures are shown in the Hay Say UI')
    return parser.parse_args()


def select_architecture_tabs(choices):
    return [architecture_map[choice] for choice in choices]


def select_cache_implementation(choice):
    return cache_implementation_map[choice]


def construct_main_app(args, available_tabs, cache_implementation, enable_session_caches):
    app = Dash(__name__, external_stylesheets=[dbc.themes.SLATE])

    tab_buttons, tabs_contents = construct_tabs_interface(available_tabs, args.enable_model_management)
    for tab in available_tabs:
        tab.register_callbacks(args.enable_model_management)

    app.layout = html.Div(construct_main_interface(tab_buttons, tabs_contents, enable_session_caches))
    register_main_callbacks(available_tabs, cache_implementation)
    app.title = 'Hay Say'
    return app


def register_download_callbacks(args):
    # The import statement is located here, to make sure that the download callbacks are not loaded at all unless this
    # method is called.
    from celery_component import ArchitectureSelection
    # Instantiate ArchitectureSelection to instantiate the download callbacks.
    ArchitectureSelection(None, args.architectures)


def add_model_manager_page(app, available_tabs):
    # The import statement is located here, to make sure that the model_manager module is not loaded at all unless this
    # method is called.
    from model_manager import construct_model_manager, register_model_manager_callbacks
    app.layout.children.append(construct_model_manager(available_tabs))
    register_model_manager_callbacks(available_tabs)


def add_toolbar(app):
    # The import statement is located here, to make sure that the toolbar module is not loaded at all unless this method
    # is called.
    from toolbar import construct_toolbar, register_toolbar_callbacks
    app.layout.children.append(construct_toolbar())
    register_toolbar_callbacks()


def add_model_management_components_if_needed(args, app, available_tabs):
    if args.enable_model_management:
        add_model_management_components(args, app, available_tabs)


def add_model_management_components(args, app, available_tabs):
    register_download_callbacks(args)
    add_model_manager_page(app, available_tabs)
    add_toolbar(app)


if __name__ == '__main__':
    args = parse_arguments()

    available_tabs = select_architecture_tabs(args.architectures)
    cache_implementation = select_cache_implementation(args.cache_implementation)
    Migrator.migrate_models_if_specified(args, available_tabs)
    Downloader.update_model_lists_if_specified(args, available_tabs)
    app = construct_main_app(args, available_tabs, cache_implementation, args.enable_session_caches)
    add_model_management_components_if_needed(args, app, available_tabs)

    app.run(host='0.0.0.0', port=6573)


