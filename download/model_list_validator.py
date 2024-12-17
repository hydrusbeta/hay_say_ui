import jsonschema
from jsonschema.exceptions import ValidationError

import model_licenses
from download import Downloader

# For sample dictionaries, see:
# "architectures/sample_architecture/character_models.py"
# "architectures/sample_architecture/multi_speaker_models.py"

files_schema = {
    'type': 'array',
    'items': {
        'properties': {
            'URL': {'type': 'string'},
            'Download With': {'enum': [download_type.name for download_type in Downloader.DownloadType]},
            'Download As': {'type': 'string'},
            'Unzip Strategy': {'enum': [unzip_type.name for unzip_type in Downloader.UnzipType]},
            'Size (bytes)': {'type': 'integer', 'minimum': 0}
        },
        'additionalProperties': False,
        'required': ['URL', 'Download With', 'Download As', 'Size (bytes)']
    }
}

character_schema = {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'Model Name': {'type': 'string'},
            'Multi-speaker Model Dependency': {'type': 'string'},
            'Files': files_schema,
            'Symlinks': {
                'type': 'array',
                'items': {
                    'properties': {
                        'As': {'type': 'string'},
                        'Target': {'type': 'string'}
                    },
                    'additionalProperties': False,
                    'required': ['As', 'Target']
                }
            },
            'License': {'enum': [licence_type.name for licence_type in model_licenses.License]},
            'Creator': {'type': 'string'},
            'Originally Acquired From': {'type': 'string'}
        },
        'additionalProperties': False,
        'required': ['Model Name', 'Files', 'License'],
        'dependentRequired': {
            'Symlinks': ['Multi-speaker Model Dependency'],
            'Multi-speaker Model Dependency': ['Symlinks']
        }
    }
}

multi_speaker_schema = {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'Model Name': {'type': 'string'},
            'Files': files_schema,
            'Originally Acquired From': {'type': 'string'}
        },
        'additionalProperties': False,
        'required': ['Model Name', 'Files']
    }
}


def validate_character_model_infos(tab):
    character_model_infos = tab.read_character_model_infos()
    validation_message = 'Character models validation for ' + tab.id + ':\n'
    validation_error = '    passed'
    try:
        jsonschema.validate(instance=character_model_infos, schema=character_schema)
    except ValidationError as e:
        validation_error = '    ' + e.message
    return validation_message + validation_error


def validate_multi_speaker_model_infos(tab):
    multi_speaker_model_infos = tab.read_multi_speaker_model_infos()
    validation_message = 'Multispeaker models validation for ' + tab.id + ':\n'
    validation_error = '    passed'
    try:
        jsonschema.validate(instance=multi_speaker_model_infos, schema=multi_speaker_schema)
    except ValidationError as e:
        validation_error = e.message
    return validation_message + validation_error


def validate_model_dependencies(tab):
    validation_message = 'Model dependencies validation for ' + tab.id + ':\n'
    validation_error = '    passed'
    multi_speaker_model_dependencies = set([character_model_info.get('Multi-speaker Model Dependency')
                                            for character_model_info in tab.read_character_model_infos()
                                            if character_model_info.get('Multi-speaker Model Dependency')])
    multi_speaker_model_names = set([model_info['Model Name'] for model_info in tab.read_multi_speaker_model_infos()])
    extra_models = multi_speaker_model_names.difference(multi_speaker_model_dependencies)
    if len(extra_models) != 0:
        validation_error = 'Warning! The following multi-speaker model(s) do not appear to be used: ' + \
                           str(extra_models)

    missing_dependencies = multi_speaker_model_dependencies.difference(multi_speaker_model_names)
    if len(missing_dependencies) != 0:
        validation_error = 'Error! One or more characters has a dependency on one of the following multi-speaker ' \
                           'model(s), but the multi-speaker model(s) do not exist! ' + str(missing_dependencies)
    return validation_message + validation_error


def instantiate_tabs_for_testing():
    from architectures.controllable_talknet.ControllableTalknetTab import ControllableTalknetTab
    from architectures.so_vits_svc_3.SoVitsSvc3Tab import SoVitsSvc3Tab
    from architectures.so_vits_svc_4.SoVitsSvc4Tab import SoVitsSvc4Tab
    from architectures.so_vits_svc_5.SoVitsSvc5Tab import SoVitsSvc5Tab
    from architectures.rvc.RvcTab import RvcTab
    from architectures.styletts_2.StyleTTS2Tab import StyleTTS2Tab
    from architectures.gpt_so_vits.GPTSoVITSTab import GPTSoVITSTab
    from architectures.sample_architecture.SampleArchitectureTab import SampleTab
    return [
        ControllableTalknetTab(None),
        SoVitsSvc3Tab(None),
        SoVitsSvc4Tab(None),
        SoVitsSvc5Tab(None),
        RvcTab(None),
        StyleTTS2Tab(None),
        GPTSoVITSTab(None),
        SampleTab(None)
    ]


if __name__ == '__main__':
    available_tabs = instantiate_tabs_for_testing()
    for tab in available_tabs:
        print('===== ' + tab.id + ' =====')
        print(validate_character_model_infos(tab))
        print(validate_multi_speaker_model_infos(tab))
        print(validate_model_dependencies(tab))
