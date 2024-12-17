import argparse
import datetime
import hashlib
import json
import os
import re
import tempfile
import uuid

import dash_bootstrap_components as dbc
import soundfile
from dash import Dash, html, dcc, Input, Output, State, ctx, callback, MATCH
from dash.exceptions import PreventUpdate
from hay_say_common.cache import Stage

import hay_say_common as hsc
import plotly_celery_common as pcc
from deletion_scheduler import register_cache_cleanup_callback

# todo: so-vits output is much louder than controllable talknet. Should the output volume be equalized?

SHOW_INPUT_OPTIONS_LABEL = 'Show pre-processing options'
SHOW_OUTPUT_OPTIONS_LABEL = 'Show post-processing options'
TAB_BUTTON_PREFIX = '-tab-button'
TAB_CELL_SUFFIX = '-tab-cell'
ANNOUNCEMENT_CHECK_INTERVAL = 60000  # milliseconds

def construct_main_interface(tab_buttons, tabs_contents, enable_session_caches):
    return [
        html.Div([
            html.Div(id='dummy'),
            dcc.Store(id='session', storage_type='memory', data={'id': None}),
            dcc.Interval(interval=ANNOUNCEMENT_CHECK_INTERVAL, id='announcement-checker'),
            html.Div(
                dcc.Markdown('Banner Announcements will appear here', id='banner-announcement'),
                id='banner-announcement-wrapper', hidden=True),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Announcement"), close_button=False),
                dbc.ModalBody("Modal Announcements will appear here", id='modal-announcement-body'),
                dbc.ModalFooter(
                    dbc.Button("Close", id='modal-announcement-close'))
            ], id='modal-announcement', is_open=False),
            html.H1('Hay Say'),
            html.H2('A Unified Interface for Pony Voice Generation', className='subtitle'),
            html.H2('Input'),
            dcc.Textarea(id='text-input', placeholder="Enter some text you would like a pony to say."),
            html.P('And/or provide a voice recording that you would like to ponify:'),
            dcc.Upload([html.Div('Drag and drop file or click to Upload...')], id='file-picker', multiple=True),
            dcc.ConfirmDialog(id='confirm-delete-inputs', message='Are you sure you want to delete all uploaded audio?'),
            dcc.Loading(
                html.Table([
                    html.Tr(
                        html.Td(
                            html.Div('Selected File:')
                        )
                    ),
                    html.Tr(
                        html.Td(html.Div([
                            dbc.Select(id='file-dropdown', className='file-dropdown'),
                            html.Button('delete all uploaded files', id='delete-raw-through-output',
                                        style={'margin-top': '20px'})],
                            id='dropdown-container',
                        )),
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
            dcc.Checklist([SHOW_INPUT_OPTIONS_LABEL], id='show-preprocessing-options', value=[],
                          inputStyle={'margin-right': '10px'}),
            # For future ref, this is how you do a vertical checklist with spacing, in case I want to try that again:
            # dcc.Checklist(['Debug pitch', 'Reduce noise', 'Crop Silence'], ['Debug pitch'], id='test',
            #                labelStyle={'display': 'block', 'margin': '20px'}),
            html.Table([
                html.Tr(
                    html.Td('Note: There are currently no options available. ' +
                            'Adding pre-processing options is on the to-do list!',
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
                    dcc.Checklist([SHOW_OUTPUT_OPTIONS_LABEL], id='show-output-options', value=[],
                                  inputStyle={'margin-right': '10px'})
                    ],
                ),
                html.Table([
                    html.Tr(
                        html.Td('Note: There are currently no options available. ' +
                                'Adding post-processing options is on the to-do list!',
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
                        html.Td(dcc.Input(type='range', min=0.25, max=4, value="1", id='adjust-output-speed',
                                          step='0.01')),
                    ], hidden=True)],
                    id='postprocessing-options',
                    className='spaced-table'
                ),
                html.Table([
                    html.Tr(
                        html.Td(
                            html.Div('Generate with:'), className='centered'
                        ),
                    ),
                    html.Tr(
                        html.Td(
                            dcc.Loading(
                                dcc.RadioItems(id='hardware-selector'),
                                type='default'  # circle, graph, cube, circle, dot, default,
                            ),
                            className='centered'
                        ),
                    ),
                    html.Tr(
                        html.Td(
                            dcc.Loading(
                                html.Button('Generate!', id='generate-button-gpu', className='generate-button'),
                                type='default'  # circle, graph, cube, circle, dot, default
                            ),
                            className='no-padding'
                        ),
                    ),
                    html.Tr(
                        html.Td(
                            dcc.Loading(
                                html.Button('Generate!', id='generate-button-cpu', className='generate-button'),
                                type='default'  # circle, graph, cube, circle, dot, default
                            ),
                            className='no-padding'
                        ),
                    ),
                    html.Tr(
                        html.Td(
                            html.Span('Waiting in queue...', id='generate-message', hidden=True),
                            className='centered'
                        ),
                    )],
                    className='generate-table'
                ),
            ], className='box-div'),
            html.Br(),
            html.Hr(),
            html.H2('Output'),
            html.Table(
                html.Tr([
                    # todo: hide this delete button if there's nothing to delete?
                    html.Td(html.Button('Delete all generated audio', id='delete-postprocessed'), style={"width": "70%"}),
                    html.Td(
                        html.Tr([
                            html.Td(html.Label("Download file format:", htmlFor='output-file-format')),
                            html.Td(dbc.Select(options=sorted([item.lower() for item in soundfile.available_formats().keys() if item.lower() != 'raw']), value='flac', id='output-file-format',
                                               className='file-format-dropdown')),
                        ]),
                        style={"text-align": "right"}
                    )
                ]),
                style={"width": "100%"}
            ),
            html.Div(id='message'),
        ], id='hay-say-outer-div', className='outer-div')
    ]


def register_generate_callbacks(cache_type, architectures):
    import celery_generate_gpu
    import celery_generate_cpu
    celery_generate_gpu.CacheSelection(None, cache_type, architectures)
    celery_generate_cpu.CacheSelection(None, cache_type, architectures)


def register_main_callbacks(enable_session_caches, cache_type, architectures):
    cache = hsc.select_cache_implementation(cache_type)
    available_tabs = pcc.select_architecture_tabs(architectures)

    @callback(
        Output('session', 'data'),
        Input('dummy', 'n_clicks'),
        State('session', 'data')
    )
    def initialize_session_data(n_clicks, existing_data):
        if n_clicks is None:
            return {'id': uuid.uuid4().hex if enable_session_caches else None}
        else:
            print('Warning! initialize_session_data was called outside of initialization. Ignoring request.',
                  flush=True)
            return existing_data

    @callback(
        [Output('banner-announcement', 'children'),
         Output('banner-announcement-wrapper', 'hidden'),
         Output('modal-announcement-body', 'children'),
         Output('modal-announcement', 'is_open')],
        [State('modal-announcement', 'is_open'),
         Input('announcement-checker', 'n_intervals')],
    )
    def display_announcements(current_modal_open, _):
        time_now_utc = datetime.datetime.now(datetime.timezone.utc)
        announcements_file = os.path.join(os.path.dirname(__file__), 'running as server', 'announcements.json')
        print('announcements_file', flush=True)
        print(announcements_file, flush=True)
        banner_announcements, banner_hidden, modal_announcements, modal_open = [], True, [], current_modal_open
        if os.path.isfile(announcements_file):
            try:
                with open(announcements_file, 'r') as file:
                    json_contents = json.load(file)
                for announcement in json_contents:
                    time_format = '%Y-%m-%d %H:%M:%S%z'  # e.g. "2023-11-25 19:01:11+0000"
                    effective_time = datetime.datetime.strptime(announcement['Effective Time'], time_format)
                    expiration_time = datetime.datetime.strptime(announcement['Expiration Time'], time_format)
                    message = announcement['Message']
                    if effective_time <= time_now_utc < expiration_time:
                        # Announcement is active.
                        if announcement.get('Modal') and time_now_utc < effective_time + \
                                datetime.timedelta(milliseconds=ANNOUNCEMENT_CHECK_INTERVAL-1):
                            # A modal announcements is only displayed if it just went active within the last
                            # ANNOUNCEMENT_CHECK_INTERVAL milliseconds.
                            modal_announcements += [message]
                        if announcement.get('Banner'):
                            banner_announcements += [message]
                if banner_announcements:
                    banner_hidden = False
                if modal_announcements:
                    modal_open = True
            except:
                # If there's any problem with parsing the announcements file, don't display any announcements.
                banner_announcements, banner_hidden, modal_announcements, modal_open = [], True, [], current_modal_open
        return '\n\n'.join(banner_announcements), banner_hidden, '\n\n'.join(modal_announcements), modal_open

    @callback(
        Output('modal-announcement', 'is_open', allow_duplicate=True),
        Input('modal-announcement-close', 'n_clicks'),
        prevent_initial_call=True
    )
    def close_modal_announcements(_):
        return False

    @callback(
        [Output('generate-button-gpu', 'hidden'),
         Output('generate-button-cpu', 'hidden')],
        Input('hardware-selector', 'value')
    )
    def select_generate_button(hardware_selection):
        return hardware_selection != 'GPU', hardware_selection != 'CPU'

    @callback(
        Output('message', 'children', allow_duplicate=True),
        Input('delete-postprocessed', 'n_clicks'),
        State('session', 'data'),
        prevent_initial_call=True
    )
    def delete_all_postprocessed(_, session_data):
        cache.delete_all_files_at_stage(Stage.POSTPROCESSED, session_data['id'])
        return ''

    gpt_so_vits_tab = pcc.architecture_map().get('GPTSoVITS', None)
    if gpt_so_vits_tab is not None:
        @callback(
            [Output('file-dropdown', 'options', allow_duplicate=True),
             Output('file-dropdown', 'value', allow_duplicate=True),
             Output('dropdown-container', 'hidden', allow_duplicate=True),
             Output(gpt_so_vits_tab.input_ids[1], 'options', allow_duplicate=True),
             Output(gpt_so_vits_tab.input_ids[1], 'value', allow_duplicate=True)],
            Input('confirm-delete-inputs', 'submit_n_clicks'),
            State('session', 'data'),
            prevent_initial_call=True
        )
        def delete_all_raw_through_output(_, session_data):
            # We must write to the cache of each stage first, to guarantee the Stage exits before deleting all its contents.
            # todo: fix the hay_say_common method so we can call delete_all_files_at_stage by itself.
            cache.write_metadata(Stage.RAW, session_data['id'], dict())
            cache.write_metadata(Stage.PREPROCESSED, session_data['id'], dict())
            cache.write_metadata(Stage.OUTPUT, session_data['id'], dict())
            cache.delete_all_files_at_stage(Stage.RAW, session_data['id'])
            cache.delete_all_files_at_stage(Stage.PREPROCESSED, session_data['id'])
            cache.delete_all_files_at_stage(Stage.OUTPUT, session_data['id'])
            return [], None, True, [], None

        @callback(
            [Output('file-dropdown', 'options'),
             Output('file-dropdown', 'value'),
             Output('dropdown-container', 'hidden'),
             Output('file-picker', 'contents'),
             Output(gpt_so_vits_tab.input_ids[1], 'options'),
             Output(gpt_so_vits_tab.input_ids[1], 'value')],
            # work around for issue #816 (https://github.com/plotly/dash-core-components/issues/816)
            Input('file-picker', 'contents'),
            State('file-picker', 'filename'),
            State('session', 'data'),
            State(gpt_so_vits_tab.input_ids[1], 'value')
        )
        def upload_file(file_contents_list, filename_list, session_data, current_gpt_file):
            if file_contents_list is None:  # initial load of page
                filenames, currently_selected_file, hidden = update_dropdown(cache, None, session_data)
                return filenames, currently_selected_file, hidden, None, filenames, currently_selected_file
            else:
                for file_contents, filename in zip(file_contents_list, filename_list):
                    filename = append_index_if_needed(filename, session_data)
                    raw_array, raw_samplerate = hsc.get_audio_from_src_attribute(file_contents, 'utf-8')
                    save_raw_audio_to_cache(filename, raw_array, raw_samplerate, session_data)
                filenames, currently_selected_file, hidden = update_dropdown(cache, filename_list[0], session_data)
                selected_gptsovits_file = current_gpt_file if current_gpt_file in filenames else currently_selected_file
                return filenames, currently_selected_file, hidden, None, filenames, selected_gptsovits_file
    else:
        @callback(
            [Output('file-dropdown', 'options', allow_duplicate=True),
             Output('file-dropdown', 'value', allow_duplicate=True),
             Output('dropdown-container', 'hidden', allow_duplicate=True)],
            Input('confirm-delete-inputs', 'submit_n_clicks'),
            State('session', 'data'),
            prevent_initial_call=True
        )
        def delete_all_raw_through_output(_, session_data):
            # We must write to the cache of each stage first, to guarantee the Stage exits before deleting all its contents.
            # todo: fix the hay_say_common method so we can call delete_all_files_at_stage by itself.
            cache.write_metadata(Stage.RAW, session_data['id'], dict())
            cache.write_metadata(Stage.PREPROCESSED, session_data['id'], dict())
            cache.write_metadata(Stage.OUTPUT, session_data['id'], dict())
            cache.delete_all_files_at_stage(Stage.RAW, session_data['id'])
            cache.delete_all_files_at_stage(Stage.PREPROCESSED, session_data['id'])
            cache.delete_all_files_at_stage(Stage.OUTPUT, session_data['id'])
            return [], None, True

        @callback(
            [Output('file-dropdown', 'options'),
             Output('file-dropdown', 'value'),
             Output('dropdown-container', 'hidden'),
             Output('file-picker', 'contents')],  # work around for issue #816 (https://github.com/plotly/dash-core-components/issues/816)
            Input('file-picker', 'contents'),
            State('file-picker', 'filename'),
            State('session', 'data'),
        )
        def upload_file(file_contents_list, filename_list, session_data):
            if file_contents_list is None:  # initial load of page
                return *update_dropdown(cache, None, session_data), None
            else:
                for file_contents, filename in zip(file_contents_list, filename_list):
                    filename = append_index_if_needed(filename, session_data)
                    raw_array, raw_samplerate = hsc.get_audio_from_src_attribute(file_contents, 'utf-8')
                    save_raw_audio_to_cache(filename, raw_array, raw_samplerate, session_data)
                return *update_dropdown(cache, filename_list[0], session_data), None

    @callback(
        Output('confirm-delete-inputs', 'displayed'),
        Input('delete-raw-through-output', 'n_clicks'),
        prevent_initial_call=True
    )
    def display_confirm_for_deleting_inputs(_):
        return True

    @callback(
        [Output(tab.id, 'hidden') for tab in available_tabs] +
        [Output(tab.id + TAB_CELL_SUFFIX, 'className') for tab in available_tabs] +
        [Input(tab.id + TAB_BUTTON_PREFIX, 'n_clicks') for tab in available_tabs],
    )
    def hide_unused_tabs(*_):
        hidden_states = [not (tab.id + TAB_BUTTON_PREFIX == ctx.triggered_id) for tab in available_tabs]
        tabs_css_classes = ['tab-cell' if not tab.id + TAB_BUTTON_PREFIX == ctx.triggered_id else
                            'tab-cell-selected' for tab in available_tabs]
        return hidden_states + tabs_css_classes

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
            'Time of Creation': datetime.datetime.now().strftime(hsc.cache.TIMESTAMP_FORMAT)
        }
        cache.write_metadata(Stage.RAW, session_data['id'], raw_metadata)

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
        src = pcc.prepare_src_attribute(bytes_raw, hsc.cache.CACHE_MIMETYPE)
        return src, False

    @callback(
        Output('postprocessing-options', 'hidden'),
        Input('show-output-options', 'value')
    )
    def show_postprocessing_options(value):
        return SHOW_OUTPUT_OPTIONS_LABEL not in value

    @callback(
        [Output('generate-button-gpu', 'disabled'),
         Output('generate-button-cpu', 'disabled')],
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
            return True, True
        else:
            index = hidden_states.index(False)
            selected_character = character_selections[index]
            hidden = not tab_object.meets_requirements(user_text, selected_file, selected_character)
            return hidden, hidden

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

        hash_preprocessed = pcc.preprocess(cache, selected_file, semitone_pitch, debug_pitch, reduce_noise, crop_silence)

        # return src
        bytes_preprocessed = cache.read_file_bytes(Stage.PREPROCESSED, session_data['id'], hash_preprocessed)
        hash_raw = pcc.lookup_filehash(cache, selected_file, session_data)
        return pcc.prepare_src_attribute(bytes_preprocessed, hsc.cache.CACHE_MIMETYPE)

    def get_selected_tab_object(hidden_states):
        # Get the tab that is *not* hidden (i.e. hidden == False)
        return {hidden: tab for hidden, tab in zip(hidden_states, available_tabs)}.get(False)

    @callback(
        Output({'type': 'output-download', 'index': MATCH}, 'data'),
        State('session', 'data'),
        State('output-file-format', 'value'),
        Input({'type': 'output-download-button', 'index': MATCH}, 'n_clicks'),
        prevent_initial_call=True
    )
    def download_postprocessed_audio(session_data, output_file_format, n_clicks):
        if n_clicks:
            # A download button was actually clicked, so return a download.
            hash_postprocessed = ctx.triggered_id['index']
            with tempfile.TemporaryDirectory() as tempdir:
                path = os.path.join(tempdir, hash_postprocessed + '.' + output_file_format)
                data, sr = cache.read_audio_from_cache(Stage.POSTPROCESSED, session_data['id'], hash_postprocessed)
                soundfile.write(path, data, sr)
                return dcc.send_file(path)
        else:
            return None

    def update_dropdown(cache, filename, session_data):
        raw_metadata = cache.read_metadata(Stage.RAW, session_data['id'])
        filenames = [value['User File'] for value in raw_metadata.values()]
        currently_selected_file = filename if filename else filenames[0] if filenames else None
        hidden = currently_selected_file is None
        return filenames, currently_selected_file, hidden

        # raw_metadata = cache.read_metadata(Stage.RAW, session_data['id']) if ctx.triggered_id == 'confirm-delete-inputs' else dict()
        # filenames = [value['User File'] for value in raw_metadata.values()]
        # filenames = filenames + uploaded_filename_list if uploaded_filename_list is not None else filenames
        # currently_selected_file = currently_selected_file if currently_selected_file in filenames \
        #     else uploaded_filename_list[0] if uploaded_filename_list is not None and len(uploaded_filename_list) > 0 \
        #     else filenames[0] if len(filenames) > 0 \
        #     else None
        # return filenames, currently_selected_file


def construct_tab_buttons(available_tabs):
    return [html.Td(
        html.Button(tab.label, id=tab.id + TAB_BUTTON_PREFIX, className='tab-button'),
        className='tab-cell', id=tab.id + TAB_CELL_SUFFIX)
        for tab in available_tabs]


def construct_tabs_interface(architectures, enable_model_management, cache_type):
    available_tabs = pcc.construct_architecture_tabs(architectures, cache_type)
    tab_buttons = construct_tab_buttons(available_tabs)
    tabs_contents = [tab.tab_contents(enable_model_management) for tab in available_tabs]
    return tab_buttons, tabs_contents


def register_tab_callbacks(architectures, enable_model_management):
    available_tabs = pcc.select_architecture_tabs(architectures)
    for tab in available_tabs:
        tab.register_callbacks(enable_model_management)


def parse_arguments(arguments):
    parser = argparse.ArgumentParser(prog='wsgi.py', description='A Unified Interface for Pony Voice Generation.')
    parser.add_argument('--update_model_lists_on_startup', action='store_true', default=False, help='Causes Hay Say to download the latest model lists so that all the latest models appear in the character download menus.')
    parser.add_argument('--enable_model_management', action='store_true', default=False, help='Enables the user to download and delete models.')
    parser.add_argument('--enable_session_caches', action='store_true', default=False, help='Maintain separate caches for each session. If not enabled, a single cache is used for all sessions.')
    parser.add_argument('--cache_implementation', default='file', choices=hsc.cache_implementation_map.keys(), help='Selects an implementation for the audio cache, e.g. saving them to files or to a database.')
    parser.add_argument('--migrate_models', action='store_true', default=False, help='Automatically move models from the model pack directories and custom model directory to the new models directory when Hay Say starts.')
    # todo: this is hardcoded. fix it.
    parser.add_argument('--architectures', nargs='*', choices=['ControllableTalkNet', 'SoVitsSvc3', 'SoVitsSvc4', 'SoVitsSvc5', 'Rvc', 'StyleTTS2', 'GPTSoVITS'], default=['ControllableTalkNet', 'SoVitsSvc3', 'SoVitsSvc4', 'SoVitsSvc5', 'Rvc', 'StyleTTS2', 'GPTSoVITS'], help='Selects which architectures are shown in the Hay Say UI')
    return parser.parse_args(arguments)


def construct_app_layout(enable_model_management, cache_type, architectures, enable_session_caches):
    app = Dash(__name__, external_stylesheets=[dbc.themes.SLATE])
    tab_buttons, tabs_contents = construct_tabs_interface(architectures, enable_model_management, cache_type)
    app.layout = html.Div(construct_main_interface(tab_buttons, tabs_contents, enable_session_caches))
    app.title = 'Hay Say'
    return app


def register_app_callbacks(architectures, enable_model_management, enable_session_caches, cache_type):
    register_tab_callbacks(architectures, enable_model_management)
    register_main_callbacks(enable_session_caches, cache_type, architectures)
    register_generate_callbacks(cache_type, architectures)


def register_download_callbacks(cache_type, architectures):
    # The import statement is located here, to make sure that the download callbacks are not loaded at all unless this
    # method is called.
    from celery_download import ArchitectureSelection
    # Instantiate ArchitectureSelection to instantiate the download callbacks.
    ArchitectureSelection(None, cache_type, architectures)


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


def add_model_management_components_if_needed(cache_type, enable_model_management, architectures, app):
    if enable_model_management:
        available_tabs = pcc.select_architecture_tabs(architectures)
        add_model_management_components(cache_type, architectures, app, available_tabs)


def add_model_management_components(cache_type, architectures, app, available_tabs):
    register_download_callbacks(cache_type, architectures)
    add_model_manager_page(app, available_tabs)
    add_toolbar(app)


def register_cache_cleanup_callback_if_needed(enable_session_caches, cache_type):
    if enable_session_caches:
        register_cache_cleanup_callback(cache_type)


def build_app(architectures, update_model_lists_on_startup=False, enable_model_management=False, enable_session_caches=False,
              cache_type='file', migrate_models=False):
    app = construct_app_layout(enable_model_management, cache_type, architectures, enable_session_caches)
    register_app_callbacks(architectures, enable_model_management, enable_session_caches, cache_type)
    add_model_management_components_if_needed(cache_type, enable_model_management, architectures, app)
    register_cache_cleanup_callback_if_needed(enable_session_caches, cache_type)

    # Save some of the command-line options to the server object so that the server hook methods can get to them:
    app.server.update_model_lists_on_startup = update_model_lists_on_startup
    app.server.migrate_models = migrate_models
    app.server.architectures = architectures
    return app
