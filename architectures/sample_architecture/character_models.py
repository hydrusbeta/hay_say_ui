from download.model_list_validator import validate_character_model

# Please do not actually try to download these files. I made up the URLs.
# The purpose of this file is to provide a sample to demonstrate how the character_models dictionary should be
# structured.

character_models = [
    {
        "Model Name": "Rainbow Shine",
        "Multi-speaker Model Dependency": "Generic Pony",
        "Files": [
            {
                "URL": "example.com/1",
                "Download With": "GDOWN",
                "Download As": "something.config",
                "Size (bytes)": 1111
            },
            {
                "URL": "example.com/2",
                "Download With": "GDOWN",
                "Download As": "indices/somethingElse.index",
                "Size (bytes)": 2222
            }
        ],
        "Symlinks": [
            {
                "As": "singer/Rainbow Shine.pth",
                "Target": "singer/Generic Pony.pth"
            }
        ],
        "Originally Acquired From": "originalURL.com/1.zip"
    }
]

if __name__ == '__main__':
    print('Validating with jsonschema...')
    character_errors = validate_character_model(character_models)
    print(character_errors if character_errors else '=== No validation errors for Character Models ===')
