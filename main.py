from hay_say_common import ROOT_DIR, RAW_DIR, PREPROCESSED_DIR, OUTPUT_DIR, POSTPROCESSED_DIR, CACHE_MIMETYPE, \
    CACHE_EXTENSION, TIMESTAMP_FORMAT, save_audio_to_cache, get_audio_from_src_attribute, read_metadata, \
    write_metadata, get_hashes_sorted_by_timestamp, file_is_already_cached, read_audio_from_cache
from tabs.ControllableTalknetTab import ControllableTalknetTab
from tabs.SoVitsSvc3Tab import SoVitsSvc3Tab
from tabs.SoVitsSvc4Tab import SoVitsSvc4Tab
from tabs.SoVitsSvc5Tab import SoVitsSvc5Tab
from dash import Dash, html, dcc, Input, Output, State, ctx
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from numbers import Number
from datetime import datetime
from http.client import HTTPConnection
import re
import base64
import hashlib
import json
import os
import traceback

# todo: so-vits output is much louder than controllable talknet. Should the output volume be equalized?

SHOW_INPUT_OPTIONS_LABEL = 'Show pre-processing options'
SHOW_OUTPUT_OPTIONS_LABEL = 'Show post-processing options'
TAB_BUTTON_PREFIX = '-tab-button'
TAB_CELL_SUFFIX = '-tab-cell'

app = Dash(__name__, external_stylesheets=[dbc.themes.SLATE])

available_tabs = [
    ControllableTalknetTab(app, ROOT_DIR),
    SoVitsSvc3Tab(app, ROOT_DIR),
    SoVitsSvc4Tab(app, ROOT_DIR),
    SoVitsSvc5Tab(app, ROOT_DIR)
]

