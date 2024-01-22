import model_migrator as migrator
import util
from architectures.styletts_2.StyleTTS2Tab import STYLETTS2_ID
from plotly_celery_common import select_architecture_tabs

preload_app = True


def on_starting(server):
    """This is a special gunicorn Server Hook method and is called only once during server startup (as opposed to once
    per worker thread). See gunicorn documentation."""
    # server.app.callable is the same object as app.server from main.py. This lets us pass the already-parsed command
    # line arguments from the main application to this server hook.
    architectures = server.app.callable.architectures
    migrate_models = server.app.callable.migrate_models
    update_model_lists_on_startup = server.app.callable.update_model_lists_on_startup
    initialize_app(architectures, migrate_models, update_model_lists_on_startup)


def initialize_app(architectures, migrate_models=False, update_model_lists_on_startup=False):
    migrator.migrate_models_if_specified(migrate_models, architectures)
    update_model_lists_if_specified(update_model_lists_on_startup, architectures)


def update_model_lists_if_specified(update_model_lists_on_startup, architectures):
    if update_model_lists_on_startup and util.internet_available():
        update_model_lists(architectures)


def update_model_lists(architectures):
    available_tabs = select_architecture_tabs(architectures)
    for tab in available_tabs:
        tab.update_multi_speaker_infos_file()
        tab.update_character_infos_file()
        if tab.id == STYLETTS2_ID:
            tab.update_style_lists_for_styletts2()
