from dash import Dash, html, dcc, Input, Output, State
from .AbstractTab import AbstractTab


class ControllableTalknetTab(AbstractTab):

    def __init__(self, app, root_dir):
        super().__init__(app, root_dir)
        app.callback(Output('autotune-cell', 'children'),
                     [Input(self.input_ids[1], 'value'),
                      Input('file-dropdown', 'value')])(self.disable_autotune)

    @property
    def id(self):
        return 'controllable_talknet'

    @property
    def port(self):
        return 6574

    @property
    def label(self):
        return 'Controllable Talknet'

    @property
    def description(self):
        return [html.P('Controllable TalkNet is based on NVIDIA\'s implementation of Talknet2, with some changes to '
                       'support singing synthesis and higher audio quality.'),
                html.P(
                    html.A('https://github.com/SortAnon/ControllableTalkNet',
                           href='https://github.com/SortAnon/ControllableTalkNet')
                )]

    @property
    def requirements(self):
        return html.P(
            html.Em('This architecture requires text input. You may optionally provide a voice recording of that text '
                    'too, to guide the pacing and inflection of the generated voice.')
        )

    def meets_requirements(self, user_text, user_audio):
        return user_text is not None and user_text != ''

    @property
    def options(self):
        return html.Table([
            html.Tr([
                html.Td(html.Label('Character', htmlFor=self.input_ids[0]), className='option-label'),
                html.Td(self.character_dropdown)
            ]),
            html.Tr([
                html.Td(html.Label('Disable Audio Input', htmlFor=self.input_ids[1]), className='option-label'),
                html.Td(dcc.Checklist([''], id=self.input_ids[1]))
            ],
                title='Instructs Controllable Talknet to ignore \n'
                      'the audio file you selected above, if any, \n'
                      'and only use the text you have entered.'),
            html.Tr([
                html.Td(html.Label('Adjust Input Pitch (semitones)', htmlFor=self.input_ids[2]), className='option-label'),
                html.Td(dcc.Input(id=self.input_ids[2], type='number', min=-25, max=25, step=1, value=0))
            ],
                title='Adjusts the pitch of the input audio, in semitones'),
            html.Tr([
                html.Td(html.Label('Auto Tune Output', htmlFor=self.input_ids[3]), className='option-label'),
                html.Td(dcc.Checklist([''], id=self.input_ids[3]), id='autotune-cell')
            ],
                title='Auto tunes the output using the pitch of the audio reference.'),
            html.Tr([
                html.Td(html.Label('Reduce Metallic Sound', htmlFor=self.input_ids[4]), className='option-label'),
                html.Td(dcc.Checklist([''], id=self.input_ids[4]))
            ],
                title='Runs the generated spectrogram through the "vq" GAN network - and then reconstructs the audio '
                      'from the spectrogram using the "hifirec" GAN network - to reduce metallic noise.'),
        ], className='spaced-table')

    # Pretend this is annotated like so:
    # @app.callback(
    #     Output('autotune-cell', 'children'),
    #     [Input(self.input_ids[1], 'value'),
    #      Input('file-dropdown', 'value')]
    # )
    def disable_autotune(self, disable_audio_input, selected_file):
        disabled = True if disable_audio_input else selected_file is None
        return dcc.Checklist(options=[{'label': '', 'value': '', 'disabled': disabled}], id=self.input_ids[3])

    @property
    def input_ids(self):
        return [self.id + '-character',
                self.id + '-disable-text',
                self.id + '-pitch-factor',
                self.id + '-auto-tune',
                self.id + '-reduce-metallic-sound']

    def construct_input_dict(self, *args):
        return {
            'Architecture': self.id,
            'Character': args[0],
            # Note: A checklist option is initially None, but if you toggle it on and then back off, it becomes an empty
            # list, []. The expression "True if args[x] else False" maps both None and [] to False and [''] to True.
            'Disable Reference Audio': True if args[1] else False,
            'Pitch Factor': args[2],
            'Auto Tune': True if args[3] else False,
            'Reduce Metallic Sound': True if args[4] else False
        }

