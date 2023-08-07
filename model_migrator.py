import os
import shutil
from hay_say_common import custom_model_dir, characters_dir, model_pack_dirs


def migrate_models_if_needed(args, available_tabs):
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
    existing_models = [model for model in os.listdir(target_dir)]
    models_to_move = [os.path.join(source_dir, model) for model in os.listdir(source_dir)
                      if os.path.isdir(os.path.join(source_dir, model)) and model not in existing_models]
    for model in models_to_move:
        shutil.move(model, target_dir)
    shutil.rmtree(source_dir)
