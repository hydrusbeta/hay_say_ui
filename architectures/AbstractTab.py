from hay_say_common import model_dirs, character_dir, multispeaker_model_dir
import download.Downloader as Downloader
import util

from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

from abc import ABC, abstractmethod
import os
import sys
import json
import tempfile
import shutil

SHOW_CHARACTER_DOWNLOAD_MENU = '▷ Show Character Download Menu'
HIDE_CHARACTER_DOWNLOAD_MENU = '▽ Hide Character Download Menu'

BRANCH = 'In-app-model-download'  # todo: Update this to 'main' before Pull Request to main.
CHARACTER_JSON_FILENAME = 'character_models.json'
MULTI_SPEAKER_JSON_FILENAME = 'multi_speaker_models.json'
BASE_JSON_URL = 'https://raw.githubusercontent.com/hydrusbeta/hay_say_ui/' + BRANCH + '/architectures/{architecture}/'
BASE_CHARACTER_JSON_URL = BASE_JSON_URL + CHARACTER_JSON_FILENAME
BASE_MULTISPEAKER_JSON_URL = BASE_JSON_URL + MULTI_SPEAKER_JSON_FILENAME


class AbstractTab(ABC):
    @property
    @abstractmethod
    def id(self):
        # A unique string for identifying this tab in code. It is used as a prefix for the IDs of html elements related
        # to the tab. The hostname of the container running the ai is <id>_server.
        return 'sample_architecture'

    @property
    @abstractmethod
    def port(self):
        # The port number that the container running the ai architecture uses
        return 8080

    @property
    @abstractmethod
    def label(self):
        # The tab name that is displayed to the user. This is the text shown inside the Button for selecting the tab.
        return 'A Sample Architecture'

    @property
    @abstractmethod
    def description(self):
        return [html.P('Put a general description of the AI architecture here'),
                html.P(
                    html.A("Put a link to the architecture's source code or website here")
                ),
                html.P('Give credit to those who trained the character models here')]

    @property
    @abstractmethod
    def requirements(self):
        return html.P(
            html.Em('Describe to the user which inputs (e.g. text and/or audio reference) are required, here.')
        )

    @abstractmethod
    def meets_requirements(self, user_text, user_audio, selected_character):
        # Return True or False, depending on whether the supplied inputs meet the requirements
        return False

    @property
    @abstractmethod
    def options(self):
        # Display options that are specific to this AI architecture. An example containing a character dropdown and a
        # checkbox option is given below.
        return html.Table([
            html.Tr([
                html.Td(html.Label('Character', htmlFor=self.input_ids[0]), className='option-label'),
                # Note: For a real tab, replace the following with html.Td(self.character_dropdown)
                html.Td(dbc.Select(options=[
                    'Purple Smart',
                    'Ponkers',
                    'Blue Fast',
                    'Yellow Shy',
                    'Good Apple',
                    'Marshmallow'
                ], value='Purple Smart', className='option-dropdown', id=self.input_ids[0]))
            ]),
            html.Tr([
                html.Td(html.Label('Set best pony:', htmlFor=self.input_ids[1]), className='option-label'),
                html.Td(dcc.RadioItems(['Rainbow Dash', 'Rainbow Dash ', 'Rainbow Dash  '],
                                       id=self.input_ids[1], labelClassName='label'))
            ])
        ], className='spaced-table')

    @property
    @abstractmethod
    def input_ids(self):
        # A list of all the element IDs whose values need to be sent when the user clicks the "Generate!" button.
        return [self.id + '-character',
                self.id + '-best-pone']

    @abstractmethod
    def construct_input_dict(self, *args):
        # Construct JSON that will be sent to the container when the user clicks the "Generate!" button.
        # *args will be a list of values the same length of input_ids, in the respective order.
        return dict()

    def downloadable_character_options(self, disabled=False):
        # Sorted options for a dcc.Checklist that includes all downloadable characters, minus the ones that are already
        # downloaded. Optionally set disabled=True to disable every option in the checklist.
        full_list = [model_info['Model Name'] for model_info in self.read_character_model_infos()]
        already_downloaded = self.characters
        sorted_characters = sorted(list(set(full_list).difference(set(already_downloaded))))
        return [{'label': [html.Span(character)], 'value': character, 'disabled': disabled}
                for character in  sorted_characters]

    @property
    def deletable_character_options(self):
        model_paths_and_sizes = [(dir, util.get_size_of_directory(dir)) for dir in sorted(self.model_directory_paths)]
        return [{'label': os.path.basename(entry[0]) + ' [' + util.scale_bytes(entry[1]) + ']',
                 'value': os.path.basename(entry[0])}
                for entry in model_paths_and_sizes]

    def tab_contents(self, enable_model_management):
        return html.Tr([
            html.Td([
                html.Tr(self.description),
                html.Tr(self.requirements)
            ], className='architecture-info'),
            html.Td(
                ([] if not enable_model_management else [html.Div([
                    html.Button(SHOW_CHARACTER_DOWNLOAD_MENU, id=self.id + '-download-menu-button'),
                    dbc.Collapse([
                        # todo: move styling to a css file
                        dcc.Checklist(options=self.downloadable_character_options(),
                                      value=[],
                                      id=self.id + '-download-checklist',
                                      inputClassName='checklist-input-style'),
                        html.Div([
                            html.Br(),
                            html.Div(id=self.id + '-download-size', style={'margin': '5px'}),
                            html.Button('Download Selected Models', style={'margin': '5px'}, id=self.id+'-download-button'),
                            html.Button('Cancel', style={'margin': '5px'}, id=self.id+'-cancel-download-button', hidden=True),
                            html.Div([
                                dcc.Loading(html.Div(id=self.id + '-download-progress-spinner'),
                                            parent_style={'display': 'inline-block', 'width': '60px',
                                                          'height': '15px'}),
                                html.Progress(max='100', value='0', id=self.id + '-download-progress',
                                              style={'display': 'inline-block'}),
                            ], style={'margin-bottom': '20px'}, id=self.id + '-download-progress-container', hidden=True),
                            html.Div('', id=self.id + '-download-text'),
                        ], className='centered')
                    ], is_open=False, id=self.id + "-download-menu", className='model-list-expanded'),
                ], className='model-list-div')]) +
                [self.options])
        ], id=self.id, hidden=True)

    @property
    def characters(self):
        # A sorted list of all the characters available for this architecture.
        return sorted([os.path.basename(character_path) for character_path in self.model_directory_paths])

    @property
    def model_directory_paths(self):
        # A list of all the individual character model folders for this architecture.
        # Loop through all the directories in model_dirs(architecture_name), call os.listdir(model_dir), and flatten the
        # result into a single list. Ignore files; we're only interested in folders that bear character names.
        return [character_path
                for character_path_list in ([os.path.join(model_dir, character) for character in os.listdir(model_dir)]
                                            for model_dir in model_dirs(self.id))
                for character_path in character_path_list if not os.path.isfile(character_path)]

    @property
    def character_dropdown(self):
        return dbc.Select(options=self.characters, value=None if len(self.characters) == 0 else self.characters[0],
                          id=self.input_ids[0], className='option-dropdown')

    def register_callbacks(self, enable_model_management):
        if enable_model_management:
            self.register_model_management_callbacks()

    def register_model_management_callbacks(self):
        @callback(
            [Output(self.id + '-download-menu-button', 'children'),
             Output(self.id + '-download-menu', 'is_open')],
            Input(self.id + '-download-menu-button', 'n_clicks'),
            State(self.id + '-download-menu', 'is_open'),
        )
        def toggle_character_download_menu(n_clicks, is_open):
            if n_clicks is None:
                raise PreventUpdate
            return SHOW_CHARACTER_DOWNLOAD_MENU if is_open else HIDE_CHARACTER_DOWNLOAD_MENU, not is_open

        @callback(
            Output(self.id + '-download-size', 'children'),
            Output(self.id + '-download-button', 'disabled'),
            Input(self.id + '-download-checklist', 'value'),
        )
        def update_download_size(selected_characters):
            files_and_sizes = {}
            for character in selected_characters:
                files_and_sizes |= self.determine_files_required_by_character(character)  # |= performs a PEP 584 Dict union
            total_size = sum([size for filename, size in files_and_sizes.items()])
            no_characters_text = 'No additional characters available for download'
            download_size_text = 'Total Download Size: ' + util.scale_bytes(total_size)
            displayed_text = no_characters_text if len(self.downloadable_character_options()) == 0 else download_size_text
            return displayed_text, False if selected_characters else True

    def determine_files_required_by_character(self, character):
        # Return a dictionary with entries of the form {'<path/to/file>': <file_size_in_bytes>}.
        character_model_info, multi_speaker_model_info = self.get_model_infos_for_character(character)
        files_and_sizes = self.determine_files_required_for_character_alone(character_model_info)
        files_and_sizes |= self.determine_files_required_for_multi_speaker_model(multi_speaker_model_info)
        return files_and_sizes

    def determine_files_required_for_character_alone(self, character_model_info):
        # Return a dictionary with entries of the form {'<path/to/file>': <file_size_in_bytes>}.
        model_directory = character_dir(self.id, character_model_info['Model Name'])
        return {os.path.join(model_directory, file['Download As']): file['Size (bytes)']
                for file in character_model_info['Files']}

    def determine_files_required_for_multi_speaker_model(self, multi_speaker_model_info):
        # Return a dictionary with entries of the form {'<path/to/file>': <file_size_in_bytes>}.
        # If the multi speaker model is already downloaded, return an empty dictionary.
        if multi_speaker_model_info is not None:
            model_directory = multispeaker_model_dir(self.id, multi_speaker_model_info['Model Name'])
            if not os.path.exists(model_directory):
                return {os.path.join(model_directory, file['Download As']): file['Size (bytes)']
                        for file in multi_speaker_model_info['Files']}
        return {}

    def get_model_infos_for_character(self, character):
        character_model_infos = [model_info for model_info in self.read_character_model_infos()
                                if model_info['Model Name'] == character]
        if len(character_model_infos) == 0:
            # This should never happen. But in case it somehow does, throw a potentially useful Exception.
            raise Exception(str(character) + ' was not found in character_models.json.')
        if len(character_model_infos) > 1:
            raise Exception(str(character) + ' has multiple entries in character_models.json. Only one is allowed.')
        character_model_info = character_model_infos[0]
        multi_speaker_model = self.get_multi_speaker_model_info_for_character(character_model_info)
        return character_model_info, multi_speaker_model

    def get_multi_speaker_model_info_for_character(self, character_model_info):
        multi_speaker_model_name = character_model_info.get('Multi-speaker Model Dependency')
        if multi_speaker_model_name is None:
            return None
        else:
            multi_speaker_model_infos = [model_info for model_info in self.read_multi_speaker_model_infos()
                                         if model_info['Model Name'] == multi_speaker_model_name]
            if len(multi_speaker_model_infos) == 0:
                raise Exception(str(multi_speaker_model_name) + ' was not found in multi_speaker_models.json, but is '
                                'specified as a dependency for ' + character_model_info['Model Name'] + ' in '
                                'character_models.json')
            if len(multi_speaker_model_infos) > 1:
                raise Exception(str(multi_speaker_model_name) + ' has multiple entries in multi_speaker_models.json. '
                                'Only one is allowed.')
            return multi_speaker_model_infos[0]

    def read_character_model_infos(self):
        return self.read_json_file(CHARACTER_JSON_FILENAME)

    def read_multi_speaker_model_infos(self):
        return self.read_json_file(MULTI_SPEAKER_JSON_FILENAME)

    def read_json_file(self, filename):
        # Read a json file from this architecture's subdirectory
        directory = self.get_dir_of_extending_class_module()
        json_path = os.path.join(directory, filename)
        with open(json_path, 'r') as file:
            file_contents = json.load(file)
        return file_contents

    def get_dir_of_extending_class_module(self):
        # Gets the directory of the module where the concrete class is defined. For example, if ctt is an instance of
        # ControllableTalknetTab, then ctt.get_module_dir_of_extending_class() will return a path like
        # /<path-to-hay_say>/architectures/controllable_talknet/
        path_to_module_of_extending_class = sys.modules[self.__module__].__file__
        return os.path.dirname(path_to_module_of_extending_class)

    def update_multi_speaker_infos_file(self):
        self.update_model_infos_file(BASE_MULTISPEAKER_JSON_URL, MULTI_SPEAKER_JSON_FILENAME)

    def update_character_infos_file(self):
        self.update_model_infos_file(BASE_CHARACTER_JSON_URL, CHARACTER_JSON_FILENAME)

    def update_model_infos_file(self, base_url, filename):
        target_path = os.path.join(self.get_dir_of_extending_class_module(), filename)
        url = base_url.replace("{architecture}", self.id)
        with tempfile.TemporaryDirectory() as tempdir:
            source_path = os.path.join(tempdir, filename)
            Downloader.requests_downloader(url, source_path)
            if os.path.exists(target_path):
                os.remove(target_path)  # delete the original file
            shutil.move(source_path, target_path)  # replace the original file

