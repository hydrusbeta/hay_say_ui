import os

import dash_bootstrap_components as dbc
import hay_say_common as hsc
from dash import html, dcc, Input, Output, callback, ctx
from dash.exceptions import PreventUpdate

import model_licenses
from architectures.AbstractTab import AbstractTab


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
            html.Tr(
                html.Td(id=self.id + '-license-note', colSpan=2),
                id=self.id + '-license-row', hidden=True
            ),
            html.Tr([
                html.Td(html.Label('Shift Pitch (semitones)', htmlFor=self.input_ids[1]), className='option-label'),
                html.Td(dcc.Input(id=self.input_ids[1], type='number', min=-36, max=36, step=1, value=0))
            ], title='Also called "transform". Adjusts the pitch of the generated audio in semitones. For male to '
                     'female voice conversion, a value of around 12 is recommended.'),
            html.Tr([
                html.Td(html.Label('f0 Extraction Method', htmlFor=self.input_ids[2]), className='option-label'),
                html.Td(dbc.Select(options=['crepe', 'harvest', 'parselmouth', 'rmvpe'], id=self.input_ids[2],
                                   className='option-dropdown', value='harvest'))
            ], title='Select a method for extracting fundamentals frequencies. parselmouth is the fastest, but crepe '
                     'and harvest tend to produce higher quality results.'),
            html.Tr([
                html.Td(html.Label('Filter Radius', htmlFor=self.input_ids[3]), className='option-label'),
                html.Tr([
                    html.Td(dcc.Input(id=self.input_ids[3], type='range', min=0, max=20, value="3", step='1')),
                    html.Td(dcc.Input(id=self.id + '-filter-radius-number', type='number', min=0, max=20, value="3", step='1')),
                ])
            ], title='The degree to which median filtering is applied, which can help reduce metallic/raspy artifacts. '
                     'A value of 2 or less disables this feature. This feature is only available if the f0 Extraction '
                     'method is set to "harvest".'),
            html.Tr([
                html.Td(html.Label('Character Similarity', htmlFor=self.input_ids[4]), className='option-label'),
                html.Tr([
                    html.Td(dcc.Input(id=self.input_ids[4], type='range', min=0, max=1, value="0.88", step='0.01')),
                    html.Td(dcc.Input(id=self.id + '-character-likeness-number', type='number', min=0, max=1, value="0.88", step='0.01')),
                ])
            ], title='Also called the "Index Rate." Values closer to 1 will cause the output to mimic the timbre of '
                     'the character more closely, by adjusting the extracted audio features towards patterns that were '
                     'observed during training. If this feature is disabled, it means that no .index file was provided '
                     'with the character model.'),
            html.Tr([
                html.Td(html.Label('Voice Envelope Mix Ratio', htmlFor=self.input_ids[5]), className='option-label'),
                html.Tr([
                    html.Td(dcc.Input(id=self.input_ids[5], type='range', min=0, max=1, value="1", step='0.01')),
                    html.Td(dcc.Input(id=self.id + '-voice-envelope-mix-ratio-number', type='number', min=0, max=1, value="1", step='0.01')),
                ])
            ], title="Values closer to 0 will reshape the volume envelope of the output to more closely match the "
                     "volume envelope of the input. A value of 1 will leave the output's volume envelope alone."),
            html.Tr([
                html.Td(html.Label('Voiceless Consonants Protection Ratio', htmlFor=self.input_ids[6]), className='option-label'),
                html.Tr([
                    html.Td(dcc.Input(id=self.input_ids[6], type='range', min=0, max=0.5, value="0.33", step='0.01')),
                    html.Td(dcc.Input(id=self.id + '-voiceless-consonants-protection-ratio-number', type='number', min=0, max=0.5, value="0.33", step='0.01')),
                ])
            ], title="Protects voiceless speech to prevent certain artifacts. Lower values add more protection. A "
                     "value of 0.5 disables this feature."),
        ], className='spaced-table')

    def register_callbacks(self, enable_model_management):
        super().register_callbacks(enable_model_management)

        def do_adjustment(adjustment):
            if adjustment is None:
                raise PreventUpdate
            # cast to float first, then round to 2 decimal places
            return "{:3.2f}".format(float(adjustment))

        def do_adjustment_int(adjustment):
            if adjustment is None:
                raise PreventUpdate
            return adjustment

        @callback(
            Output(self.input_ids[3], 'value'),
            Output(self.id + '-filter-radius-number', 'value'),
            Input(self.input_ids[3], 'value'),
            Input(self.id + '-filter-radius-number', 'value')
        )
        def adjust_filter_radius(slider_value, input_value):
            trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
            value = do_adjustment_int(slider_value if trigger_id == self.input_ids[3] else input_value)
            return value, value

        @callback(
            Output(self.input_ids[4], 'value'),
            Output(self.id + '-character-likeness-number', 'value'),
            Input(self.input_ids[4], 'value'),
            Input(self.id + '-character-likeness-number', 'value')
        )
        def adjust_character_likeness(slider_value, input_value):
            trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
            value = do_adjustment(slider_value if trigger_id == self.input_ids[4] else input_value)
            return value, value

        @callback(
            Output(self.input_ids[5], 'value'),
            Output(self.id + '-voice-envelope-mix-ratio-number', 'value'),
            Input(self.input_ids[5], 'value'),
            Input(self.id + '-voice-envelope-mix-ratio-number', 'value')
        )
        def adjust_voice_envelope_mix_ratio(slider_value, input_value):
            trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
            value = do_adjustment(slider_value if trigger_id == self.input_ids[5] else input_value)
            return value, value

        @callback(
            Output(self.input_ids[6], 'value'),
            Output(self.id + '-voiceless-consonants-protection-ratio-number', 'value'),
            Input(self.input_ids[6], 'value'),
            Input(self.id + '-voiceless-consonants-protection-ratio-number', 'value')
        )
        def adjust_voiceless_consonants_protection_ratio(slider_value, input_value):
            trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
            value = do_adjustment(slider_value if trigger_id == self.input_ids[6] else input_value)
            return value, value

        @callback(
            Output(self.input_ids[3], 'disabled'),
            Output(self.id + '-filter-radius-number', 'disabled'),
            Input(self.input_ids[2], 'value')
        )
        def disable_filter_radius(f0_extraction_method):
            disabled = not f0_extraction_method == 'harvest'
            return disabled, disabled

        @callback(
            Output(self.input_ids[4], 'disabled'),
            Output(self.id + '-character-likeness-number', 'disabled'),
            Input(self.input_ids[0], 'value')
        )
        def disable_character_likeness(character):
            if character is None:
                raise PreventUpdate
            index_paths = self.get_index_paths(character)
            disabled = len(index_paths) == 0
            return disabled, disabled

        @callback(
            [Output(self.id + '-license-note', 'children'),
             Output(self.id + '-license-row', 'hidden')],
            Input(self.input_ids[0], 'value')
        )
        def show_license_note(character):
            model_metadata = next(iter([model_info for model_info in self.read_character_model_infos()
                                        if model_info['Model Name'] == character]), {})
            license_name = model_metadata.get('License')
            license_enum = model_licenses.get_license_enum(license_name)
            additional_text = model_metadata.get('Creator')
            return model_licenses.get_verbiage(license_enum, additional_text), \
                not model_licenses.is_ui_notice_required(license_enum)

    def get_index_paths(self, character):
        # Note: Hay Say only supports one index path. The UI just checks whether there's 0 or not.
        character_dir = hsc.character_dir(self.id, character)
        return hsc.get_files_with_extension(character_dir, '.index')

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

    def construct_input_dict(self, session_data, *args):
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

