import os
import shutil
import subprocess
import tempfile
import traceback
import zipfile
from enum import Enum, auto
from urllib.parse import urlparse, unquote

import gdown
import requests
from huggingface_hub import hf_hub_download

import util
from hay_say_common import character_dir, multispeaker_model_dir, create_link


class DownloadType(Enum):
    GDOWN = auto()
    HUGGINGFACE_HUB = auto()
    MEGA = auto()
    REQUESTS = auto()


class UnzipType(Enum):
    UNZIP_IN_PLACE = auto()
    FLATTEN = auto()
    REMOVE_OUTERMOST_DIR = auto()


def try_download_character(architecture, character_model_info, multi_speaker_model_info):
    # Call download_character, returning any error stacktrace as a string
    try:
        download_character(architecture, character_model_info, multi_speaker_model_info)
    except Exception as e:
        return traceback.format_exc()
    return ''


def download_character(architecture, character_model_info, multi_speaker_model_info):
    # This is the main entrypoint method for downloading all the files for a character in a given architecture.
    # character_model_info is a dictionary containing the character's name, any multi-speaker model dependency, the
    # URLs for all the files that need to be downloaded, and info on any required symlinks. See character_models.json in
    # the various architecture folders. multi_speaker_model_info is a dictionary containing similar information about
    # any multi-speaker model dependency. See multi_speaker_models.json in the various architecture folders.
    download_multi_speaker_model_if_needed(architecture, multi_speaker_model_info)
    download_character_model(architecture, character_model_info)
    create_symlinks_if_needed(architecture, character_model_info, multi_speaker_model_info)


def download_multi_speaker_model_if_needed(architecture, multi_speaker_model_info):
    if multi_speaker_model_info is not None:
        multi_speaker_model_name, multi_speaker_model_files = extract_multi_speaker_model_metadata(multi_speaker_model_info)
        multi_speaker_model_directory = multispeaker_model_dir(architecture, multi_speaker_model_name)
        if not os.path.exists(multi_speaker_model_directory):
            download_model_files(multi_speaker_model_directory, multi_speaker_model_files)


def download_character_model(architecture, character_model_info):
    character_name, character_files, _ = extract_character_metadata(character_model_info)
    character_directory = character_dir(architecture, character_name)
    download_model_files(character_directory, character_files)


def create_symlinks_if_needed(architecture, character_model_info, multi_speaker_model_info):
    if multi_speaker_model_info is not None:
        character_name, _, symlinks = extract_character_metadata(character_model_info)
        multi_speaker_model_name, _ = extract_multi_speaker_model_metadata(multi_speaker_model_info)
        multi_speaker_model_directory = multispeaker_model_dir(architecture, multi_speaker_model_name)
        character_directory = character_dir(architecture, character_name)
        for symlink in symlinks:
            existing_filename, symlink_filename = extract_symlink_metadata(symlink)
            existing_path = os.path.join(multi_speaker_model_directory, existing_filename)
            if not os.path.exists(existing_path):
                raise Exception('Expected a file at ' + existing_path + ' for symlink creation but it is not there. '
                                'Please report this error to the maintainers of Hay Say and ask them to check '
                                'character_models.json and multi_speaker_models.json for inconsistencies in the ' +
                                architecture + ' architecture.')
            symlink_path = os.path.join(character_directory, symlink_filename)
            create_link(existing_path, symlink_path)


def download_model_files(target_dir, files):
    model_name = os.path.basename(target_dir)
    if os.path.exists(target_dir):
        # This should never happen, but in case it somehow does, delete the existing directory
        shutil.rmtree(target_dir)
    # Download all the files into a temp directory first and then move the directory as the final step. That way, if an
    # error occurs at any time during the downloads, all files will be automatically cleaned and we won't be left with
    # an incomplete target directory (which would prevent the user from retrying the download).
    with tempfile.TemporaryDirectory() as tempdir:
        temp_model_dir = os.path.join(tempdir, model_name)
        os.mkdir(temp_model_dir)
        for file in files:
            download_file_and_unzip(file, temp_model_dir)
        shutil.move(temp_model_dir, target_dir)


def download_file_and_unzip(file, target_directory):
    url, download_type, relative_path, unzip_type = extract_file_metadata(file)
    absolute_path = os.path.join(target_directory, relative_path)
    download_file(download_type, url, absolute_path)
    unzip_file(absolute_path, unzip_type)


def download_file(download_type, url, target_filepath):
    os.makedirs(os.path.dirname(target_filepath), exist_ok=True)
    downloader = get_downloader(download_type)
    downloader(url, target_filepath)


def unzip_file(zip_file_path, unzip_type):
    unzipper = get_unzipper(unzip_type)
    unzipper(zip_file_path, os.path.dirname(zip_file_path))


def get_downloader(download_type):
    if download_type == DownloadType.GDOWN.name:
        return gdown_downloader
    elif download_type == DownloadType.HUGGINGFACE_HUB.name:
        return huggingface_hub_downloader
    elif download_type == DownloadType.MEGA.name:
        return mega_downloader
    elif download_type == DownloadType.REQUESTS.name:
        return requests_downloader
    else:
        raise Exception('Unknown download type "' + download_type + '"')


def get_unzipper(unzip_type):
    if unzip_type == UnzipType.UNZIP_IN_PLACE.name:
        return unzip_in_place
    elif unzip_type == UnzipType.FLATTEN.name:
        return unzip_flattened
    elif unzip_type == UnzipType.REMOVE_OUTERMOST_DIR.name:
        return unzip_and_remove_outermost_dir
    elif unzip_type is None:
        return no_unzip
    else:
        raise Exception('Unknown unzip type "' + unzip_type + '"')


