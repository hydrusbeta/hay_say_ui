from dash import html, dcc, Input, Output, State

from .AbstractTab import AbstractTab


class SoVitsSvc4Tab(AbstractTab):
    def __init__(self, app, root_dir):
        super().__init__(app, root_dir)

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
                    )]

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
                html.Td(),
                html.Td("Note: \"PS1\" = PonySinger1 model")
            ]),
            html.Tr([
                html.Td('Character', className='option-label'),
                html.Td(self.character_dropdown)
            ]),
            # todo: can this be totally replaced with the preprocessing option?
            html.Tr([
                html.Td('Transform', className='option-label'),
                html.Td(dcc.Input(id=self.input_ids[1], type='number', min=-25, max=25, step=1, value=0))
            ], title='Adjusts the pitch of the generated audio in semitones'),  # todo: is this technically accurate?
        ], className='spaced-table')

    @property
    def input_ids(self):
        return [self.id+'-character', self.id+'-semitone-pitch']

    def construct_input_dict(self, *args):
        return {
            'Architecture': self.id,
            'Character': args[0],
            'Semitone Pitch': args[1]
        }
