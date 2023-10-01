from numbers import Number
from dash import html, Input, Output, State, callback, CeleryManager
from plotly_celery_common import *
from hay_say_common.cache import CACHE_MIMETYPE


def prepare_postprocessed_display(cache, hash_postprocessed, session_data, highlight=False):
    # todo: color-code the information in the display.
    bytes_postprocessed = cache.read_file_bytes(Stage.POSTPROCESSED, session_data['id'], hash_postprocessed)

    metadata = cache.read_metadata(Stage.POSTPROCESSED, session_data['id'])[hash_postprocessed]
    selected_file = metadata['Inputs']['User File']
    user_text = metadata['Inputs']['User Text']
    if metadata['Preprocessing Options']:
        semitone_pitch = metadata['Preprocessing Options']['Semitone Pitch']
        reduce_noise = metadata['Preprocessing Options']['Reduce Noise']
        crop_silence = metadata['Preprocessing Options']['Crop Silence']
    else:  # i.e. There was no input audio to preprocess
        semitone_pitch = 'N/A'
        reduce_noise = False
        crop_silence = False
    inputs = metadata['Processing Options']
    output_speed_adjustment = metadata['Postprocessing Options']['Adjust Output Speed']
    reduce_metallic_noise = metadata['Postprocessing Options']['Reduce Metallic Noise']
    auto_tune_output = metadata['Postprocessing Options']['Auto Tune Output']
    timestamp = metadata['Time of Creation']

    display = html.Div([
        html.Div(style={'height': '30px'}),  # todo: There's got to be a better way to add spacing
        html.Table([
            html.Tr(
                # This table entry serves the special purpose of alerting screen readers that generation is complete.
                html.Td('New Output Generated:' if highlight else '', role='status' if highlight else None,
                        colSpan=2)
            ),
            html.Tr(
                html.Td(
                    html.Audio(src=prepare_src_attribute(bytes_postprocessed, CACHE_MIMETYPE), controls=True),
                    colSpan=2)
            ),
            html.Tr([
                html.Td('Inputs:', className='output-label'),
                html.Td('Audio = ' + (selected_file or 'None')
                        + ((' | Text = ' + user_text[0:20] + ('...' if len(user_text) > 20 else ''))
                           if user_text is not None else ''),
                        className='output-value')
            ]),
            # Commenting this out for now because there are no pre-processing options available.
            # html.Tr([
            #     html.Td('Pre-processing Options:', className='output-label'),
            #     html.Td('Pitch adjustment = ' + str(semitone_pitch) + (
            #         ' semitone(s)' if semitone_pitch != 'N/A' else '')
            #             + (' | Reduce Noise' if reduce_noise else '')
            #             + (' | Crop Silence' if crop_silence else ''), className='output-value')
            # ]),
            html.Tr([
                html.Td('Processing Options:', className='output-label'),
                html.Td(prettify_inputs(inputs), className='output-value')
            ]),
            # Commenting this out for now because there are no post-processing options available.
            # html.Tr([
            #     html.Td('Post-processing Options:', className='output-label'),
            #     html.Td('Output Speed factor = ' + str(output_speed_adjustment)
            #             + (' | Reduce Metallic Sound' if reduce_metallic_noise else '')
            #             + (' | Auto Tune Output' if auto_tune_output else ''), className='output-value')
            # ]),
            html.Tr([
                html.Td('Creation Time:', className='output-label'),
                html.Td(timestamp, className='output-value')
            ]),
        ], className='output-table-highlighted' if highlight else 'output-table'),
        html.Div(style={'height': '30px'}),  # todo: There's got to be a better way to add spacing
    ], className='centered')
    return display


def prettify_inputs(inputs):
    result = ''
    for key in inputs.keys():
        if isinstance(inputs[key], str):
            result = result + key + " = " + inputs[key] + ' | '
        elif isinstance(inputs[key], bool):
            result = result + ((key + ' | ') if inputs[key] else '')
        elif isinstance(inputs[key], Number):
            result = result + key + ' = ' + str(inputs[key]) + ' | '
        else:
            result = result + key + ' = ' + str(inputs[key]) + ' | '
    if result.endswith(' | '):
        result = result[:-3]
    return result
