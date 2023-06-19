from download.model_list_validator import validate_character_model

# Todo: Replace 1111 with the correct sizes of the files.

character_models = [
    {
        "Model Name": "Apple Bloom",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1Wm-7gqws0B3j8mtSQa77Tdk3RZwHEwT5",
                "Download With": "GDOWN",
                "Download As": "Apple Bloom.zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Applejack",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1kpEjZ3YqMN3chKSXODOqayEm581rxj4r",
                "Download With": "GDOWN",
                "Download As": "Applejack.zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Applejack (singing)",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1kegd0J2G4nogaX4IOB2O_vd8msaqMx8M",
                "Download With": "GDOWN",
                "Download As": "Applejack (singing).zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Big McIntosh",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1UzL5vo_ykmRdbi-5JOlsQzNKkoV4tJBP",
                "Download With": "GDOWN",
                "Download As": "Big McIntosh.zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Cadance",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1w98tMJPfGhWvl797gImMfErPXDz_hA-6",
                "Download With": "GDOWN",
                "Download As": "Cadance.zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Celestia",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1whXXcnXu9XPcI60xIkTEofpaDYDOw5yB",
                "Download With": "GDOWN",
                "Download As": "Celestia.zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Chrysalis",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1bb5jKAcQcEQbx1feVwT1UmAEgocINh-E",
                "Download With": "GDOWN",
                "Download As": "Chrysalis.zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Cozy Glow",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1cUQQ_4KXTXbmH3MqwwyZu77SpMr20HAL",
                "Download With": "GDOWN",
                "Download As": "Cozy Glow.zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Discord",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1Cg9Oc_K9UDe5WgVDAcaCSbbBoo-Npj1E",
                "Download With": "GDOWN",
                "Download As": "Discord.zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Fluttershy",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1KgVnjrnxZTXgjnI56ilkq5G4UJCbbwZZ",
                "Download With": "GDOWN",
                "Download As": "Fluttershy.zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Fluttershy (singing)",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1BBdTHis91MwnHTt7tD_xtZ-nQ9SgvqD6",
                "Download With": "GDOWN",
                "Download As": "Fluttershy (singing).zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Granny Smith",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1FJuxLB6MhcHLtmEnOIxhN-yxJ85kmacu",
                "Download With": "GDOWN",
                "Download As": "Granny Smith.zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Luna",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1_ztAbe5YArCMwyyQ_G9lUiz74ym5xJKC",
                "Download With": "GDOWN",
                "Download As": "Luna.zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Maud Pie",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=132G6oD0HHPPn4t1H6IkYv18_F0UVLWgi",
                "Download With": "GDOWN",
                "Download As": "Maud Pie.zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Mayor Mare",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1UFQWJHzKFPumoxioopPbAzM9ydznnRX3",
                "Download With": "GDOWN",
                "Download As": "Mayor Mare.zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Pinkie Pie",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1CdYZ2r52mtgJsFs88U0ZViMSnzpQ_HRp",
                "Download With": "GDOWN",
                "Download As": "Pinkie Pie.zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Pinkie Pie (singing)",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1lo-8wI8iB3GArrzIDlaNTA1If8WX0OEf",
                "Download With": "GDOWN",
                "Download As": "Pinkie Pie (singing).zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Rainbow Dash",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1k3EMXxLC0fLvfxzGbeP6B6plgu9hqCSx",
                "Download With": "GDOWN",
                "Download As": "Rainbow Dash.zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Rainbow Dash (singing)",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1q4RgCEVJCSaR_1Dh0rxs6JVRJt30hQRK",
                "Download With": "GDOWN",
                "Download As": "Rainbow Dash (singing).zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Rarity",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1QWBvQSso4guc1LRUD40WRJ8DY2CfqHGK",
                "Download With": "GDOWN",
                "Download As": "Rarity.zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Rarity (singing)",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1AOMqD_XDV-7JQMZOuZKdJLoB3ebqujOg",
                "Download With": "GDOWN",
                "Download As": "Rarity (singing).zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Scootaloo",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1YkV1VtP1w5XOx3jYYarrCKSzXCB_FLCy",
                "Download With": "GDOWN",
                "Download As": "Scootaloo.zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Shining Armor",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1PUUS71w2ik0uuycNB30nXFze8C7O8OzY",
                "Download With": "GDOWN",
                "Download As": "Shining Armor.zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Spike",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1TKFdmFLttjjzByj2fZW8J70ZHjR-RTwc",
                "Download With": "GDOWN",
                "Download As": "Spike.zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Starlight Glimmer",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1M1AMBq_xjwGTNzRUCXtSLIDJHbcSs3zR",
                "Download With": "GDOWN",
                "Download As": "Starlight Glimmer.zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Sunset Shimmer",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1x1aJt06lBvzUWRlxJ9CEKcFHxQxZPpST",
                "Download With": "GDOWN",
                "Download As": "Sunset Shimmer.zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Sweetie Belle",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1jLX0Py6j8uY93Fjf2l0HOZQYXiShfWUO",
                "Download With": "GDOWN",
                "Download As": "Sweetie Belle.zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Tirek",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1rcPDqgDeCIHGDdvfOo-fxfA1XeM4g3CB",
                "Download With": "GDOWN",
                "Download As": "Tirek.zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Trixie Lulamoon",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1a3CYt0-oTTSFjxtZvAVMpClTmQteYua5",
                "Download With": "GDOWN",
                "Download As": "Trixie.zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Trixie Lulamoon (singing)",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1dA26cUn0Kltt3Evps8DfM-uSrs3sFz72",
                "Download With": "GDOWN",
                "Download As": "Trixie (singing).zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Twilight Sparkle",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1QnOliOAmerMUNuo2wXoH-YoainoSjZen",
                "Download With": "GDOWN",
                "Download As": "Twilight Sparkle.zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Twilight Sparkle (singing)",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=10CENYWV5ugTXZbnsldN6OKR7wkDEe7V7",
                "Download With": "GDOWN",
                "Download As": "Twilight Sparkle (singing).zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Twilight Sparkle (whispering)",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=14_TUQVirITdyBh9etfNV8KFFhi_PUs30",
                "Download With": "GDOWN",
                "Download As": "Twilight Sparkle (whispering).zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Zecora",
        "Files": [
            {
                "URL": "https://drive.google.com/uc?id=1gL0hqqB7952Q1S185moQd_DRCFfIa3_g",
                "Download With": "GDOWN",
                "Download As": "Zecora.zip",
                "Unzip Strategy": "UNZIP_IN_PLACE",
                "Size (bytes)": 1111
            }
        ]
    }
]

if __name__ == '__main__':
    print('Validating with jsonschema...')
    character_errors = validate_character_model(character_models)
    print(character_errors if character_errors else '=== No validation errors for Character Models ===')