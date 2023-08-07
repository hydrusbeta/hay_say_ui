import os

from architectures.AbstractTab import AbstractTab
from hay_say_common import get_model_path

from dash import html, dcc, Input, Output, callback
from dash.exceptions import PreventUpdate

import dash_bootstrap_components as dbc


class RvcTab(AbstractTab):
    @property
    def id(self):
        return 'rvc'

    @property
    def port(self):
        return 6578

    @property
    def label(self):
        return 'RVC'

    @property
    def description(self):
        return [html.P('RVC is a simple voice conversion framework based on VITS'),
                html.P(
                    html.A('https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI',
                           href='https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI')
                    ),
                html.P('Thank you to Vul Traz, ThunderAnon, Kindont, Anony Ken, and Music Box 67 for providing the character models')]

    @property
    def requirements(self):
        return html.P(
            html.Em('This architecture requires a voice recording input. Text inputs are ignored.')
        )

    def meets_requirements(self, user_text, user_audio, selected_character):
        return user_audio is not None and selected_character is not None

    @property
    def options(self):
        return html.Table([
            html.Tr([
                html.Td(html.Label('Character', htmlFor=self.input_ids[0]), className='option-label'),
                html.Td(self.character_dropdown)
            ]),
            html.Tr([
                html.Td(html.Label('Shift Pitch (semitones)', htmlFor=self.input_ids[1]), className='option-label'),
                html.Td(dcc.Input(id=self.input_ids[1], type='number', min=-36, max=36, step=1, value=0))
            ], title='Also called "transform". Adjusts the pitch of the generated audio in semitones. For male to '
                     'female voice conversion, a value of around 12 is recommended.'),
            html.Tr([
                html.Td(html.Label('f0 Extraction Method', htmlFor=self.input_ids[2]), className='option-label'),
                html.Td(dbc.Select(options=['crepe', 'harvest', 'parselmouth'], id=self.input_ids[2],
                                   className='option-dropdown', value='harvest'))
            ], title='Select a method for extracting fundamentals frequencies. parselmouth is the fastest, but crepe '
                     'and harvest tend to produce higher quality results.'),
            html.Tr([
                html.Td(html.Label('Filter Radius', htmlFor=self.input_ids[3]), className='option-label'),
                html.Tr([
                    html.Td(dcc.Input(type='range', min=0, max=20, value="3", id=self.input_ids[3], step='1')),
                    html.Td(html.Div('0', id='filter-radius-number')),
                ])
            ], title='The degree to which median filtering is applied, which can help reduce metallic/raspy artifacts. '
                     'A value of 2 or less disables this feature. This feature is only available if the f0 Extraction '
                     'method is set to "harvest".'),
            html.Tr([
                html.Td(html.Label('Character Similarity', htmlFor=self.input_ids[4]), className='option-label'),
                html.Tr([
                    html.Td(dcc.Input(type='range', min=0, max=1, value="0.88", id=self.input_ids[4], step='0.01')),
                    html.Td(html.Div('0', id='rvc-character-likeness-number')),
                ])
            ], title='Also called the "Index Rate." Values closer to 1 will cause the output to mimic the timbre of '
                     'the character more closely, by adjusting the extracted audio features towards patterns that were '
                     'observed during training. If this feature is disabled, it means that no .index file was provided '
                     'with the character model.'),
            html.Tr([
                html.Td(html.Label('Voice Envelope Mix Ratio', htmlFor=self.input_ids[5]), className='option-label'),
                html.Tr([
                    html.Td(dcc.Input(type='range', min=0, max=1, value="1", id=self.input_ids[5], step='0.01')),
                    html.Td(html.Div('0', id='voice-envelope-mix-ratio-number')),
                ])
            ], title="Values closer to 0 will reshape the volume envelope of the output to more closely match the "
                     "volume envelope of the input. A value of 1 will leave the output's volume envelope alone."),
            html.Tr([
                html.Td(html.Label('Voiceless Consonants Protection Ratio', htmlFor=self.input_ids[6]), className='option-label'),
                html.Tr([
                    html.Td(dcc.Input(type='range', min=0, max=0.5, value="0.33", id=self.input_ids[6], step='0.01')),
                    html.Td(html.Div('0', id='voiceless-consonants-protection-ratio-number')),
                ])
            ], title="Protects voiceless speech to prevent certain artifacts. Lower values add more protection. A "
                     "value of 0.5 disables this feature."),
        ], className='spaced-table')

    def register_callbacks(self, enable_model_management):
        super().register_callbacks(enable_model_management)

        @callback(
            Output('filter-radius-number', 'children'),
            Input(self.input_ids[3], 'value')
        )
        def adjust_filter_radius(adjustment):
            return adjustment

        @callback(
            Output('rvc-character-likeness-number', 'children'),
            Input(self.input_ids[4], 'value')
        )
        def adjust_character_likeness(adjustment):
            if adjustment is None:
                raise PreventUpdate
            # cast to float first, then round to 2 decimal places
            return "{:3.2f}".format(float(adjustment))

        @callback(
            Output('voice-envelope-mix-ratio-number', 'children'),
            Input(self.input_ids[5], 'value')
        )
        def adjust_voice_envelope_mix_ratio(adjustment):
            if adjustment is None:
                raise PreventUpdate
            # cast to float first, then round to 2 decimal places
            return "{:3.2f}".format(float(adjustment))

        @callback(
            Output('voiceless-consonants-protection-ratio-number', 'children'),
            Input(self.input_ids[6], 'value')
        )
        def adjust_voiceless_consonants_protection_ratio(adjustment):
            if adjustment is None:
                raise PreventUpdate
            # cast to float first, then round to 2 decimal places
            return "{:3.2f}".format(float(adjustment))

        @callback(
            Output(self.input_ids[3], 'disabled'),
            Input(self.input_ids[2], 'value')
        )
        def disable_filter_radius(f0_extraction_method):
            return not f0_extraction_method == 'harvest'

        @callback(
            Output(self.input_ids[4], 'disabled'),
            Input(self.input_ids[0], 'value')
        )
        def disable_character_likeness(character):
            if character is None:
                raise PreventUpdate
            index_path = self.get_index_path(character)
            return not os.path.isfile(index_path)

    def get_index_path(self, character):
        character_dir = get_model_path(self.id, character)
        return os.path.join(character_dir, character + '.index')

    @property
    def input_ids(self):
        return [self.id+'-character',
                self.id+'-pitch-shift',
                self.id+'-f0-extraction-method',
                self.id+'-filter-radius',
                self.id+'-character-likeness',
                self.id+'-voice-envelope-mix-ratio',
                self.id+'-voiceless-consonants-protection-ratio',
                ]

    def construct_input_dict(self, *args):
        input_dict = {
            'Architecture': self.id,
            'Character': args[0],
            'Pitch Shift': int(args[1]),
            'f0 Extraction Method': args[2],
            'Index Ratio': float(args[4]),
            'Voice Envelope Mix Ratio': float(args[5]),
            'Voiceless Consonants Protection Ratio': float(args[6]),
        }
        if args[2] == 'harvest':
            input_dict['Filter Radius'] = int(args[3])
        return input_dict

