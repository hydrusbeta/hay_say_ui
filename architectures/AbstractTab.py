import hay_say_common

from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

from abc import ABC, abstractmethod
import os

from architectures.sample_architecture.character_models import character_models
from architectures.sample_architecture.multi_speaker_models import multi_speaker_models

SHOW_CHARACTER_DOWNLOAD_MENU = "▷ Show Character Download Menu"
HIDE_CHARACTER_DOWNLOAD_MENU = "▽ Hide Character Download Menu"


class AbstractTab(ABC):

    def __init__(self, app, root_dir):
        self.app = app
        self.root_dir = root_dir
        app.callback(
                [Output(self.id+'-download-menu-button', 'children'),
                 Output(self.id+'-download-menu', 'is_open')],
                Input(self.id+'-download-menu-button', 'n_clicks'),
                State(self.id+'-download-menu', 'is_open'),
        )(self.toggle_character_download_menu)
        app.callback(
            Output(self.id + '-download-size', 'children'),
            Input(self.id + '-download-checklist', 'value'))(self.update_download_size)

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
    def meets_requirements(self, user_text, user_audio):
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
                ], value='Purple Smart', className='option-dropdown'))
            ]),
            html.Tr([
                html.Td(html.Label('Set best pony:', htmlFor=self.input_ids[1]), className='option-label'),
                html.Td(dcc.RadioItems(['Rainbow Dash', 'Rainbow Dash ', 'Rainbow Dash  '],
                                       id='best-pony', labelClassName='label'))
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

    @property
    @abstractmethod
    def characters_metadata(self):
        # Return a dictionary containing metadata about all downloadable character models for this architecture and the
        # URLs for downloading them.
        return character_models

    @property
    @abstractmethod
    def multi_speaker_models_metadata(self):
        # Return a dictionary containing metadata about all downloadable multi-speaker models for this architecture and
        # the URLs for downloading them.
        return multi_speaker_models

    @property
    def downloadable_characters(self):
        # A sorted list of all downloadable characters, minus the ones that are already downloaded.
        full_list = [character['Model Name'] for character in self.characters_metadata]
        already_downloaded = self.characters
        return sorted(list(set(full_list).difference(set(already_downloaded))))

    @property
    def tab_contents(self):
        return html.Tr([
            html.Td([
                html.Tr(self.description),
                html.Tr(self.requirements)
            ], className='architecture-info'),
            html.Td([
                html.Div([
                    html.Button(SHOW_CHARACTER_DOWNLOAD_MENU, id=self.id + '-download-menu-button'),
                    dbc.Collapse([
                        html.Table([
                            html.Colgroup([
                                # todo: move styling to a css file
                                html.Col(span=1, style={'width': '10%'}),
                                html.Col(span=1, style={'width': '90%'}),
                            ]),
                            html.Tr([
                                html.Td(),
                                html.Td(dcc.Checklist(self.downloadable_characters, id=self.id + '-download-checklist', inputStyle={'margin-right': '10px'}, labelStyle={'margin-top': '5px'}))
                            ]),
                        ]),
                        html.Div([
                            html.Br(),
                            html.Div('Total Download Size: 0 bytes', id=self.id + '-download-size', style={'margin': '5px'}),
                            html.Button('Download Selected Models', style={'margin': '5px'}),
                        ], className='centered')
                    ], is_open=False, id=self.id + "-download-menu", className='model-list-expanded'),
                ], className='model-list-div'),
                self.options,
            ])
        ], id=self.id, hidden=True)

    @property
    def characters(self):
        # A sorted list of all the characters available for this architecture.
        # Loop through all the directories in model_dirs(architecture_name), call os.listdir(model_dir), and flatten the
        # result into a single list. Character models are expected to be in subdirectories with the characters' names,
        # so ignore files.
        return sorted(
            [os.path.basename(character_path)
             for character_path_list in ([os.path.join(model_dir, character) for character in os.listdir(model_dir)]
                                         for model_dir in hay_say_common.model_dirs(self.id))
             for character_path in character_path_list if not os.path.isfile(character_path)])

    @property
    def character_dropdown(self):
        return dbc.Select(options=self.characters, value=None if len(self.characters) == 0 else self.characters[0],
                          id=self.input_ids[0], className='option-dropdown')

    # Pretend this is annotated like so:
    # @app.callback(
    #     [Output(self.id + '-download-menu-button', 'children'),
    #      Output(self.id + '-download-menu', 'is_open')],
    #     Input(self.id + '-download-menu-button', 'n_clicks'),
    #     State(self.id + '-download-menu', 'is_open'),
    # )
    def toggle_character_download_menu(self, n_clicks, is_open):
        if n_clicks is None:
            raise PreventUpdate
        return SHOW_CHARACTER_DOWNLOAD_MENU if is_open else HIDE_CHARACTER_DOWNLOAD_MENU, not is_open

    # Pretend this is annotated like so:
    # @app.callback(
    #     Output(self.id + '-download-size', 'children'),
    #     Input(self.id + '-download-checklist', 'value')
    # )
    def update_download_size(self, selected_characters):
        if selected_characters is None:
            return 'Total Download Size: 0 bytes'
        character_to_size_dict = {character['Model Name']: sum([file['Size (bytes)'] for file in character['Files']])
                                  for character in self.characters_metadata}
        total_size = 0
        for character in selected_characters:
            total_size += character_to_size_dict[character]
        return 'Total Download Size: ' + str(self.scale_bytes(total_size))

    def scale_bytes(self, size_in_bytes):
        # Convert the given number of bytes into a more human-readable number by scaling it to kB, MB, GB, etc.
        # For example, 1234 becomes "1.21 kB"
        # size_in_bytes must be non-negative. Otherwise, behavior is undefined. The maximum scale is Zettabytes, ZB.
        scales = [(0, 'bytes'), (10, 'kB'), (20, 'MB'), (30, 'GB'), (40, 'TB'), (50, 'PB'), (60, 'EB'), (70, 'ZB')]

        scaled_to_zero_decimals = [size_in_bytes >> scale[0] for scale in scales] + [0]
        index = scaled_to_zero_decimals.index(0) - 1
        index = 0 if index < 0 else index
        scaled_to_two_decimals = "{:.2f}".format(size_in_bytes / pow(2, scales[index][0]))

        # return a different precision for bytes than for other scales
        if index == 0:
            return str(scaled_to_zero_decimals[index]) + ' ' + scales[index][1]
        return scaled_to_two_decimals + ' ' + scales[index][1]


