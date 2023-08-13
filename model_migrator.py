import os
import shutil
from hay_say_common import custom_model_dir, characters_dir, model_pack_dirs


def migrate_models_if_specified(args, available_tabs):
    if args.migrate_models:
        migrate_all_models(available_tabs)


def migrate_all_models(available_tabs):
    for tab in available_tabs:
        migrate_model_dir_if_exists(custom_model_dir(tab.id), characters_dir(tab.id))  # migrates custom models
        for model_pack_dir in model_pack_dirs(tab.id):
            migrate_model_dir_if_exists(model_pack_dir, characters_dir(tab.id))  # migrates model_pack models


def migrate_model_dir_if_exists(source_dir, target_dir):
    if source_dir is not None and os.path.exists(source_dir):
        migrate_model_dir(source_dir, target_dir)


def migrate_model_dir(source_dir, target_dir):
    print("migrating any models from " + source_dir + " to " + target_dir, flush=True)
    existing_models = [model for model in os.listdir(target_dir)]
    models_to_move = [os.path.join(source_dir, model_name) for model_name in os.listdir(source_dir)
                      if os.path.isdir(os.path.join(source_dir, model_name)) and model_name not in existing_models]
    for model_path in models_to_move:
        shutil.move(model_path, target_dir)
    clean_directory(source_dir)


def clean_directory(directory):
    # Delete all files and directories within the specified directory. Do not delete the specified directory itself.
    items = [os.path.join(directory, item) for item in os.listdir(directory)]
    for item in items:
        if os.path.isdir(item):
            shutil.rmtree(item)
        else:
            os.remove(item)