import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback, ctx
from dash.exceptions import PreventUpdate

import requests
import model_licenses
from architectures.AbstractTab import AbstractTab


class MossTTSTab(AbstractTab):
    @property
    def id(self):
        return 'moss_tts'

    @property
    def port(self):
        return 6582

    @property
    def label(self):
        return 'Moss TTS'

    @property
    def description(self):
        return [html.P('Moss-TTS is a text-to-speech model developed by MOSI.AI and the OpenMOSS team. In this implementation, Moss-TTS has been fine-tuned on pony voices, and has been combined with emotion embeddings (cirimus/modernbert-base-go-emotions) and an iSTFTNet2 vocoder customized by Delta.'),
                html.P(
                    html.A('https://huggingface.co/ZDisket/MOSS-TTS-PNY',
                           href='https://huggingface.co/ZDisket/MOSS-TTS-PNY')
                    ),
                html.P('Thank you to Delta, for adding emotion control and providing the first fine-tuned model')]

    @property
    def requirements(self):
        return html.P(
            html.Em('This architecture requires text input. Audio inputs are not used.')
        )

    def meets_requirements(self, user_text, user_audio, selected_character):
        return user_text is not None and selected_character is not None

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
                html.Td(html.Label('Emotion', htmlFor=self.input_ids[1]), className='option-label'),
                html.Td(dbc.Select(options=['todo'], id=self.input_ids[1], className='option-dropdown', value='todo'))
            ]),
            html.Tr([
                html.Td(html.Label('Emotion Energy', htmlFor=self.input_ids[2]), className='option-label'),
                html.Tr([
                    html.Td(dcc.Input(id=self.input_ids[2], type='range', min=0, max=1, value="0.50", step='0.01')),
                    html.Td(dcc.Input(id=self.id + '-emotion-energy-number', type='number', min=0, max=1, value="0.50", step='0.01')),
                ])
            ], title='A higher energy produces output that more strongly expresses the selected emotion'),
            # html.Tr([ # todo: This input is disabled because it currently does nothing in MOSS-TTS-PNY.
            #     html.Td(html.Label('Style Text', htmlFor=self.input_ids[1]), className='option-label'),
            #     html.Td(dcc.Textarea(id=self.input_ids[1], placeholder="Todo: fill in a hint here"))],
            #     title='Todo: fill in a tooltip here'),
            html.Tr([
                html.Td(html.Label('Audio Temperature', htmlFor=self.input_ids[3]), className='option-label'),
                html.Tr([
                    html.Td(dcc.Input(id=self.input_ids[3], type='range', min=0.01, max=2.00, value="0.80", step='0.01')),
                    html.Td(dcc.Input(id=self.id + '-audio-temperature-number', type='number', min=0.01, max=2.00, value="0.80", step='0.01')),
                ])
            ], title='Divides logits by this number before applying softmax. higher temperature = flatter distribution of logits, so the code is more likely to select an unusual token output. In other words, higher temperature = the output is more "creative". Lower temperature = the output is more predictable / typical.'),
            html.Tr([
                html.Td(html.Label('Audio Top-K', htmlFor=self.input_ids[4]), className='option-label'),
                html.Tr([
                    html.Td(dcc.Input(id=self.input_ids[4], type='range', min=0, max=200, value="50", step='1')),
                    html.Td(dcc.Input(id=self.id + '-audio-top-k-number', type='number', min=0, max=200, value="50", step='1')),
                ])
            ], title='Only consider the first k logits with the highest probability. Give everything else a probability of zero. This prevents high-temperature sampling from going too wild and picking too many unusual tokens. A value of zero disables this feature. This is applied after applying "temperature".'),
            html.Tr([
                html.Td(html.Label('Audio Top-P', htmlFor=self.input_ids[5]), className='option-label'),
                html.Tr([
                    html.Td(dcc.Input(id=self.input_ids[5], type='range', min=0.01, max=1.00, value="1.00", step='0.01')),
                    html.Td(dcc.Input(id=self.id + '-audio-top-p-number', type='number', min=0.01, max=1.00, value="1.00", step='0.01')),
                ])
            ], title=' Gather only the highest-probability logits until their cumulative probability just exceeds this value. Give everything else a probability of zero, and then renormalize the probabilities. Similar to Top-k, This prevents the selection of the least likely tokens, thereby preventing unusual outputs. Lower values have a greater effect. A value of 1 causes this parameter to have no effect at all. This is applied after applying "top-k".'),
            html.Tr([
                html.Td(html.Label('Repetition Penalty', htmlFor=self.input_ids[6]), className='option-label'),
                html.Tr([
                    html.Td(dcc.Input(id=self.input_ids[6], type='range', min=0.5, max=2.00, value="1.05", step='0.01')),
                    html.Td(dcc.Input(id=self.id + '-repetition-penalty-number', type='number', min=0.5, max=2.00, value="1.05", step='0.01')),
                ])
            ], title='Discourages the generation of audio loops in the output. Higher values = fewer loops. A value of 1 means no penalty. A value less than 1 encourages repetition.'),
            html.Tr([
                html.Td(html.Label('RVQ Codebook layers', htmlFor=self.input_ids[7]), className='option-label'),
                html.Tr([
                    html.Td(dcc.Input(id=self.input_ids[7], type='range', min=1, max=32, value="32", step='1')),
                    html.Td(dcc.Input(id=self.id + '-rvq_codebook-layers-number', type='number', min=1, max=32, value="32", step='1')),
                ])
            ], title='"Residual Vector Quantization" codebook layers. A higher number increases quality, but at the cost of slower inference speed.'),
            # html.Tr([ # todo: This input is disabled because it currently does nothing in MOSS-TTS-PNY as far as I can tell.
            #     html.Td(html.Label('Language', htmlFor=self.input_ids[2]), className='option-label'),
            #     html.Td(dbc.Select(options=['put languages here'], id=self.input_ids[2], className='option-dropdown', value='en'))
            # ], title='Todo: fill in a tooltip here'),
        ], className='spaced-table')

    def available_emotions(self, character):
        response = requests.get(f'http://{self.id + "_server"}:{self.port}/available-traits/{character}')
        code = response.status_code

        if code != 200:
            # Something probably went wrong, so log a message and assume that no emotions are available.
            print(
                f'Warning! available_precomputed_traits returned the unexpected http code {code}. Assuming no '
                f'precomputed traits are available. Please inform the maintainers of Hay Say.')
            return []
        else:
            return response.json()

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
            [Output(self.input_ids[1], 'options'),
             Output(self.input_ids[1], 'value')],
            [Input(self.input_ids[0], 'value')]
        )
        def update_emotion_options(character):
            options = self.available_emotions(character) if character else []
            selected_option = options[0] if options else None
            return options, selected_option

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

        @callback(
            Output(self.input_ids[2], 'value'),
            Output(self.id + '-emotion-energy-number', 'value'),
            Input(self.input_ids[2], 'value'),
            Input(self.id + '-emotion-energy-number', 'value')
        )
        def adjust_emotion_energy(slider_value, input_value):
            trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
            value = do_adjustment(slider_value if trigger_id == self.input_ids[2] else input_value)
            return value, value

        @callback(
            Output(self.input_ids[3], 'value'),
            Output(self.id + '-audio-temperature-number', 'value'),
            Input(self.input_ids[3], 'value'),
            Input(self.id + '-audio-temperature-number', 'value')
        )
        def adjust_audio_temperature(slider_value, input_value):
            trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
            value = do_adjustment(slider_value if trigger_id == self.input_ids[3] else input_value)
            return value, value

        @callback(
            Output(self.input_ids[4], 'value'),
            Output(self.id + '-audio-top-k-number', 'value'),
            Input(self.input_ids[4], 'value'),
            Input(self.id + '-audio-top-k-number', 'value')
        )
        def adjust_audio_top_k(slider_value, input_value):
            trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
            value = do_adjustment_int(slider_value if trigger_id == self.input_ids[4] else input_value)
            return value, value

        @callback(
            Output(self.input_ids[5], 'value'),
            Output(self.id + '-audio-top-p-number', 'value'),
            Input(self.input_ids[5], 'value'),
            Input(self.id + '-audio-top-p-number', 'value')
        )
        def adjust_audio_top_p(slider_value, input_value):
            trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
            value = do_adjustment(slider_value if trigger_id == self.input_ids[5] else input_value)
            return value, value

        @callback(
            Output(self.input_ids[6], 'value'),
            Output(self.id + '-repetition-penalty-number', 'value'),
            Input(self.input_ids[6], 'value'),
            Input(self.id + '-repetition-penalty-number', 'value')
        )
        def adjust_repetition_penalty(slider_value, input_value):
            trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
            value = do_adjustment(slider_value if trigger_id == self.input_ids[6] else input_value)
            return value, value

        @callback(
            Output(self.input_ids[7], 'value'),
            Output(self.id + '-rvq_codebook-layers-number', 'value'),
            Input(self.input_ids[7], 'value'),
            Input(self.id + '-rvq_codebook-layers-number', 'value')
        )
        def adjust_rvq_codebook_layers(slider_value, input_value):
            trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
            value = do_adjustment_int(slider_value if trigger_id == self.input_ids[7] else input_value)
            return value, value

    @property
    def input_ids(self):
        return [self.id+'-character',
                # self.id+'-style-text',
                # self.id+'-language',
                self.id+'-emotion',
                self.id+'-emotion-energy',
                self.id+'-audio-temperature',
                self.id+'-audio-top-k',
                self.id+'-audio-top-p',
                self.id+'-repetition-penalty',
                self.id+'-rvq-codebook-layers',
                ]

    def construct_input_dict(self, session_data, *args):
        input_dict = {
            'Architecture': self.id,
            'Character': args[0],
            'Style Text': '', # args[1], # todo: This input is disabled because it currently does nothing in MOSS-TTS-PNY.
            'Language': 'en', # args[2], # todo: This input is disabled because it currently does nothing in MOSS-TTS-PNY as far as I can tell.
            'Emotion': args[1],
            'Emotion Energy': float(args[2]),
            'Audio Temperature': float(args[3]),
            'Audio Top-K': int(args[4]),
            'Audio Top-P': float(args[5]),
            'Repetition Penalty': float(args[6]),
            'RVQ Codebook Layers': int(args[7]),
        }
        return input_dict

