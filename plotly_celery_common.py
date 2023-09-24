import base64
import hashlib

import hay_say_common.cache
from architectures.controllable_talknet.ControllableTalknetTab import ControllableTalknetTab
from architectures.rvc.RvcTab import RvcTab
from architectures.so_vits_svc_3.SoVitsSvc3Tab import SoVitsSvc3Tab
from architectures.so_vits_svc_4.SoVitsSvc4Tab import SoVitsSvc4Tab
from architectures.so_vits_svc_5.SoVitsSvc5Tab import SoVitsSvc5Tab

cache_implementation_map = {'mongo': hay_say_common.cache.MongoImpl,
                            'file': hay_say_common.cache.FileImpl}


def select_cache_implementation(choice):
    return cache_implementation_map[choice]


architecture_map = {'ControllableTalkNet': ControllableTalknetTab(),
                    'SoVitsSvc3': SoVitsSvc3Tab(),
                    'SoVitsSvc4': SoVitsSvc4Tab(),
                    'SoVitsSvc5': SoVitsSvc5Tab(),
                    'Rvc': RvcTab()}


def select_architecture_tabs(choices):
    return [architecture_map[choice] for choice in choices]


def convert_to_bools(*args):
    # intended for converting a list of checklist items from ['']/None to True/False, respectively
    return [arg is not None for arg in args]


def compute_next_hash(current_hash, *args):
    # concatenate current_hash with all the remaining arguments and then take the hash
    # current_hash can be None.
    base_string = str(current_hash).join([str(item) for item in args])
    return hashlib.sha256(base_string.encode('utf-8')).hexdigest()[:20]


def prepare_src_attribute(src_bytes, mimetype):
    binary_contents = b'data:' + mimetype.encode('utf-8') + b',' + base64.b64encode(src_bytes)
    return binary_contents.decode('utf-8')