from dash import Dash, html, dcc, Input, Output, State
from .AbstractTab import AbstractTab


class ControllableTalknetTab(AbstractTab):

    def __init__(self, app, root_dir):
        super().__init__(app, root_dir)

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
                html.Td('Character', className='option-label'),
                html.Td(self.character_dropdown)
            ]),
            html.Tr([
                html.Td('Disable Audio Input', className='option-label'),
                html.Td(dcc.Checklist([''], id=self.input_ids[1]))
            ],
                title='Instruct Controllable Talknet to ignore \n'
                      'the audio file you selected above, if any, \n'
                      'and only use the text you have entered.')
        ], className='spaced-table')

    @property
    def input_ids(self):
        return [self.id+'-character', self.id+'-disable-text']

    def construct_input_dict(self, *args):
        return {
            'Architecture': self.id,
            'Character': args[0],
            # Note: args[1] is initially None, but if you toggle it on and then back off, it becomes an empty list, [].
            'Disable Text': True if args[1] else False  # None and [] map to False, [''] maps to True
        }

    def pretty_input(self, *args):
        return args[0] + (' | Disable Text' if args[1] is not None else '')