app.layout = \
    html.Div([
        html.H1('Hay Say'),
        html.H2('A Unified Interface for Pony Voice Generation', className='subtitle'),
        html.H2('Input'),
        dcc.Textarea(id='text-input', placeholder="Enter some text you would like a pony to say."),
        html.P('And/or provide a voice recording that you would like to ponify:'),
        dcc.Upload([html.Div('Drag and drop file or click to Upload...')], id='file-picker'),
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
        dcc.Checklist([SHOW_INPUT_OPTIONS_LABEL], id='show-preprocessing-options', value=[]),
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
            html.Tr([
                html.Td(
                    html.Button(tab.label, id=tab.id + TAB_BUTTON_PREFIX, className='tab-button'),
                    className='tab-cell', id=tab.id + TAB_CELL_SUFFIX)
                for tab in available_tabs
            ]), className='tab-table-header'
        ),
        html.Div([
            html.Table(
                [tab.tab_contents for tab in available_tabs],
                className='tab-table'
            ),
            html.Table([
                html.H2('Postprocessing'),
                dcc.Checklist([SHOW_OUTPUT_OPTIONS_LABEL], id='show-output-options', value=[])
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
                            html.Button(id='generate-button'),
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
    ], id='outer-div')
app.title = 'Hay Say'


@app.callback(
    Output('message', 'children', allow_duplicate=True),
    Input('delete-postprocessed', 'n_clicks'),
    prevent_initial_call=True
)
def delete_all_postprocessed(_):
    for filename in os.listdir(POSTPROCESSED_DIR):
        path = os.path.join(POSTPROCESSED_DIR, filename)
        os.remove(path)


@app.callback(
    [Output(tab.id, 'hidden') for tab in available_tabs] +
    [Output(tab.id + TAB_CELL_SUFFIX, 'className') for tab in available_tabs],
    [Input(tab.id + TAB_BUTTON_PREFIX, 'n_clicks') for tab in available_tabs]
)
def hide_unused_tabs(*_):
    return [not (tab.id + TAB_BUTTON_PREFIX == ctx.triggered_id) for tab in available_tabs] + \
        ['tab-cell' if not tab.id + TAB_BUTTON_PREFIX == ctx.triggered_id else 'tab-cell-selected'
         for tab in available_tabs]
    return result


@app.callback(
    Output('output-speed-adjustment', 'children'),
    Input('adjust-output-speed', 'value')
)
def adjust_output_speed(adjustment):
    # cast to float first, then round to 2 decimal places
    return "{:3.2f}".format(float(adjustment))


@app.callback(
    Output('preprocessing-options', 'hidden'),
    Input('show-preprocessing-options', 'value')
)
def show_preprocessing_options(value):
    return SHOW_INPUT_OPTIONS_LABEL not in value


@app.callback(
    [Output('file-dropdown', 'options'),
     Output('file-dropdown', 'value'),
     Output('dropdown-container', 'hidden')],
    Input('file-picker', 'contents'),
    State('file-picker', 'filename')
)
def upload_file(file_contents, filename):
    if file_contents is None:  # initial load of page
        return update_dropdown(None)
    else:
        filename = append_index_if_needed(filename)
        raw_array, raw_samplerate = get_audio_from_src_attribute(file_contents, 'utf-8')
        save_raw_audio_to_cache(filename, raw_array, raw_samplerate)
        return update_dropdown(filename)


def update_dropdown(filename):
    raw_metadata = read_metadata(RAW_DIR)
    filenames = [value['User File'] for value in raw_metadata.values()]
    currently_selected_file = filename if filename else filenames[0] if filenames else None
    hidden = currently_selected_file is None
    return filenames, currently_selected_file, hidden


def append_index_if_needed(filename):
    # Appends an index to the end of the filename, like 'my file.wav (2)', if the file already exists.
    # todo: I think putting something after the extension might break stuff. Do this instead: 'my file (2).wav'
    raw_metadata = read_metadata(RAW_DIR)
    similar_filenames = [value['User File']
                         for value in raw_metadata.values()
                         if value['User File'].startswith(filename)
                         and (re.match(r' \([0-9]+\)', value['User File'][len(filename):])  # file with same name but ending with ' (#)'
                              or not value['User File'][len(filename):])]  # file with exactly the same name
    index = 1
    while filename in similar_filenames:
        index += 1
        filename = filename + ' (' + str(index) + ')'
    return filename


def save_raw_audio_to_cache(filename, raw_array, raw_samplerate):
    hash_raw = hashlib.sha256(raw_array).hexdigest()[:20]
    if file_is_already_cached(RAW_DIR, hash_raw):
        pass
    else:
        save_audio_to_cache(RAW_DIR, hash_raw, raw_array, raw_samplerate)
        write_raw_metadata(hash_raw, filename)


def read_file_bytes(folder, filename):
    path = os.path.join(folder, filename + CACHE_EXTENSION)
    with open(path, 'rb') as file:
        byte_data = file.read()
    return byte_data


def write_raw_metadata(hash_80_bits, filename):
    raw_metadata = read_metadata(RAW_DIR)
    raw_metadata[hash_80_bits] = {
        'User File': filename,
        'Time of Creation': datetime.now().strftime(TIMESTAMP_FORMAT)
    }
    write_metadata(RAW_DIR, raw_metadata)


@app.callback(
    [Output('input-playback', 'src'),
     Output('input-playback', 'hidden')],
    Input('file-dropdown', 'value')
)
def update_playback(selected_file):
    if selected_file is None:
        return None, True
    metadata = read_metadata(RAW_DIR)
    reverse_lookup = {metadata[key]['User File']: key for key in metadata}
    hash_raw = reverse_lookup[selected_file]
    bytes_raw = read_file_bytes(RAW_DIR, hash_raw)
    src = prepare_src_attribute(bytes_raw, CACHE_MIMETYPE)
    return src, False


def prepare_src_attribute(src_bytes, mimetype):
    binary_contents = b'data:' + mimetype.encode('utf-8') + b',' + base64.b64encode(src_bytes)
    return binary_contents.decode('utf-8')


@app.callback(
    Output('postprocessing-options', 'hidden'),
    Input('show-output-options', 'value')
)
def show_postprocessing_options(value):
    return SHOW_OUTPUT_OPTIONS_LABEL not in value


@app.callback(
    [Output('message', 'children'),
     Output('generate-button', 'children')],  # To activate the spinner
    Input('generate-button', 'n_clicks'),
    [State('text-input', 'value'),
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
def generate(clicks, user_text, selected_file, semitone_pitch, debug_pitch, reduce_noise,
             crop_silence, reduce_metallic_noise, auto_tune_output, output_speed_adjustment, *args):
    if clicks is not None:
        try:
            selected_tab_object = get_selected_tab_object(args[0:len(available_tabs)])
            relevant_inputs = get_inputs_for_selected_tab(selected_tab_object, args[len(available_tabs):])
            hash_preprocessed = preprocess_if_needed(selected_file, semitone_pitch, debug_pitch, reduce_noise, crop_silence)
            hash_output = process(user_text, hash_preprocessed, selected_tab_object, relevant_inputs)
            hash_postprocessed = postprocess(hash_output, reduce_metallic_noise, auto_tune_output, output_speed_adjustment)
            highlight_first = True
        except Exception as e:
            return 'An error has occurred. Please send the software maintainers the following information (please ' \
                   'review and remove any private info before sending!): \n\n' + \
                      traceback.format_exc(), 'Generate!'
    else:
        highlight_first = False
    sorted_hashes = get_hashes_sorted_by_timestamp(POSTPROCESSED_DIR)
    first_output = [prepare_postprocessed_display(sorted_hashes[0], highlight=highlight_first)] if sorted_hashes else []
    remaining_outputs = [prepare_postprocessed_display(hash_postprocessed) for hash_postprocessed in reversed(sorted_hashes[1:])]
    return remaining_outputs + first_output, 'Generate!'


def prepare_postprocessed_display(hash_postprocessed, highlight=False):
    # todo: color-code the architecture or something to make it easier to tell the difference.
    bytes_postprocessed = read_file_bytes(POSTPROCESSED_DIR, hash_postprocessed)

    metadata = read_metadata(POSTPROCESSED_DIR)[hash_postprocessed]
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
                html.Td('New Output Generated:' if highlight else '', role='status' if highlight else None, colSpan=2)
            ),
            html.Tr(
                html.Td(html.Audio(src=prepare_src_attribute(bytes_postprocessed, CACHE_MIMETYPE), controls=True), colSpan=2)
            ),
            html.Tr([
                html.Td('Inputs:', className='output-label'),
                html.Td((selected_file or 'None')
                        + ((' | ' + user_text[0:20]) if user_text is not None else ''), className='output-value')
            ]),
            html.Tr([
                html.Td('Pre-processing Options:', className='output-label'),
                html.Td('Pitch adjustment = ' + str(semitone_pitch) + (' semitone(s)' if semitone_pitch != 'N/A' else '')
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


def get_selected_tab_object(hidden_states):
    # Get the tab that is *not* hidden (i.e. hidden == False)
    return {hidden: tab for hidden, tab in zip(hidden_states, available_tabs)}.get(False)


def get_inputs_for_selected_tab(tab_object, args):
    all_inputs = [item for sublist in [tab.input_ids for tab in available_tabs] for item in sublist]
    indices_of_relevant_inputs = [index for index, item in enumerate(all_inputs) if item in tab_object.input_ids]
    return [args[i] for i in indices_of_relevant_inputs]


def preprocess_if_needed(selected_file, semitone_pitch, debug_pitch, reduce_noise, crop_silence):
    if selected_file is None:
        hash_preprocessed = None
    else:
        hash_preprocessed = preprocess(selected_file, semitone_pitch, debug_pitch, reduce_noise, crop_silence)
    return hash_preprocessed


def postprocess(hash_output, reduce_metallic_noise, auto_tune_output, output_speed_adjustment):
    # Convert data types to something more digestible
    reduce_metallic_noise, auto_tune_output = convert_to_bools(reduce_metallic_noise, auto_tune_output)
    output_speed_adjustment = float(output_speed_adjustment)  # Dash's Range Input supplies a string, so cast to float

    # Check whether the postprocessed file already exists
    hash_postprocessed = compute_next_hash(hash_output, reduce_metallic_noise, auto_tune_output, output_speed_adjustment)
    if file_is_already_cached(POSTPROCESSED_DIR, hash_postprocessed):
        return hash_postprocessed

    # Perform postprocessing
    data_output, sr_output = read_audio_from_cache(OUTPUT_DIR, hash_output)
    data_postprocessed, sr_postprocessed = postprocess_bytes(data_output, sr_output, reduce_metallic_noise, auto_tune_output, output_speed_adjustment)

    # write the postprocessed data to file
    save_audio_to_cache(POSTPROCESSED_DIR, hash_postprocessed, data_postprocessed, sr_postprocessed)

    # write metadata file
    write_postprocessed_metadata(hash_output, hash_postprocessed, reduce_metallic_noise, auto_tune_output, output_speed_adjustment)

    return hash_postprocessed


def write_postprocessed_metadata(hash_output, hash_postprocessed, reduce_metallic_noise, auto_tune_output, output_speed_adjustment):
    processing_options, user_text, hash_preprocessed = get_process_info(hash_output)
    selected_file, preprocess_options = get_preprocess_info(hash_preprocessed)

    postprocessed_metadata = read_metadata(POSTPROCESSED_DIR)
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
    write_metadata(POSTPROCESSED_DIR, postprocessed_metadata)


def get_preprocess_info(hash_preprocessed):
    if hash_preprocessed is None:
        selected_file = None
        preprocess_options = None
    else:
        preprocess_metadata = read_metadata(PREPROCESSED_DIR)
        preprocess_options = preprocess_metadata.get(hash_preprocessed).get('Options')
        hash_raw = preprocess_metadata.get(hash_preprocessed).get('Raw File')

        raw_metadata = read_metadata(RAW_DIR)
        selected_file = raw_metadata.get(hash_raw).get('User File')
    return selected_file, preprocess_options


def get_process_info(hash_output):
    output_metadata = read_metadata(OUTPUT_DIR)
    processing_options = output_metadata.get(hash_output).get('Options')
    user_text = output_metadata.get(hash_output).get('Inputs').get('User Text')
    hash_preprocessed = output_metadata.get(hash_output).get('Inputs').get('Preprocessed File')
    return processing_options, user_text, hash_preprocessed


def postprocess_bytes(bytes_output, sr_output, reduce_metallic_noise, auto_tune_output, output_speed_adjustment):
    # todo: implement this
    return bytes_output, sr_output


def process(user_text, hash_preprocessed, tab_object, relevant_inputs):
    """Send a JSON payload to a container, instructing it to perform processing"""

    hash_output = compute_next_hash(hash_preprocessed, user_text, relevant_inputs)
    payload = construct_payload(user_text, hash_preprocessed, tab_object, relevant_inputs, hash_output)

    host = tab_object.id + '_server'
    port = tab_object.port
    send_payload(payload, host, port)

    # Uncomment this for local testing only. It writes a mock output file by copying the input file.
    # data_preprocessed, sr_preprocessed = read_audio_from_cache(PREPROCESSED_DIR, hash_preprocessed)
    # save_audio_to_cache(OUTPUT_DIR, hash_output, data_preprocessed, sr_preprocessed)

    verify_output_exists(hash_output)
    write_output_metadata(hash_preprocessed, user_text, hash_output, tab_object, relevant_inputs)
    return hash_output


def verify_output_exists(hash_output):
    try:
        read_audio_from_cache(OUTPUT_DIR, hash_output)
    except Exception as e:
        raise Exception("Payload was sent, but output file was not produced.") from e


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


def write_output_metadata(hash_preprocessed, user_text, hash_output, tab_object, relevant_inputs):
    output_metadata = read_metadata(OUTPUT_DIR)

    output_metadata[hash_output] = {
        'Inputs': {
            'Preprocessed File': hash_preprocessed,
            'User Text': user_text
        },
        'Options': tab_object.construct_input_dict(*relevant_inputs),
        'Time of Creation': datetime.now().strftime(TIMESTAMP_FORMAT)
    }
    write_metadata(OUTPUT_DIR, output_metadata)


def construct_payload(user_text, hash_preprocessed, tab_object, relevant_inputs, hash_output):
    return {
        'Inputs': {
            'User Text': user_text,
            'User Audio': hash_preprocessed
        },
        'Options': tab_object.construct_input_dict(*relevant_inputs),
        'Output File': hash_output
    }


def lookup_filehash(selected_file):
    raw_metadata = read_metadata(RAW_DIR)
    reverse_lookup = {raw_metadata[key]['User File']: key for key in raw_metadata}
    return reverse_lookup.get(selected_file)


@app.callback(
    Output('generate-button', 'disabled'),
    [Input('text-input', 'value'),
     Input('file-dropdown', 'value')] +
     [Input(tab.id, 'hidden') for tab in available_tabs]
)
def disable_generate_button(user_text, selected_file, *hidden_states):
    # todo: don't disable the generate button. Instead, highlight the requirements text and whatever the user is
    #  missing in red.
    tab_object = get_selected_tab_object(hidden_states)
    if tab_object is None:
        return True
    else:
        return not tab_object.meets_requirements(user_text, selected_file)


# todo: disable the preview button if no audio file is selected.
@app.callback(
    Output('preprocess_playback', 'src'),
    Input('preview', 'n_clicks'),
    State('file-dropdown', 'value'),
    State('semitone-pitch', 'value'),
    State('debug-pitch', 'value'),
    State('reduce-noise', 'value'),
    State('crop-silence', 'value'),
)
def generate_preview(_, selected_file, semitone_pitch, debug_pitch, reduce_noise, crop_silence):
    if selected_file is None:
        raise PreventUpdate

    hash_preprocessed = preprocess(selected_file, semitone_pitch, debug_pitch, reduce_noise, crop_silence)

    # return src
    bytes_preprocessed = read_file_bytes(PREPROCESSED_DIR, hash_preprocessed)
    hash_raw = lookup_filehash(selected_file)
    return prepare_src_attribute(bytes_preprocessed, CACHE_MIMETYPE)


def compute_next_hash(current_hash, *args):
    # concatenate current_hash with all the remaining arguments and then take the hash
    # current_hash can be None.
    base_string = str(current_hash).join([str(item) for item in args])
    return hashlib.sha256(base_string.encode('utf-8')).hexdigest()[:20]


def preprocess(filename, semitone_pitch, debug_pitch, reduce_noise, crop_silence):
    # Get hashes and determine file locations. Delegate actual preprocessing work to preprocess_file
    # filename must not be None.

    debug_pitch, reduce_noise, crop_silence = convert_to_bools(debug_pitch, reduce_noise, crop_silence)

    hash_raw = lookup_filehash(filename)
    hash_preprocessed = compute_next_hash(hash_raw, semitone_pitch, debug_pitch, reduce_noise, crop_silence)
    preprocess_file(hash_raw, hash_preprocessed, semitone_pitch, debug_pitch, reduce_noise,
                    crop_silence)
    return hash_preprocessed


def convert_to_bools(*args):
    # intended for converting a list of checklist items from ['']/None to True/False, respectively
    return [arg is not None for arg in args]


def preprocess_file(hash_raw, hash_preprocessed, semitone_pitch, debug_pitch, reduce_noise, crop_silence):
    # Handle file operations and write to metadata file. Delegate actual preprocessing work to preprocess_bytes

    if file_is_already_cached(PREPROCESSED_DIR, hash_preprocessed):
        return

    data_raw, sr_raw = read_audio_from_cache(RAW_DIR, hash_raw)
    data_preprocessed, sr_preprocessed = preprocess_bytes(data_raw, sr_raw, semitone_pitch, debug_pitch, reduce_noise, crop_silence)
    save_audio_to_cache(PREPROCESSED_DIR, hash_preprocessed, data_preprocessed, sr_preprocessed)
    write_preprocessed_metadata(hash_raw, hash_preprocessed, semitone_pitch, debug_pitch, reduce_noise, crop_silence)


def write_preprocessed_metadata(hash_raw, hash_preprocessed, semitone_pitch, debug_pitch,
                                reduce_noise, crop_silence):
    preprocessed_metadata = read_metadata(PREPROCESSED_DIR)
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
    write_metadata(PREPROCESSED_DIR, preprocessed_metadata)


def preprocess_bytes(bytes_raw, sr_raw, semitone_pitch, debug_pitch, reduce_noise, crop_silence):
    # todo: implement this
    return bytes_raw, sr_raw


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=6573)


