import jsonschema
from jsonschema.exceptions import ValidationError

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
            'Originally Acquired From': {'type': 'string'}
        },
        'additionalProperties': False,
        'required': ['Model Name', 'Files'],
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


def validate_character_model(character_model):
    validation_error = None
    try:
        jsonschema.validate(instance=character_model, schema=character_schema)
    except ValidationError as e:
        validation_error = e.message
    return validation_error


def validate_multi_speaker_model(multi_speaker_model):
    validation_error = None
    try:
        jsonschema.validate(instance=multi_speaker_model, schema=multi_speaker_schema)
    except ValidationError as e:
        validation_error = e.message
    return validation_error
