from hay_say_common import get_model_path
from architectures.AbstractTab import AbstractTab

from dash import html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate

import os


class SoVitsSvc4Tab(AbstractTab):
    def __init__(self, app, root_dir):
        super().__init__(app, root_dir)
        app.callback(Output('slice-length-number', 'children'),
                     Input(self.input_ids[3], 'value'))(self.adjust_slice_length)
        app.callback(Output('cross-fade-number', 'children'),
                     Input(self.input_ids[4], 'value'))(self.adjust_crossfade_length)
        app.callback(Output('character-likeness-number', 'children'),
                     Input(self.input_ids[5], 'value'))(self.adjust_character_likeness)
        app.callback([Output(self.input_ids[5], 'disabled'),
                      Output(self.input_ids[5], 'value')],
                     Input(self.input_ids[0], 'value'),
                     State(self.input_ids[5], 'value'))(self.disable_character_likeness)
        app.callback(Output(self.input_ids[4], 'disabled'),
                     Input(self.input_ids[3], 'value'))(self.disable_crossfade_length)

    @property
    def id(self):
        return 'so_vits_svc_4'

    @property
    def port(self):
        return 6576

    @property
    def label(self):
        return 'so-vits-svc 4.0'

    @property
    def description(self):
        return [html.P('so-vits-svc achieves a voice conversion effect by extracting "soft speech" features from '
                       'reference audio and passing them to a variational autoencoder.'),
                html.P(
                    html.A('https://github.com/svc-develop-team/so-vits-svc',
                           href='https://github.com/svc-develop-team/so-vits-svc')
                    ),
                html.P('Thank you to Vul Traz, HazySkies, Amo Awesome Art, and OlivineEllva for providing the '
                       'character models')]

    @property
    def requirements(self):
        return html.P(
            html.Em('This architecture requires a voice recording input. Text inputs are ignored.')
        )

    def meets_requirements(self, user_text, user_audio):
        return user_audio is not None

    @property
    def options(self):
        return html.Table([
            html.Tr([
                html.Td("Note: \"PS1\" = PonySinger1 model", colSpan=2, className='centered')
            ]),
            html.Tr([
                html.Td(html.Label('Character', htmlFor=self.input_ids[0]), className='option-label'),
                html.Td(self.character_dropdown)
            ]),
            html.Tr([
                html.Td(html.Label('Shift Pitch (semitones)', htmlFor=self.input_ids[1]), className='option-label'),
                html.Td(dcc.Input(id=self.input_ids[1], type='number', min=-36, max=36, step=1, value=0))
            ], title='Also called "transform". Adjusts the pitch of the generated audio in semitones'),
            html.Tr([
                html.Td(html.Label('Predict Voice Pitch', htmlFor=self.input_ids[2]), className='option-label'),
                html.Td(dcc.Checklist([''], id=self.input_ids[2]))
            ], title="Using an f0 predictor that was trained alongside the main model, predict the character's pitch "
                     "instead of using the reference audio's actual pitch. Note: Keep this disabled for songs."),
            html.Tr([
                html.Td(html.Label('Slice Length (seconds)', htmlFor=self.input_ids[3]), className='option-label'),
                html.Tr([
                    html.Td(dcc.Input(type='range', min=0, max=20, value="0", id=self.input_ids[3], step='0.01')),
                    html.Td(html.Div('0', id='slice-length-number')),
                ])
            ], title="Slice the voice into segments of this length and convert each slice. A value of 0 turns this "
                     "feature off."),
            html.Tr([
                html.Td(html.Label('Cross-Fade Length (seconds)', htmlFor=self.input_ids[4]), className='option-label'),
                html.Tr([
                    html.Td(dcc.Input(type='range', min=0, max=20, value="0", id=self.input_ids[4], step='0.01')),
                    html.Td(html.Div('0', id='cross-fade-number')),
                ])
            ], title="The cross fade overlap between voice slices, in seconds."),
            html.Tr([
                html.Td(html.Label('Character Likeness', htmlFor=self.input_ids[5]), className='option-label'),
                html.Tr([
                    html.Td(dcc.Input(type='range', min=0, max=1, value="0", id=self.input_ids[5], step='0.01')),
                    html.Td(html.Div('0', id='character-likeness-number')),
                ])
            ], title="Also called \"cluster ratio\". Values closer to 1 will cause the output audio to mimic the "
                     "character's timbre more closely, but at the cost of reduced clarity/intelligibility. In general, "
                     "models that were trained with more data can accommodate higher values. If this option is "
                     "disabled, it means that a kmeans file was not provided with the character model so this option "
                     "cannot be used."),
            html.Tr([
                html.Td(html.Label('Reduce Hoarseness', htmlFor=self.input_ids[6]), className='option-label'),
                html.Td(dcc.Checklist([''], id=self.input_ids[6]))
            ], title='Don\'t worry, that\'s Hoarseness with an "a", not Horse-ness :) \nApply "mean pooling" on '
                     'the fundamental frequency (f0) to reduce hoarseness in the output.'),
            html.Tr([
                html.Td(html.Label('Apply nsf_hifigan', htmlFor=self.input_ids[7]), className='option-label'),
                html.Td(dcc.Checklist([''], id=self.input_ids[7]))
            ], title='Runs the output audio through an additional AI network, nsf_hifigan. May improve output quality '
                     'for characters that were trained on a limited data set. However, this option often degrades '
                     'quality for well-trained characters.'),
        ], className='spaced-table')

    # Pretend this is annotated like so:
    # @app.callback(
    #     Output('slice-length-number', 'children'),
    #     Input(self.input_ids[3], 'value')
    # )
    def adjust_slice_length(self, adjustment):
        if adjustment is None:
            raise PreventUpdate
        # cast to float first, then round to 2 decimal places
        return "{:3.2f}".format(float(adjustment))

    # Pretend this is annotated like so:
    # @app.callback(
    #     Output('cross-fade-number', 'children'),
    #     Input(self.input_ids[4], 'value')
    # )
    def adjust_crossfade_length(self, adjustment):
        if adjustment is None:
            raise PreventUpdate
        # cast to float first, then round to 2 decimal places
        return "{:3.2f}".format(float(adjustment))

    # Pretend this is annotated like so:
    # @app.callback(
    #     Output('character-likeness-number', 'children'),
    #     Input(self.input_ids[5], 'value')
    # )
    def adjust_character_likeness(self, adjustment):
        if adjustment is None:
            raise PreventUpdate
        # cast to float first, then round to 2 decimal places
        return "{:3.2f}".format(float(adjustment))

    # Pretend this is annotated like so:
    # @app.callback(
    #     [Output(self.input_ids[5], 'disabled'),
    #      Output(self.input_ids[5], 'value')
    #     Input(self.input_ids[0], 'value'),
    #     State(self.input_ids[5], 'value')
    # )
    def disable_character_likeness(self, character, current_character_likeness):
        # todo: Account for the possibility of multiple kmeans models for multi-speaker models
        if character is None:
            raise PreventUpdate
        character_dir = get_model_path(self.id, character)
        potential_names = [file for file in os.listdir(character_dir) if file.startswith('kmeans')]
        if len(potential_names) == 0:
            return True, 0
        else:
            return False, current_character_likeness

    # Pretend this is annotated like so:
    # @app.callback(
    #     Output(self.input_ids[4], 'disabled'),
    #     Input(self.input_ids[3], 'value')
    # )
    def disable_crossfade_length(self, slice_length):
        if slice_length is None:
            raise PreventUpdate
        return float(slice_length) < 0.01

    @property
    def input_ids(self):
        return [self.id+'-character',
                self.id+'-pitch-shift',
                self.id+'-predict-pitch',
                self.id+'-slice-length',
                self.id+'-crossfade-length',
                self.id+'-character-likeness',
                self.id+'-reduce-hoarseness',
                self.id+'-apply-nsf-hifigan',
                ]

    def construct_input_dict(self, *args):
        return {
            'Architecture': self.id,
            'Character': args[0],
            'Pitch Shift': args[1],
            # Note: A checklist option is initially None, but if you toggle it on and then back off, it becomes an empty
            # list, []. The expression "True if args[x] else False" maps both None and [] to False and [''] to True.
            'Predict Pitch': True if args[2] else False,
            'Slice Length': args[3],
            'Cross-Fade Length': args[4],
            'Character Likeness': args[5],
            'Reduce Hoarseness': True if args[6] else False,
            'Apply nsf_hifigan': True if args[7] else False,
        }

    @property
    def characters_metadata(self):
        return []

    @property
    def multi_speaker_models_metadata(self):
        return []