from dash import html, dcc, Input, Output, callback
from dash.exceptions import PreventUpdate

import model_licenses
from architectures.AbstractTab import AbstractTab


class StyleTTS2Tab(AbstractTab):
    @property
    def id(self):
        return 'styletts_2'

    @property
    def port(self):
        return 6578

    @property
    def label(self):
        return 'StyleTTS 2'

    @property
    def description(self):
        return [html.P('StyleTTS 2 is a text-to-speech framework that uses style diffusion and adversarial training '
                       'with large speech language models'),
                html.P(
                    html.A('https://github.com/yl4579/StyleTTS2',
                           href='https://github.com/yl4579/StyleTTS2')
                    ),
                html.P('Thank you to Vul Traz for leading the charge and providing the first character model.')]

    @property
    def requirements(self):
        return html.P(
            html.Em("This architecture requires a text input. You may optionally provide a reference audio and select "
                    "the \"Enable Reference Audio\" checkbox to make the generated output mimic the reference audio's "
                    "timbre and prosody.")
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
                html.Td(html.Label('Noise', htmlFor=self.input_ids[1]), className='option-label'),
                html.Tr([
                    html.Td(dcc.Input(id=self.input_ids[1], type='range', min=0, max=3, step=0.1, value=0.3)),
                    html.Td(html.Div('0', id=self.id + '-noise-number')),
                ])
            ], title='Randomness applied to the style predictor. "Style" refers to various vocal qualities such as '
                     'prosody, lexical stress, formant transitions, and speaking rate.'),
            html.Tr([
                html.Td(html.Label('Diffusion Steps', htmlFor=self.input_ids[2]), className='option-label'),
                html.Tr([
                    html.Td(dcc.Input(id=self.input_ids[2], type='number', min=2, max=32, step=1, value=5.0)),
                ])
            ], title="The number of diffusion steps that are applied to predict the text's style. Good quality results "
                     "are observed with as few as 3 steps. The quality does not noticeably increase above 5 steps, "
                     "although diversity of the style increases up until about 16 steps."),
            html.Tr([
                html.Td(html.Label('Embedding Scale', htmlFor=self.input_ids[3]), className='option-label'),
                html.Tr([
                    html.Td(dcc.Input(id=self.input_ids[3], type='range', min=0, max=5, step=0.1, value=1.5)),
                    html.Td(html.Div('0', id=self.id + '-embedding-scale-number')),
                ])
            ], title='Also called the "Classifier-free guidance (CFG) scale". Increasing this value causes the style '
                     'prediction to adhere more closely to the input text, causing it to sound more expressive/'
                     'emotional, but the quality drops off when the value goes too high.'),
            html.Tr([
                html.Td(html.Label('Split Into Sentences', htmlFor=self.input_ids[4]), className='option-label'),
                html.Td(dcc.Checklist([''], value=[''], id=self.input_ids[4]))
            ],
                title='Splits the input text into individual sentences, converts each sentence, and merges the results '
                      'back together. The style of one sentence influences the style of the next sentence; the degree '
                      'to which that happens is controlled by the "Style Blend" option.'),
            html.Tr([
                html.Td(html.Label('Style Blend', htmlFor=self.input_ids[5]), className='option-label'),
                html.Tr([
                    html.Td(dcc.Input(id=self.input_ids[5], type='range', min=0, max=1, step=0.1, value=0.5)),
                    html.Td(html.Div('0', id=self.id + '-style-blend-number')),
                ])
            ], title='The degree to which the style of one sentence affects the style of the next sentence. This has '
                     'no effect if "Split Into Sentences" is disabled.'),
            html.Tr([
                html.Td(html.Label('Enable Reference Audio', htmlFor=self.input_ids[6]), className='option-label'),
                html.Td(dcc.Checklist([''], value=[], id=self.input_ids[6]))
            ],
                title=''),
            html.Tr([
                html.Td(html.Label('Blend with Reference Timbre', htmlFor=self.input_ids[7]), className='option-label'),
                html.Tr([
                    html.Td(dcc.Input(id=self.input_ids[7], type='range', min=0, max=1, step=0.1, value=0.5)),
                    html.Td(html.Div('0', id=self.id + '-timbre-blend-number')),
                ])
            ], title="The degree to which the generated audio mimics the timbre of the reference audio. Use higher "
                     "numbers to make the voice of the generated output sound more like the character in the reference "
                     "audio. Note: This value is equal to 1-alpha from StyleTTS's Inference_LibriTTS.ipynb script."),
            html.Tr([
                html.Td(html.Label('Blend with Reference Prosody', htmlFor=self.input_ids[8]), className='option-label'),
                html.Tr([
                    html.Td(dcc.Input(id=self.input_ids[8], type='range', min=0, max=1, step=0.1, value=0.9)),
                    html.Td(html.Div('0', id=self.id + '-prosody-blend-number')),
                ])
            ], title="The degree to which the generated audio mimics the prosody of the reference audio. Use higher "
                     "numbers to make the intonation, stress, rhythm, and speaking pace of the generated output sound "
                     "more like that of the reference audio. Note: This value is equal to 1-beta from StyleTTS's "
                     "Inference_LibriTTS.ipynb script"),
        ], className='spaced-table')

    def register_callbacks(self, enable_model_management):
        super().register_callbacks(enable_model_management)

        def do_adjustment(adjustment):
            if adjustment is None:
                raise PreventUpdate
            # cast to float first, then round to 2 decimal places
            print("{:3.2f}".format(float(adjustment)), flush=True)
            return "{:3.2f}".format(float(adjustment))

        @callback(
            Output(self.id + '-noise-number', 'children'),
            Input(self.input_ids[1], 'value')
        )
        def adjust_noise(adjustment):
            return do_adjustment(adjustment)

        @callback(
            Output(self.id + '-embedding-scale-number', 'children'),
            Input(self.input_ids[3], 'value')
        )
        def adjust_embedding_scale(adjustment):
            return do_adjustment(adjustment)

        @callback(
            Output(self.id + '-style-blend-number', 'children'),
            Input(self.input_ids[5], 'value')
        )
        def adjust_style_blend(adjustment):
            return do_adjustment(adjustment)

        @callback(
            Output(self.id + '-timbre-blend-number', 'children'),
            Input(self.input_ids[7], 'value')
        )
        def adjust_timbre_blend(adjustment):
            return do_adjustment(adjustment)

        @callback(
            Output(self.id + '-prosody-blend-number', 'children'),
            Input(self.input_ids[8], 'value')
        )
        def adjust_prosody_blend(adjustment):
            return do_adjustment(adjustment)

        @callback(
            Output(self.input_ids[5], 'disabled'),
            Input(self.input_ids[4], 'value')
        )
        def disable_style_blend(use_long_form):
            return not use_long_form

        @callback(
            Output(self.input_ids[7], 'disabled'),
            Input(self.input_ids[6], 'value')
        )
        def disable_timbre_blend(use_reference_audio):
            return not use_reference_audio

        @callback(
            Output(self.input_ids[8], 'disabled'),
            Input(self.input_ids[6], 'value')
        )
        def disable_prosoxy_blend(use_reference_audio):
            return not use_reference_audio

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

    @property
    def input_ids(self):
        return [self.id+'-character',
                self.id+'-noise',
                self.id+'-diffusion-steps',
                self.id+'-embedding-scale',
                self.id+'-use-long-form',
                self.id+'-style-blend',
                self.id+'-enable-reference-audio',
                self.id+'-timbre-reference-blend',
                self.id+'-prosody-reference-blend',
                ]

    def construct_input_dict(self, *args):
        input_dict = {
            'Architecture': self.id,
            'Character': args[0],
            'Noise': float(args[1]),
            'Diffusion Steps': int(args[2]),
            'Embedding Scale': float(args[3]),
            # Note: A checklist option is initially None, but if you toggle it on and then back off, it becomes an empty
            # list, []. The expression "True if args[x] else False" maps both None and [] to False and [''] to True.
            'Use Long Form': True if args[4] else False,
            'Style Blend': float(args[5]),
            'Enable Reference Audio': True if args[6] else False,
            'Timbre Reference Blend': 1.0 - float(args[7]),
            'Prosody Reference Blend': 1.0 - float(args[8]),
        }
        return input_dict

