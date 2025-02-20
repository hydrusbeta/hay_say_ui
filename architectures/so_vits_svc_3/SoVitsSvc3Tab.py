from dash import html, dcc, Input, Output, State

from architectures.AbstractTab import AbstractTab


class SoVitsSvc3Tab(AbstractTab):
    @property
    def id(self):
        return 'so_vits_svc_3'

    @property
    def port(self):
        return 6575

    @property
    def label(self):
        return 'so-vits-svc 3.0'

    @property
    def description(self):
        return [html.P('so-vits-svc achieves a voice conversion effect by extracting "soft speech" features from '
                       'reference audio and passing them to a variational autoencoder.'),
                html.P(
                    html.A('https://github.com/svc-develop-team/so-vits-svc',
                           href='https://github.com/svc-develop-team/so-vits-svc')
                ),
                html.P('Thank you to Vul Traz and various unknown/anonymous users for providing the character models')]

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
                html.Td("Note: \"TFH\" = Them's Fightin' Herds characters", colSpan=2, className='centered')
            ]),
            html.Tr([
                html.Td(html.Label('Character', htmlFor=self.input_ids[0]), className='option-label'),
                html.Td(self.character_dropdown)
            ]),
            html.Tr([
                html.Td(html.Label('Shift Pitch (semitones)', htmlFor=self.input_ids[1]), className='option-label'),
                html.Td(dcc.Input(id=self.input_ids[1], type='number', min=-36, max=36, step=1, value=0))
            ], title='Adjusts the pitch of the generated audio in semitones'),
        ], className='spaced-table')

    @property
    def input_ids(self):
        return [self.id+'-character', self.id+'-semitone-pitch']

    def construct_input_dict(self, session_data, *args):
        return {
            'Architecture': self.id,
            'Character': args[0],
            'Pitch Shift': args[1]
        }