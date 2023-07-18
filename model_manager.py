from dash import html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate
from hay_say_common import get_model_path
import shutil


def construct_model_manager(available_tabs):
    return html.Div(
        [html.Div('Select the models you would like to delete:')] +
        [html.Br()] +
        [html.Div(list_models(tab)) for tab in available_tabs] +
        [html.Button('Delete Selected Models', id='delete-models-button')],
        id='model-manager-outer-div', className='outer-div', hidden=True)


def list_models(tab):
    return [
        html.Div(tab.label),
        dcc.Checklist(['(Select all)'], inputClassName='checklist-input-style', id=tab.id + '-delete-all-checkbox'),
        dcc.Checklist(tab.characters, inputClassName='checklist-input-style', id=tab.id + '-delete-checklist'),
        html.Br()
    ]


def register_model_manager_callbacks(app, available_tabs):
    def define_select_all_callback(tab):
        @app.callback(
            Output(tab.id + '-delete-checklist', 'value'),
            Input(tab.id + '-delete-all-checkbox', 'value'),
            State(tab.id + '-delete-checklist', 'options'),
        )
        def select_all(select_all_value, selectable_values):
            return selectable_values if select_all_value else []
        return select_all

    # Instantiate the "select all" checkbox callback for all tabs
    callbacks = [define_select_all_callback(tab) for tab in available_tabs]

    @app.callback(
        [Output(tab.id + '-download-checklist', 'options', allow_duplicate=True) for tab in available_tabs] +
        [Output(tab.input_ids[0], 'options', allow_duplicate=True) for tab in available_tabs] +  # character dropdown
        [Output(tab.input_ids[0], 'value', allow_duplicate=True) for tab in available_tabs] +  # character dropdown
        [Output(tab.id + '-delete-checklist', 'options', allow_duplicate=True) for tab in available_tabs] +
        [Output(tab.id + '-delete-checklist', 'value', allow_duplicate=True) for tab in available_tabs],
        [Input('delete-models-button', 'n_clicks')] +
        [State(tab.id + '-delete-checklist', 'value') for tab in available_tabs],
        prevent_initial_call=True
    )
    def delete_selected_models(n_clicks, *model_lists_to_delete):
        if n_clicks is None:
            raise PreventUpdate
        models_to_delete = [get_model_path(available_tabs[idx].id, model_to_delete)
                            for idx, model_list_to_delete in enumerate(model_lists_to_delete)
                            for model_to_delete in model_list_to_delete]
        for model in models_to_delete:
            shutil.rmtree(model)
        # Refresh the character download list, refresh the character selection dropdowns, deselect the currently
        # selected character for each architecture in case it was deleted, refresh the deletable characters lists, and
        # deselect the selections in the deletable character lists.
        return [tab.downloadable_characters() for tab in available_tabs] + \
            [tab.characters for tab in available_tabs] + \
            [None for tab in available_tabs] + \
            [tab.characters for tab in available_tabs] +\
            [[] for tab in available_tabs]

    # If a user has recently downloaded a new model, we need to refresh the download list when they navigate to the
    # model manager. Note: we cannot merge this callback into the generate_download_callback method of main.py because
    # the elements with id "tab.id + '-delete-checklist'" will not exist for that callback if local_mode is false.
    @app.callback(
        [Output(tab.id + '-delete-checklist', 'options') for tab in available_tabs],
        Input('model-manager-outer-div', 'hidden')
    )
    def update_delete_checklists(hidden):
        if hidden is None or hidden:
            raise PreventUpdate
        else:
            return [tab.characters for tab in available_tabs]

