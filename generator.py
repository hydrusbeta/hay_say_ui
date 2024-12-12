import base64
import datetime
import json
import traceback
import uuid
from http.client import HTTPConnection

from hay_say_common.cache import Stage

import hay_say_common as hsc
import plotly_celery_common as pcc
from postprocessed_display import prepare_postprocessed_display


# todo: That's a lot of inputs, and most of them get passed down to the generate() method. Is there a cleaner way to
#  pass all these arguments?
def generate_and_prepare_postprocessed_display(clicks, set_progress, message, cache_type, gpu_id, session_data,
                                               selected_architectures, user_text, selected_file, semitone_pitch,
                                               debug_pitch, reduce_noise, crop_silence, reduce_metallic_noise,
                                               auto_tune_output, output_speed_adjustment, args):
    if clicks is not None:
        highlight_first = True
        try:
            set_progress(message)
            generate(cache_type, gpu_id, session_data, selected_architectures, user_text,
                     selected_file, semitone_pitch, debug_pitch, reduce_noise, crop_silence,
                     reduce_metallic_noise, auto_tune_output, output_speed_adjustment, args)
        except Exception as e:
            return 'An error has occurred. Please send the software maintainers the following information as ' \
                   'well as any recent output in the Command Prompt/terminal (please review and remove any ' \
                   'private info before sending!): \n\n' + \
                   traceback.format_exc(), 'Generate!'
    else:
        highlight_first = False
    cache = hsc.select_cache_implementation(cache_type)
    sorted_hashes = cache.get_hashes_sorted_by_timestamp(Stage.POSTPROCESSED, session_data['id'])
    first_output = [
        prepare_postprocessed_display(cache, sorted_hashes[0], session_data,
                                      highlight=highlight_first)] if sorted_hashes else []
    remaining_outputs = [prepare_postprocessed_display(cache, hash_postprocessed, session_data)
                         for hash_postprocessed in reversed(sorted_hashes[1:])]
    return remaining_outputs + first_output, 'Generate!'


def generate(cache_type, gpu_id, session_data, selected_architectures, user_text, selected_file, semitone_pitch,
             debug_pitch, reduce_noise, crop_silence, reduce_metallic_noise, auto_tune_output, output_speed_adjustment,
             args):
    print('generating on ' + ('CPU' if gpu_id == '' else ('GPU #' + str(gpu_id))), flush=True)
    cache = hsc.select_cache_implementation(cache_type)
    selected_tab_object = get_selected_tab_object(selected_architectures, args[0:len(selected_architectures)])
    relevant_inputs = get_inputs_for_selected_tab(selected_architectures, selected_tab_object,
                                                  args[len(selected_architectures):])
    hash_preprocessed = preprocess_if_needed(cache, selected_file, semitone_pitch, debug_pitch, reduce_noise,
                                             crop_silence, session_data)
    hash_output = process(cache, user_text, hash_preprocessed, selected_tab_object, relevant_inputs,
                          session_data, gpu_id)
    hash_postprocessed = postprocess(cache, hash_output, reduce_metallic_noise, auto_tune_output,
                                     output_speed_adjustment, session_data)


def get_selected_tab_object(selected_architectures, hidden_states):
    # Get the tab that is *not* hidden (i.e. hidden == False)
    return {hidden: tab for hidden, tab in zip(hidden_states, selected_architectures)}.get(False)


def get_inputs_for_selected_tab(selected_architectures, tab_object, args):
    all_inputs = [item for sublist in [tab.input_ids for tab in selected_architectures] for item in sublist]
    indices_of_relevant_inputs = [index for index, item in enumerate(all_inputs) if
                                  item in tab_object.input_ids]
    return [args[i] for i in indices_of_relevant_inputs]


def preprocess_if_needed(cache, selected_file, semitone_pitch, debug_pitch, reduce_noise, crop_silence, session_data):
    if selected_file is None:
        hash_preprocessed = None
    else:
        hash_preprocessed = pcc.preprocess(cache, selected_file, semitone_pitch, debug_pitch, reduce_noise,
                                       crop_silence, session_data)
    return hash_preprocessed


def process(cache, user_text, hash_preprocessed, tab_object, relevant_inputs, session_data, gpu_id):
    """Send a JSON payload to a container, instructing it to perform processing"""

    # todo: A nonce is added to the arguments of compute_next_hash so that generating output multiple times using the
    #  same input arguments will result in multiple outputs being displayed in the UI. Without it, architectures with
    #  nondeterministic output can't display multiple outputs. However, this has the side effect of making the
    #  postprocessing cache useless. It's kinda useless anyways at the moment since there are no postprocessing options
    #  yet, but is there a better way to handle this?
    nonce = uuid.uuid4().hex
    hash_output = pcc.compute_next_hash(hash_preprocessed, user_text, relevant_inputs, nonce)
    payload = construct_payload(user_text, hash_preprocessed, tab_object, relevant_inputs, hash_output,
                                session_data, gpu_id)

    host = tab_object.id + '_server'
    port = tab_object.port
    send_payload(payload, host, port)

    # Uncomment this for local testing only. It writes a mock output file by copying the input file.
    # data_preprocessed, sr_preprocessed = cache.read_audio_from_cache(Stage.PREPROCESSED, session_data['id'],
    #                                                                  hash_preprocessed)
    # cache.save_audio_to_cache(Stage.OUTPUT, session_data['id'], hash_output, data_preprocessed, sr_preprocessed)

    verify_output_exists(cache, hash_output, session_data)
    write_output_metadata(cache, hash_preprocessed, user_text, hash_output, tab_object, relevant_inputs, session_data)
    return hash_output