# === Parsing the JSON files ===
def extract_multi_speaker_model_metadata(multi_speaker_model_info):
    model_name = multi_speaker_model_info['Model Name']
    files = multi_speaker_model_info['Files']
    return model_name, files


def extract_character_metadata(character_model_info):
    character_name = character_model_info['Model Name']
    files = character_model_info['Files']
    symlinks = character_model_info.get('Symlinks')
    return character_name, files, symlinks


def extract_file_metadata(file):
    url = file['URL']
    download_type = file['Download With']
    relative_file_path = file['Download As']
    unzip_type = file.get('Unzip Strategy')
    return url, download_type, relative_file_path, unzip_type


def extract_symlink_metadata(symlink_info):
    return symlink_info['Target'], symlink_info['As']


# === Downloaders ===
def gdown_downloader(url, target_filepath):
    gdown.download(url=url, output=target_filepath)


def huggingface_hub_downloader(url, target_filepath):
    repo_id, download_filename = parse_huggingface_url(url)
    # With hf_hub_download, we do not have control over the name of the downloaded file, so we have to rename it
    # afterward. To prevent the rare case where the download name clashes with the name of a file that already exists
    # in the target directory, download the file into a temp directory first and then simultaneously rename and move it
    # to the target directory.
    with tempfile.TemporaryDirectory() as tempdir:
        hf_hub_download(repo_id=repo_id, filename=download_filename, local_dir=tempdir, local_dir_use_symlinks=False)
        download_filepath = os.path.join(tempdir, download_filename)
        shutil.move(download_filepath, target_filepath)


def mega_downloader(url, target_filepath):
    subprocess.run(['mega-get', url, target_filepath])


def requests_downloader(url, target_filepath):
    response = requests.get(url)
    with open(target_filepath, 'wb') as file:
        file.write(response.content)


def parse_huggingface_url(url):
    parsed_url = urlparse(url)
    parts = parsed_url.path.split('/')
    repo_id = '/'.join(parts[1:parts.index('resolve')])
    filename = '/'.join(parts[parts.index('main')+1:])
    # "unquote" means to unescape strings from a URL. e.g. "%20" becomes a space character, " ".
    return unquote(repo_id), unquote(filename)


# === Unzippers ===

def unzip_in_place(zip_file, target_dir):
    # Unzip the given file, retaining the directory structure of the zipfile contents. Example:
    #     MyZipFile.zip
    #     └── my_stuff
    #         ├── file1
    #         ├── file2
    #         └── subdirectory
    #             └── file3
    # Extracts as:
    #     target
    #     └── my_stuff
    #         ├── file1
    #         ├── file2
    #         └── subdirectory
    #             └── file3
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(target_dir)
    os.remove(zip_file)


def unzip_flattened(zip_file, target_dir):
    # Unzip the given file and flatten the resulting directory tree. It is assumed that all filenames in the directory
    # tree are unique. If two or more files share the same name, then only one of them will be preserved. Example:
    #     MyZipFile.zip
    #     └── my_stuff
    #         ├── file1
    #         ├── file2
    #         └── subdirectory
    #             └── file3
    # Extracts as:
    #     target
    #     ├── file1
    #     ├── file2
    #     └── file3
    unzip_in_place(zip_file, target_dir)
    flatten_directory(target_dir)


def unzip_and_remove_outermost_dir(zip_file, target_dir):
    # Unzip the given file, removing the topmost directory of the zipfile contents. Assumes that all zip contents are
    # wrapped in a single directory. Example:
    #     MyZipFile.zip
    #     └── my_stuff
    #         ├── file1
    #         ├── file2
    #         └── subdirectory
    #             └── file3
    # Extracts as:
    #     target
    #     ├── file1
    #     ├── file2
    #     └── subdirectory
    #         └── file3
    with tempfile.TemporaryDirectory() as tempdir:
        unzip_in_place(zip_file, tempdir)
        topmost_dir = [os.path.join(tempdir, item) for item in os.listdir(tempdir)
                       if os.path.isdir(os.path.join(tempdir, item))][0]  # assume there is a single topmost directory
        for item in os.listdir(topmost_dir):
            shutil.move(os.path.join(tempdir, topmost_dir, item), os.path.join(target_dir, item))


def flatten_directory(target_dir):
    # Flattens target_dir to remove all subdirectories, leaving behind only the files in the directory tree.
    # It is assumed that all filenames in the directory tree are unique. If two or more files share the same name, then
    # only one of them will be preserved. It is furthermore assumed that no file has the same name as any subdirectory
    # immediately under target_dir
    dir_meta = os.walk(target_dir)
    all_paths = [os.path.join(dir_path, filename) for (dir_path, _, filenames) in dir_meta for filename in filenames]
    rename_pairs = zip(all_paths, [os.path.join(target_dir, os.path.basename(path)) for path in all_paths])
    for rename_pair in rename_pairs:
        shutil.move(rename_pair[0], rename_pair[1])
    for item in os.listdir(target_dir):
        if os.path.isdir(item):
            shutil.rmtree(os.path.join(target_dir, item))


def no_unzip(*_):
    pass


# === Model lists update logic ===


def update_model_lists_if_specified(args, available_tabs):
    if args.update_model_lists_on_startup and util.internet_available():
        update_model_lists(available_tabs)


def update_model_lists(available_tabs):
    for tab in available_tabs:
        tab.update_multi_speaker_infos_file()
        tab.update_character_infos_file()