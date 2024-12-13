import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback, ctx
from dash.exceptions import PreventUpdate
from hay_say_common.cache import Stage

import requests
import model_licenses
from architectures.AbstractTab import AbstractTab

USE_PRECOMPUTED_EMBEDDING = 'Use Precomputed Embeddings'
USE_REFERENCE_AUDIO = "Use Reference Audio"

class GPTSoVITSTab(AbstractTab):
    @property
    def id(self):
        return 'gpt_so_vits'

    @property
    def port(self):
        return 6581

    @property
    def label(self):
        return 'GPT SoVITS'

    @property
    def description(self):
        return [html.P('GPT SoVITS is a project focused on text-to-speech and cross-language inference, with support '
                       'for several languages.'),
                html.P(
                    html.A('https://github.com/RVC-Boss/GPT-SoVITS',
                           href='https://github.com/RVC-Boss/GPT-SoVITS')
                    ),
                html.P('Thank you to Vul Traz for leading the charge and providing the first pony character models.')]

    @property
    def requirements(self):
        return html.P(
            html.Em("This architecture requires a text input. You must also do one of the following: 1. Select a trait/"
                    "emotion from a dropdown list or 2. provide at least one reference audio of the character "
                    "speaking. If you provide a reference audio, the character's \"tone\" in that file will be "
                    "mimicked in the generated output. you may optionally provide a transcription of that reference.")
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
                html.Td(html.Label('Reference Option', htmlFor=self.input_ids[12]), className='option-label'),
                html.Td(dcc.RadioItems(value=USE_PRECOMPUTED_EMBEDDING, id=self.input_ids[12]))
            ]),
            html.Tr([
                html.Td(dbc.Collapse(html.Label('Trait', htmlFor=self.input_ids[11]), id=self.id+'-precomputed-style-dropdowns-1a'),
                        className='option-label', style={'width': '20%'}),
                html.Td(dbc.Collapse(dbc.Select(
                    className='option-dropdown',
                    id=self.input_ids[11]), id=self.id+'-precomputed-style-dropdowns-1b'))
            ]),
            html.Tr([
                html.Td(dbc.Collapse(html.Label('Reference audio of the character speaking', htmlFor=self.input_ids[1]), id=self.id+'-precomputed-style-dropdowns-2a'),
                        className='option-label'),
                html.Td(dbc.Collapse(dbc.Select(className='option-dropdown', id=self.input_ids[1]), id=self.id+'-precomputed-style-dropdowns-2b'))],
                title="A reference audio whose tone/emotion you want the generated audio to mimic. Upload audio files in the Input section at the top of this page to add more options to this dropdown list."
            ),
            html.Tr([
                html.Td(dbc.Collapse(html.Label('Reference Text', htmlFor=self.input_ids[2]), id=self.id+'-precomputed-style-dropdowns-2c'), className='option-label'),
                html.Td(dbc.Collapse(dcc.Textarea(id=self.input_ids[2],
                                     placeholder="Optionally enter a transcription of the reference audio."), id=self.id+'-precomputed-style-dropdowns-2d'))],
                title="A transcription of the reference audio."),
            html.Tr([
                html.Td(dbc.Collapse(html.Label('Language spoken in the reference audio', htmlFor=self.input_ids[3]), id=self.id+'-precomputed-style-dropdowns-2e'),
                        className='option-label'),
                html.Td(dbc.Collapse(dbc.Select(className='option-dropdown', id=self.input_ids[3],
                                                options=['Chinese (Mandarin)', 'English', 'Japanese',
                                                         'Chinese (Cantonese)', 'Korean', 'Mandarin-English Mix',
                                                         'Japanese-English Mix', 'Cantonese-English Mix',
                                                         'Korean-English Mix', 'Auto Multilingual',
                                                         'Auto Multilingual (Cantonese)'], value='English'),
                                     id=self.id+'-precomputed-style-dropdowns-2f'))],
                title="The language of the reference audio. Seeing as how all the character models available so far were voiced in English, you almost certainly should set this parameter to English."
            ),
            # todo: Additional Reference Audios are maybe a future enhancement
            html.Tr([
                html.Td(dbc.Collapse(html.Label('Additional Reference Audios', htmlFor=self.input_ids[4]), id=self.id+'-precomputed-style-dropdowns-2g'),
                        className='option-label'),
                html.Td(dbc.Collapse(dcc.Checklist([''], value=[''], id=self.input_ids[4]), id=self.id+'-precomputed-style-dropdowns-2h'))],
                title="Additional reference audios. The character's \"tone\" in all the files will be averaged together and be mimicked in the generated output.",
                hidden=True
            ),
            html.Tr([
                html.Td(html.Label('Desired language of generated audio', htmlFor=self.input_ids[5]), className='option-label'),
                html.Td(dbc.Select(className='option-dropdown', id=self.input_ids[5], options=['Chinese (Mandarin)', 'English', 'Japanese', 'Chinese (Cantonese)', 'Korean', 'Mandarin-English Mix', 'Japanese-English Mix', 'Cantonese-English Mix', 'Korean-English Mix', 'Auto Multilingual', 'Auto Multilingual (Cantonese)'], value='English'))], title="The desired language of the generated audio. Please note that Hay Say will not auto-translate your text. The input text you put at the top of this page must be written in the target language."
            ),
            html.Tr([
                html.Td(html.Label('Cutting Strategy', htmlFor=self.input_ids[6]), className='option-label'),
                html.Td(dbc.Select(className='option-dropdown', id=self.input_ids[6], options=["No slicing", "One slice every 4 sentences", "One slice every 50 characters", "Slice by Mandarin Chinese punctuation", "Slice by English punctuation", "Slice by punctuation (any language)"], value='Slice by English punctuation'))], title="The output audio is generated in segments which are then spliced together. This option controls how the prompt is sliced for generating those segments."
            ),
            html.Tr([
                html.Td(html.Label('Top K', htmlFor=self.input_ids[7]), className='option-label'),
                html.Tr([
                    html.Td(dcc.Input(id=self.input_ids[7], type='range', min=1, max=90, step=1, value=15)),
                    html.Td(html.Div('0', id=self.id + '-top_k-number')),
                ])
            ], title='Keeps only the top K logits with the highest probability in a strategy called "top-k filtering".'),
            html.Tr([
                html.Td(html.Label('Top P', htmlFor=self.input_ids[8]), className='option-label'),
                html.Tr([
                    html.Td(dcc.Input(id=self.input_ids[8], type='range', min=0, max=1, step=0.01, value=1)),
                    html.Td(html.Div('0', id=self.id + '-top_p-number')),
                ])
            ], title='Prunes logits whose cumulative probabilities are higher than this value, a general strategy '
                     'called "nucleus filtering".'),
            html.Tr([
                html.Td(html.Label('Temperature', htmlFor=self.input_ids[9]), className='option-label'),
                html.Tr([
                    html.Td(dcc.Input(id=self.input_ids[9], type='range', min=1e-5, max=1, step=0.01, value=1)),
                    html.Td(html.Div('0', id=self.id + '-temperature-number')),
                ])
            ], title='Logits are multiplied by 1/Temperature. This is applied after "Top P" but *before* "Top K"'),
            html.Tr([
                html.Td(html.Label('Speed', htmlFor=self.input_ids[10]), className='option-label'),
                html.Tr([
                    html.Td(dcc.Input(id=self.input_ids[10], type='range', min=0.1, max=5.0, step=0.1, value=1.0)),
                    html.Td(html.Div('0', id=self.id + '-speed-number')),
                ])
            ], title='Modifies the speed of the generated audio, without affecting pitch. Higher number = faster.')
        ], className='spaced-table')

    def available_precomputed_traits(self, character):
        response = requests.get(f'http://{self.id + "_server"}:{self.port}/available-traits/{character}')
        code = response.status_code

        if code != 200:
            # Something probably went wrong, so log a message and assume that no precomputation file is available.
            print(
                f'Warning! available_precomputed_traits returned the unexpected http code {code}. Assuming no '
                f'precomputed traits are available. Please inform the maintainers of Hay Say.')
            return []
        else:
            return response.json()

    def construct_trait_options(self, disabled_options):
        return [
            {
                "label": html.Span(USE_PRECOMPUTED_EMBEDDING, style={'padding-left': '10px'},
                                   title='Select from among pre-computed embeddings for specific emotions/traits. '
                                         'If this option is not selectable, it means that pre-computed embeddings are '
                                         'not available.'),
                "value": USE_PRECOMPUTED_EMBEDDING,
                "disabled": USE_PRECOMPUTED_EMBEDDING in disabled_options
            },
            {
                "label": html.Span(USE_REFERENCE_AUDIO, style={'padding-left': '10px'},
                                   title='Upload a reference audio and optionally provide a transcription.'),
                "value": USE_REFERENCE_AUDIO,
                "disabled": USE_REFERENCE_AUDIO in disabled_options
            }
        ]

    def register_callbacks(self, enable_model_management):
        super().register_callbacks(enable_model_management)

        def do_adjustment(adjustment):
            if adjustment is None:
                raise PreventUpdate
            # cast to float first, then round to 2 decimal places
            return "{:3.2f}".format(float(adjustment))

        @callback(
            Output(self.id + '-top_k-number', 'children'),
            Input(self.input_ids[7], 'value')
        )
        def adjust_top_k(adjustment):
            return do_adjustment(adjustment)

        @callback(
            Output(self.id + '-top_p-number', 'children'),
            Input(self.input_ids[8], 'value')
        )
        def adjust_top_p(adjustment):
            return do_adjustment(adjustment)

        @callback(
            Output(self.id + '-temperature-number', 'children'),
            Input(self.input_ids[9], 'value')
        )
        def adjust_temperature(adjustment):
            return do_adjustment(adjustment)

        @callback(
            Output(self.id + '-speed-number', 'children'),
            Input(self.input_ids[10], 'value')
        )
        def adjust_speed(adjustment):
            return do_adjustment(adjustment)

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
            [Output(self.input_ids[11], 'options'),
             Output(self.input_ids[11], 'value')],
            [Input(self.input_ids[0], 'value')]
        )
        def update_precomputed_trait_options(character):
            options = self.available_precomputed_traits(character) if character else []
            selected_option = options[0] if options else None
            return options, selected_option

        @callback(
            [Output(self.input_ids[12], 'options'),
             Output(self.input_ids[12], 'value')],
            [Input(self.input_ids[0], 'value'),
             State(self.input_ids[12], 'value')]
        )
        def determine_trait_options(model, current_value):
            if model is None:  # Initial call
                return [], None
            disabled_options = []
            if not self.available_precomputed_traits(model):
                disabled_options.append(USE_PRECOMPUTED_EMBEDDING)
            # USE_REFERENCE_AUDIO is a "safe" fallback because it will never be disabled
            new_value = current_value if current_value is not None and current_value not in disabled_options else USE_REFERENCE_AUDIO
            return self.construct_trait_options(disabled_options), new_value

        @callback(
            [Output(self.id+'-precomputed-style-dropdowns-1a', 'is_open'),
             Output(self.id + '-precomputed-style-dropdowns-1b', 'is_open'),
             Output(self.id + '-precomputed-style-dropdowns-2a', 'is_open'),
             Output(self.id + '-precomputed-style-dropdowns-2b', 'is_open'),
             Output(self.id + '-precomputed-style-dropdowns-2c', 'is_open'),
             Output(self.id + '-precomputed-style-dropdowns-2d', 'is_open'),
             Output(self.id + '-precomputed-style-dropdowns-2e', 'is_open'),
             Output(self.id + '-precomputed-style-dropdowns-2f', 'is_open'),
             Output(self.id + '-precomputed-style-dropdowns-2g', 'is_open'),
             Output(self.id+'-precomputed-style-dropdowns-2h', 'is_open')],
            Input(self.input_ids[12], 'value')
        )
        def hide_precomputed_style_options(reference_source):
            if reference_source == USE_PRECOMPUTED_EMBEDDING:
                return True, True, False, False, False, False, False, False, False, False
            elif reference_source == USE_REFERENCE_AUDIO:
                return False, False, True, True, True, True, True, True, True, True
            else:
                return False, False, False, False, False, False, False, False, False, False

    @property
    def input_ids(self):
        return [self.id+'-character',
                self.id+'-reference_audio',
                self.id+'-reference_text',
                self.id+'-reference_language',
                self.id+'-additional_reference_audios',
                self.id+'-target_language',
                self.id+'-cutting_strategy',
                self.id+'-top_k',
                self.id+'-top_p',
                self.id+'-temperature',
                self.id+'-speed',
                self.id+'-trait',
                self.id+'-reference-option'
                ]

    def construct_input_dict(self, session_data, *args):

        input_dict = {
            'Architecture': self.id,
            'Character': args[0],
            'Reference Audio': self.lookup_filehash(self.cache, args[1], session_data),
            'Reference Text': args[2],
            'Reference Language': args[3],
            # Note: A checklist option is initially None, but if you toggle it on and then back off, it becomes an empty
            # list, []. If it's None, let's change it to an empty list instead.
            'Additional Reference Audios': args[4] if args[4] else [],
            'Target Language': args[5],
            'Cutting Strategy': args[6],
            'Top-K': int(args[7]),
            'Top-P': float(args[8]),
            'Temperature': float(args[9]),
            'Speed': float(args[10]),
            'Trait': args[11],
            'Reference Option': args[12]
        }
        input_dict = {k: v for k, v in input_dict.items() if v is not None}  # Removes all entries whose values are None
        return input_dict

    # todo: This is copied from plotly_celery_common. Is there a better DRY way that doesn't involve putting this in its own file just to avoid a circular import?
    def lookup_filehash(self, cache, selected_file, session_data):
        raw_metadata = cache.read_metadata(Stage.RAW, session_data['id'])
        reverse_lookup = {raw_metadata[key]['User File']: key for key in raw_metadata}
        return reverse_lookup.get(selected_file)
