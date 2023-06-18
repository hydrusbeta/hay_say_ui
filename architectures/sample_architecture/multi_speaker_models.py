from download.model_list_validator import validate_multi_speaker_model

# Please do not actually try to download these files. I made up the URLs.
# The purpose of this file is to provide a sample to demonstrate how the multi_speaker_models dictionary should be
# structured.

multi_speaker_models = [
    {
        "Model Name": "Generic Pony",
        "Files": [
            {
                "URL": "example.com/1",
                "Download With": "GDOWN",
                "Download As": "something.zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            },
            {
                "URL": "example.com/2",
                "Download With": "GDOWN",
                "Download As": "indices/somethingElse.index",
                "Size (bytes)": 2222
            }
        ],
        "Originally Acquired From": "originalURL.com/1.zip"
    }
]

if __name__ == '__main__':
    print('Validating with jsonschema...')
    multi_speaker_errors = validate_multi_speaker_model(multi_speaker_models)
    print(multi_speaker_errors if multi_speaker_errors else '=== No validation errors for Multi Speaker Models ===')
