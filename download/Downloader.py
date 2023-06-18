import huggingface_hub
from hay_say_common import ROOT_DIR

import gdown

from enum import Enum, auto
import zipfile
import os
from urllib.parse import urlparse, unquote
import tempfile


class DownloadType(Enum):
    GDOWN = auto()
    HUGGINGFACE_HUB = auto()


class UnzipType(Enum):
    UNZIP_IN_PLACE = auto()


def download_character(architecture, character_model_info):
    # This is the main method for downloading all the files for a character in a given architecture.
    # character_model_info is a dictionary containing the character's name, any multi-speaker model dependency, the
    # URLs for all the files that need to be downloaded, and info on any required symlinks. See character_models.py in
    # the various architecture folders.
    character_name, multi_speaker_model_dependency, files, symlinks = extract_character_metadata(character_model_info)
    character_dir = create_character_dir(architecture, character_name)
    download_files(character_dir, files)


def extract_character_metadata(character_model_info):
    character_name = character_model_info['Model Name']
    multi_speaker_model_dependency = character_model_info.get('Multi-speaker Model Dependency')
    files = character_model_info['Files']
    symlinks = character_model_info.get('Symlinks')
    return character_name, multi_speaker_model_dependency, files, symlinks


def create_character_dir(architecture, character_name):
    # todo: in hay_say_common, create a method for getting the character directory
    character_dir = os.path.join(ROOT_DIR, 'models', architecture, 'characters', character_name)
    os.makedirs(character_dir, exist_ok=True)
    return character_dir


def download_files(character_dir, files):
    for file in files:
        url, download_type, relative_path, unzip_type = extract_file_metadata(file)
        absolute_path = os.path.join(character_dir, relative_path)
        download_file(download_type, url, absolute_path)
        unzip_file(absolute_path, unzip_type)


def extract_file_metadata(file):
    url = file['URL']
    download_type = file['Download With']
    relative_file_path = file['Download As']
    unzip_type = file.get('Unzip Strategy')
    return url, download_type, relative_file_path, unzip_type


def download_file(download_type, url, target):
    downloader = get_downloader(download_type)
    downloader(url, target)


def unzip_file(file_path, unzip_type):
    unzipper = get_unzipper(unzip_type)
    unzipper(file_path, os.path.dirname(file_path))


def get_downloader(download_type):
    if download_type == DownloadType.GDOWN.name:
        return gdown_downloader
    elif download_type == DownloadType.HUGGINGFACE_HUB.name:
        return huggingface_hub_downloader
    else:
        raise Exception('Unknown download type "' + download_type + '"')


def get_unzipper(unzip_type):
    if unzip_type == UnzipType.UNZIP_IN_PLACE.name:
        return unzip_in_place
    elif unzip_type is None:
        return no_unzip
    else:
        raise Exception('Unknown unzip type "' + unzip_type + '"')


# === Downloaders ===

def gdown_downloader(url, target):
    gdown.download(url=url, output=target)


def huggingface_hub_downloader(url, target):
    repo_id, filename = parse_huggingface_url(url)
    with tempfile.TemporaryDirectory() as tempdir:
        download_path = os.path.join(tempdir, filename)
        huggingface_hub.hf_hub_download(repo_id=repo_id, filename=filename,
                                        local_dir=tempdir, local_dir_use_symlinks=False)
        os.rename(download_path, target)


def parse_huggingface_url(url):
    parsed_url = urlparse(url)
    parts = parsed_url.path.split('/')
    repo_id = '/'.join(parts[1:parts.index('resolve')])
    filename = '/'.join(parts[parts.index('main')+1:])
    # "unquote" means to unescape strings from a URL. e.g. "%20" becomes a space character, " ".
    return unquote(repo_id), unquote(filename)


# === Unzippers ===

def unzip_in_place(zip_file, target):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(target)
    os.remove(zip_file)


def no_unzip(*_):
    pass

