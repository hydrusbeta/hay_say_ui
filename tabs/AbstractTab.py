from abc import ABC, abstractmethod
from dash import html, dcc, Output, Input, ctx
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import os

import hay_say_common


class AbstractTab(ABC):

    def __init__(self, app, root_dir):
        self.app = app
        self.root_dir = root_dir
        app.callback(Output(self.input_ids[0], 'value'),
                     Output(self.id + '-character-dropdown', 'label'),
                     [Input(self.id + character, 'n_clicks') for character in self.characters])(self.select_character)

    # Pretend this is annotated like so:
    # @app.callback(
    #     Output(self.input_ids[0], 'value'),  # This stores the pony name and is later used by the "Generate!" button.
    #     Output(self.id + '-character-dropdown', 'label'),  # This is just a label for displaying the selected pony.
    #     [Input(self.id + character, 'n_clicks') for character in self.characters]
    # )
    def select_character(self, *_):
        if ctx.triggered_id is None:
            raise PreventUpdate
        # The Character IDs are all self.id + <CharacterName>. Strip off self.id
        selected_character = ctx.triggered_id[len(self.id):]
        return selected_character, selected_character

    @property
    @abstractmethod
    def id(self):
        # A unique string for identifying this tab in code. It is used as the 'value' attribute of the dcc.Tab object as
        # well as the id of the html element containing the tab contents. The hostname of the container running the ai
        # is <id>_server.
        return 'an-abstract-tab'

    @property
    @abstractmethod
    def port(self):
        # The port number that the container running the ai architecture uses
        return 8080

    @property
    @abstractmethod
    def label(self):
        # The tab name that is displayed to the user. It is used as the 'label' attribute of the dcc.Tab object.
        return 'An Abstract Tab'

    @property
    @abstractmethod
    def description(self):
        return [html.P('Put a general description of the AI architecture here'),
                html.P(
                    html.A("Put a link to the architecture's source code or website here")
                )]

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
                html.Td(dcc.Dropdown(options=[
                    'Purple Smart',
                    'Ponkers',
                    'Blue Fast',
                    'Yellow Shy',
                    'Good Apple',
                    'Marshmallow'
                ], value='Purple Smart', clearable=False, className='dropdown'))
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
    def tab_contents(self):
        return html.Tr([
            html.Td([
                html.Tr(self.description),
                html.Tr(self.requirements)
            ], className='architecture-info'),
            html.Td(self.options, className='tab-row')
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
        return html.Div([
            dbc.DropdownMenu(
                [dbc.DropdownMenuItem(character, id=self.id + character) for character in self.characters],
                id=self.id + '-character-dropdown', label=None if len(self.characters) == 0 else self.characters[0]),
            # This is a bit of a kludge. We can't just use the DropDownMenu's label to store the name of the selected
            # character. The character name needs to be stored in a component that has a "value" property, so a hidden
            # dcc.Input component is added here and the character name is copied to it in the select_character callback.
            dcc.Input(self.characters[0], id=self.input_ids[0], style={'display': 'none'})
        ])
