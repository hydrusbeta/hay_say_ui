from dash import html, dcc, Input, Output, State, callback
from dash.exceptions import PreventUpdate
from hay_say_common import get_model_path, model_dirs
import shutil
import os


def construct_model_manager(available_tabs):
    return html.Div(
        # todo: move styles to css file
        [html.H2('Select models you would like to delete:')] +
        [html.Div(list_models(tab)) for tab in available_tabs] +
        [html.Div('0 bytes', 'delete-size')] +
        [html.Button('Delete Selected Models', id='delete-models-button')] +
        [html.Br()] +
        [html.Br()] +
        [dcc.Markdown('''
        ### Important note for Windows users!  
        If you are trying to free hard drive space on Windows, then you must complete additional steps after clicking 
        the "Delete Selected Models" button above. See [the README file]
        (https://github.com/hydrusbeta/hay_say_ui#additional-required-steps-for-windows-users) 
        
        Linux and MacOS users are unaffected by this issue and should see an immediate increase in disk space after 
        clicking "Delete Selected Models". 
        ''', style={'border': 'solid', 'padding': '10px'})],
        id='model-manager-outer-div', className='outer-div', hidden=True)


def list_models(tab):
    return [
        html.Div(tab.label),
        dcc.Checklist(['(Select all)'], inputClassName='checklist-input-style', id=tab.id + '-delete-all-checkbox'),
        dcc.Checklist(options=tab.deletable_character_options,
                      inputClassName='checklist-input-style',
                      id=tab.id + '-delete-checklist'),
        html.Br()
    ]


def register_model_manager_callbacks(available_tabs):
    def define_select_all_callback(tab):
        @callback(
            Output(tab.id + '-delete-checklist', 'value'),
            Input(tab.id + '-delete-all-checkbox', 'value'),
            State(tab.id + '-delete-checklist', 'options'),
        )
        def select_all(select_all_value, selectable_options):
            # Options come as a list of {'label': 'xxx', 'value': 'yyy'} dictionaries. Grab just the values.
            selectable_values = [entry['value'] for entry in selectable_options]
            return selectable_values if select_all_value else []
        return select_all

    # Instantiate the "select all" checkbox callback for all tabs
    callbacks = [define_select_all_callback(tab) for tab in available_tabs]

    @callback(
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
        return [tab.downloadable_character_options() for tab in available_tabs] + \
            [tab.deletable_character_options for tab in available_tabs] + \
            [None for tab in available_tabs] + \
            [tab.characters for tab in available_tabs] +\
            [[] for tab in available_tabs]

    # If a user has recently downloaded a new model, we need to refresh the download list when they navigate to the
    # model manager. Note: we cannot merge this callback into the generate_download_callback method of main.py because
    # the elements with id "tab.id + '-delete-checklist'" will not exist for that callback if local_mode is false.
    @callback(
        [Output(tab.id + '-delete-checklist', 'options') for tab in available_tabs],
        Input('model-manager-outer-div', 'hidden')
    )
    def update_delete_checklists(hidden):
        if hidden is None or hidden:
            raise PreventUpdate
        else:
            return [tab.deletable_character_options for tab in available_tabs]

