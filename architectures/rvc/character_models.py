from download.model_list_validator import validate_character_model

# todo: Replace 1111 with the correct sizes of the files
# todo: Provide entries for: Babs Seed, Big McIntosh, Braeburn, Bunni Bunni, Cream Heart, Diamond Tiara, Doctor
#  Whooves, Gallus, Thorax, Applejack, Applejack (alt), Fluttershy, Fluttershy (alt), Pinkie Pie, Pinkie Pie (alt),
#  Rainbow Dash (alt), Rarity (alt), and Twilight Sparkle (alt)

character_models = [
    {
        "Model Name": "Cozy Glow",
        "Files": [
            {
                "URL": "https://huggingface.co/therealvul/RVC/resolve/main/CozyGlow/CozyGlow.pth",
                "Download With": "HUGGINGFACE_HUB",
                "Download As": "Cozy Glow.pth",
                "Size (bytes)": 1111
            },
            {
                "URL": "https://huggingface.co/therealvul/RVC/resolve/main/CozyGlow/added_IVF173_Flat_nprobe_4.index",
                "Download With": "HUGGINGFACE_HUB",
                "Download As": "Cozy Glow.index",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Derpy Hooves",
        "Files": [
            {
                "URL": "https://huggingface.co/therealvul/RVC/resolve/main/Derpy%20Hooves/derpy_hooves.pth",
                "Download With": "HUGGINGFACE_HUB",
                "Download As": "Derpy Hooves.pth",
                "Size (bytes)": 1111
            },
            {
                "URL": "https://huggingface.co/therealvul/RVC/resolve/main/Derpy%20Hooves/added_IVF127_Flat_nprobe_4.index",
                "Download With": "HUGGINGFACE_HUB",
                "Download As": "Derpy Hooves.index",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Octavia Melody",
        "Files": [
            {
                "URL": "https://huggingface.co/therealvul/RVC/resolve/main/Octavia%20Melody/OctaviaMelody.pth",
                "Download With": "HUGGINGFACE_HUB",
                "Download As": "Octavia Melody.pth",
                "Size (bytes)": 1111
            },
            {
                "URL": "https://huggingface.co/therealvul/RVC/resolve/main/Octavia%20Melody/added_IVF34_Flat_nprobe_2.index",
                "Download With": "HUGGINGFACE_HUB",
                "Download As": "Octavia Melody.index",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Twilight Sparkle (singing)",
        "Files": [
            {
                "URL": "https://huggingface.co/therealvul/RVC/resolve/main/Twilight%20Sparkle%20(singing)/twilight_sparkle_singing.pth",
                "Download With": "HUGGINGFACE_HUB",
                "Download As": "Twilight Sparkle (singing).pth",
                "Size (bytes)": 1111
            },
            {
                "URL": "https://huggingface.co/therealvul/RVC/resolve/main/Twilight%20Sparkle%20(singing)/added_IVF1364_Flat_nprobe_8.index",
                "Download With": "HUGGINGFACE_HUB",
                "Download As": "Twilight Sparkle (singing).index",
                "Size (bytes)": 1111
            }
        ]
    },
    {
        "Model Name": "Vinyl Scratch",
        "Files": [
            {
                "URL": "https://huggingface.co/therealvul/RVC/resolve/main/VinylScratch/VinylScratch.pth",
                "Download With": "HUGGINGFACE_HUB",
                "Download As": "Vinyl Scratch.pth",
                "Size (bytes)": 1111
            },
        ]
    },
]

# todo: Add Models with Mega links. See notes below.

# pinkie pie
# https://mega.nz/file/ZfJF0C7S#gGyLBDqow7yPMBWD8Oqvul74aalzhBpNUqnRjUeizJM
# 274235568 bytes
# extracts like:
# PinkiePie:
# 	PinkiePie_e400.pth
# 	added_IVF3144_Flat_nprobe_1.index
#
# So introduce a new download method: MEGA
# Introduce a new unzip method: REMOVE_OUTERMOST_DIR
# And either introduce a new option in the download dict, under Files:
# 	"Rename Unzipped Files": [
# 		{
# 			"Original Name": "PinkiePie_e400.pth",
# 			"New Name": "Pinkie Pie.pth"
# 		},
# 		{
# 			"Original Name": "added_IVF3144_Flat_nprobe_1.index",
# 			"New Name": "Pinkie Pie.index"
# 		}\
# 	]
# OORRR... just redesign the server to look for a pth file and an index file without caring about the basename.
#
# applejack
# https://mega.nz/file/kT50jKxQ#4x9vM78bGJvk_BvurrHqx3zJOnhnHvQySyG_3or2JcY
#
# fluttershy
# https://mega.nz/file/pf4wxT6J#j13tM7AwFKFPhwYJOTorWv_LU1hR8Z8BLjqtPfhbGV0


if __name__ == '__main__':
    print('Validating with jsonschema...')
    character_errors = validate_character_model(character_models)
    print(character_errors if character_errors else '=== No validation errors for Character Models ===')
