from dash import html, Input, Output, ctx


def construct_toolbar():
    return html.Div([
        html.Button('Manage Models', id='manage-models'),
        html.Button('◁ Return to Hay Say', id='hay-say', hidden=True)
    ], id='toolbar', className='toolbar')


def register_toolbar_callbacks(app):
    @app.callback(
        [Output('manage-models', 'hidden'),
         Output('hay-say', 'hidden'),
         Output('hay-say-outer-div', 'hidden'),
         Output('model-manager-outer-div', 'hidden')],
        [Input('hay-say', 'n_clicks'),
         Input('manage-models', 'n_clicks')],
        prevent_initial_call=True
    )
    def toggle_tools_menu(*_):
        triggered = ctx.triggered_id
        hide_manage_models_button = not triggered == 'hay-say'
        hide_hay_say_button = not triggered == 'manage-models'
        hide_hay_say = not triggered == 'hay-say'
        hide_model_manager = not triggered == 'manage-models'
        return hide_manage_models_button, hide_hay_say_button, hide_hay_say, hide_model_manager