def construct_payload(user_text, hash_preprocessed, tab_object, relevant_inputs, hash_output,
                      session_data, gpu_id):
    return {
        'Inputs': {
            'User Text': user_text,
            'User Audio': hash_preprocessed
        },
        'Options': tab_object.construct_input_dict(session_data, *relevant_inputs),
        'Output File': hash_output,
        'GPU ID': gpu_id,
        'Session ID': session_data['id']
    }


def send_payload(payload, host, port):
    connection = HTTPConnection(host + ':' + str(port))
    headers = {'Content-type': 'application/json'}
    connection.request('POST', '/generate', json.dumps(payload), headers)
    response = connection.getresponse()
    code = response.status

    if code != 200:
        # Something went wrong, so throw an Exception.
        # The Exception will be caught in the generate() method and displayed to the user.
        message = extract_message(response)
        raise Exception(message)


def extract_message(response):
    json_response = json.loads(response.read().decode('utf-8'))
    base64_encoded_message = json_response['message']
    return base64.b64decode(base64_encoded_message).decode('utf-8')


def verify_output_exists(cache, hash_output, session_data):
    try:
        cache.read_audio_from_cache(Stage.OUTPUT, session_data['id'], hash_output)
    except Exception as e:
        raise Exception("Payload was sent, but output file was not produced.") from e


def write_output_metadata(cache, hash_preprocessed, user_text, hash_output, tab_object, relevant_inputs, session_data):
    output_metadata = cache.read_metadata(Stage.OUTPUT, session_data['id'])

    output_metadata[hash_output] = {
        'Inputs': {
            'Preprocessed File': hash_preprocessed,
            'User Text': user_text
        },
        'Options': tab_object.construct_input_dict(session_data, *relevant_inputs),
        'Time of Creation': datetime.datetime.now().strftime(hsc.cache.TIMESTAMP_FORMAT)
    }
    cache.write_metadata(Stage.OUTPUT, session_data['id'], output_metadata)


def postprocess(cache, hash_output, reduce_metallic_noise, auto_tune_output, output_speed_adjustment, session_data):
    # Convert data types to something more digestible
    reduce_metallic_noise, auto_tune_output = pcc.convert_to_bools(reduce_metallic_noise, auto_tune_output)
    output_speed_adjustment = float(
        output_speed_adjustment)  # Dash's Range Input supplies a string, so cast to float

    # Check whether the postprocessed file already exists
    hash_postprocessed = pcc.compute_next_hash(hash_output, reduce_metallic_noise, auto_tune_output,
                                           output_speed_adjustment)
    if cache.file_is_already_cached(Stage.POSTPROCESSED, session_data['id'], hash_postprocessed):
        return hash_postprocessed

    # Perform postprocessing
    data_output, sr_output = cache.read_audio_from_cache(Stage.OUTPUT, session_data['id'], hash_output)
    data_postprocessed, sr_postprocessed = postprocess_bytes(data_output, sr_output, reduce_metallic_noise,
                                                             auto_tune_output, output_speed_adjustment)

    # write the postprocessed data to file
    cache.save_audio_to_cache(Stage.POSTPROCESSED, session_data['id'], hash_postprocessed, data_postprocessed,
                              sr_postprocessed)

    # write metadata file
    write_postprocessed_metadata(cache, hash_output, hash_postprocessed, reduce_metallic_noise, auto_tune_output,
                                 output_speed_adjustment, session_data)

    return hash_postprocessed


def postprocess_bytes(bytes_output, sr_output, reduce_metallic_noise, auto_tune_output, output_speed_adjustment):
    # todo: implement this
    return bytes_output, sr_output


def write_postprocessed_metadata(cache, hash_output, hash_postprocessed, reduce_metallic_noise, auto_tune_output,
                                 output_speed_adjustment, session_data):
    processing_options, user_text, hash_preprocessed = get_process_info(cache, hash_output, session_data)
    selected_file, preprocess_options = get_preprocess_info(cache, hash_preprocessed, session_data)

    postprocessed_metadata = cache.read_metadata(Stage.POSTPROCESSED, session_data['id'])
    postprocessed_metadata[hash_postprocessed] = {
        'Inputs': {
            'User File': selected_file,
            'User Text': user_text
        },
        'Preprocessing Options': preprocess_options,
        'Processing Options': processing_options,
        'Postprocessing Options': {
            'Reduce Metallic Noise': reduce_metallic_noise,
            'Auto Tune Output': auto_tune_output,
            'Adjust Output Speed': output_speed_adjustment
        },
        'Time of Creation': datetime.datetime.now().strftime(hsc.cache.TIMESTAMP_FORMAT)
    }
    cache.write_metadata(Stage.POSTPROCESSED, session_data['id'], postprocessed_metadata)


def get_process_info(cache, hash_output, session_data):
    output_metadata = cache.read_metadata(Stage.OUTPUT, session_data['id'])
    processing_options = output_metadata.get(hash_output).get('Options')
    user_text = output_metadata.get(hash_output).get('Inputs').get('User Text')
    hash_preprocessed = output_metadata.get(hash_output).get('Inputs').get('Preprocessed File')
    return processing_options, user_text, hash_preprocessed


def get_preprocess_info(cache, hash_preprocessed, session_data):
    if hash_preprocessed is None:
        selected_file = None
        preprocess_options = None
    else:
        preprocess_metadata = cache.read_metadata(Stage.PREPROCESSED, session_data['id'])
        preprocess_options = preprocess_metadata.get(hash_preprocessed).get('Options')
        hash_raw = preprocess_metadata.get(hash_preprocessed).get('Raw File')

        raw_metadata = cache.read_metadata(Stage.RAW, session_data['id'])
        selected_file = raw_metadata.get(hash_raw).get('User File')
    return selected_file, preprocess_options
