import json
import os
import redis
from datetime import datetime
from enum import Enum, auto

import soundfile

from hay_say_common.utility import read_audio

CACHE_FORMAT, CACHE_EXTENSION, CACHE_MIMETYPE = 'FLAC', '.flac', 'audio/flac;base64'  # FLAC compression is lossless
MAX_FILES_PER_STAGE = 25
TIMESTAMP_FORMAT = '%Y/%m/%d %H:%M:%S.%f'


class Stage(Enum):
    RAW = auto()  # Raw file supplied by the user
    PREPROCESSED = auto()  # User file after it has undergone preprocessing
    OUTPUT = auto()  # Generated file, without any preprocessing
    POSTPROCESSED = auto()  # Generated file after it has undergone postprocessing


class FileImpl:
    METADATA_FILENAME = 'metadata.json'

    ROOT_DIR = os.path.join(os.path.expanduser('~'), 'hay_say')
    AUDIO_FOLDER = os.path.join(ROOT_DIR, 'audio_cache')

    folder_map = {
        Stage.RAW: os.path.join(AUDIO_FOLDER, 'raw'),
        Stage.PREPROCESSED: os.path.join(AUDIO_FOLDER, 'preprocessed'),
        Stage.OUTPUT: os.path.join(AUDIO_FOLDER, 'output'),
        Stage.POSTPROCESSED: os.path.join(AUDIO_FOLDER, 'postprocessed')
    }

    @classmethod
    def read_metadata(cls, stage):
        """Return the metadata dictionary of the cache at the specified stage. The metadata dictionary describes all the
        files stored in the cache at a given stage.
        'stage' should be one of the Stage enums"""
        path_to_file = os.path.join(cls.folder_map[stage], cls.METADATA_FILENAME)
        metadata = dict()
        if os.path.isfile(path_to_file):
            with open(path_to_file, 'r') as file:
                metadata = json.load(file)
        return metadata

    @classmethod
    def write_metadata(cls, stage, dict_contents):
        """Sets the metadata dictionary to the supplied dictionary for the cache at the specified stage, overwriting
        existing contents. The metadata dictionary describes all the files stored in the cache at a given stage.
        'stage' should be one of the Stage enums"""
        path = os.path.join(cls.folder_map[stage], cls.METADATA_FILENAME)
        with open(path, 'w') as file:
            file.write(json.dumps(dict_contents, sort_keys=True, indent=4))

    @classmethod
    def read_audio_from_cache(cls, stage, filename_sans_extension):
        """Reads the specified file from the cache at the specified stage, returning the data array and sample rate.
        'stage' should be one of the Stage enums"""
        path = os.path.join(cls.folder_map[stage], filename_sans_extension + CACHE_EXTENSION)
        return read_audio(path)

    @classmethod
    def save_audio_to_cache(cls, stage, filename_sans_extension, array, samplerate):
        """saves the supplied audio data to the cache at the specified stage with the specified filename. The oldest file in
        the cache for the stage is deleted if saving this file would cause the total number of files cached in that stage to
        exceed MAX_FILES_PER_STAGE.
        'stage' should be one of the Stage enums"""
        if cls.count_audio_cache_files(stage) >= MAX_FILES_PER_STAGE:
            cls.delete_oldest_cache_file(stage)
        cls.write_audio_file(stage, filename_sans_extension, array, samplerate)

    @classmethod
    def write_audio_file(cls, stage, filename_sans_extension, array, samplerate):
        """writes audio data to the cache at the specified stage with the specified filename.
        'stage' should be one of the Stage enums"""
        path = os.path.join(cls.folder_map[stage], filename_sans_extension + CACHE_EXTENSION)
        soundfile.write(path, array, samplerate, format=CACHE_FORMAT)

    @classmethod
    def count_audio_cache_files(cls, stage):
        """Return the number of audio files stored in the cache at the specified stage.
        'stage' should be one of the Stage enums"""
        metadata = cls.read_metadata(stage)
        return len(metadata.keys())

    @classmethod
    def delete_oldest_cache_file(cls, stage):
        """Deletes the oldest file from the cache at the specified stage.
        'stage' should be one of the Stage enums"""
        # delete the file itself
        oldest_filename_sans_extension = cls.get_hashes_sorted_by_timestamp(stage)[-1]
        oldest_path = os.path.join(cls.folder_map[stage], oldest_filename_sans_extension + CACHE_EXTENSION)
        os.remove(oldest_path)

        # remove entry from metadata file
        metadata = cls.read_metadata(stage)
        del metadata[oldest_filename_sans_extension]
        cls.write_metadata(stage, metadata)

    @classmethod
    def get_hashes_sorted_by_timestamp(cls, stage):
        """Returns the hashes/filenames (without extension) of the audio files in the cache at the specified stage, sorted
        by their timestamp.
        'stage' should be one of the Stage enums"""
        metadata = cls.read_metadata(stage)
        return sorted(metadata.keys(),
                      key=lambda key: datetime.strptime(metadata[key]['Time of Creation'], TIMESTAMP_FORMAT),
                      reverse=True)

    @classmethod
    def file_is_already_cached(cls, stage, filename_sans_extension):
        """Return True if the specified file is already present in the cache at the specified stage, otherwise False
        'stage' should be one of the Stage enums"""
        metadata = cls.read_metadata(stage)
        return True if filename_sans_extension in metadata.keys() else False

    @classmethod
    def delete_all_files_at_stage(cls, stage):
        """Deletes all files, including the metadata file, at the specified stage
        'stage' should be one of the Stage enums"""
        path = os.path.join(cls.folder_map[stage])
        for filename in os.listdir(path):
            path = os.path.join(path, filename)
            os.remove(path)

    @classmethod
    def read_file_bytes(cls, stage, filename_sans_extension):
        """Reads the specified file at the specified stage and returns the raw bytes of the file.
        'stage' should be one of the Stage enums"""
        path = os.path.join(cls.folder_map[stage], filename_sans_extension + CACHE_EXTENSION)
        with open(path, 'rb') as file:
            byte_data = file.read()
        return byte_data


class MongoImpl:
    # todo: implement this class

    @classmethod
    def read_metadata(cls, stage):
        """Return the metadata dictionary of the cache at the specified stage. The metadata dictionary describes all the
        files stored in the cache at a given stage.
        'stage' should be one of the Stage enums"""
        pass

    @classmethod
    def write_metadata(cls, stage, dict_contents):
        """Sets the metadata dictionary to the supplied dictionary for the cache at the specified stage, overwriting
        existing contents. The metadata dictionary describes all the files stored in the cache at a given stage.
        'stage' should be one of the Stage enums"""
        pass

    @classmethod
    def read_audio_from_cache(cls, stage, filename_sans_extension):
        """Reads the specified file from the cache at the specified stage.
        'stage' should be one of the Stage enums"""
        pass

    @classmethod
    def save_audio_to_cache(cls, stage, filename_sans_extension, array, samplerate):
        """saves the supplied audio data to the cache at the specified stage with the specified filename. The oldest file in
        the cache for the stage is deleted if saving this file would cause the total number of files cached in that stage to
        exceed MAX_FILES_PER_STAGE.
        'stage' should be one of the Stage enums"""
        pass

    @classmethod
    def write_audio_file(cls, stage, filename_sans_extension, array, samplerate):
        """writes audio data to the cache at the specified stage with the specified filename.
        'stage' should be one of the Stage enums"""
        pass

    @classmethod
    def count_audio_cache_files(cls, stage):
        """Return the number of audio files stored in the cache at the specified stage.
        'stage' should be one of the Stage enums"""
        pass

    @classmethod
    def delete_oldest_cache_file(cls, stage):
        """Deletes the oldest file from the cache at the specified stage.
        'stage' should be one of the Stage enums"""
        pass

    @classmethod
    def get_hashes_sorted_by_timestamp(cls, stage):
        """Returns the hashes/filenames (without extension) of the audio files in the cache at the specified stage, sorted
        by their timestamp.
        'stage' should be one of the Stage enums"""
        pass

    @classmethod
    def file_is_already_cached(cls, stage, filename_sans_extension):
        """Return True if the specified file is already present in the cache at the specified stage, otherwise False"""
        pass

    @classmethod
    def delete_all_files_at_stage(cls, stage):
        """Deletes all files, including the metadata file, at the specified stage
        'stage' should be one of the Stage enums"""
        pass

    @classmethod
    def read_file_bytes(cls, stage, filename_sans_extension):
        """Reads the specified file at the specified stage and returns the raw bytes of the file.
        'stage' should be one of the Stage enums"""
        pass


class RedisImpl:
    # todo: implement this class (but MongoImpl is definitely higher priority)

    REDIS_URL = 'redis://redis:6379'
    redis_db = redis.StrictRedis.from_url(REDIS_URL)
    # Note: Redis databases are limited to 25 GB each.
    @classmethod
    def read_metadata(cls, stage):
        """Return the metadata dictionary of the cache at the specified stage. The metadata dictionary describes all the
        files stored in the cache at a given stage.
        'stage' should be one of the Stage enums"""
        pass

    @classmethod
    def write_metadata(cls, stage, dict_contents):
        """Sets the metadata dictionary to the supplied dictionary for the cache at the specified stage, overwriting
        existing contents. The metadata dictionary describes all the files stored in the cache at a given stage.
        'stage' should be one of the Stage enums"""
        pass

    @classmethod
    def read_audio_from_cache(cls, stage, filename_sans_extension):
        """Reads the specified file from the cache at the specified stage.
        'stage' should be one of the Stage enums"""
        pass

    @classmethod
    def save_audio_to_cache(cls, stage, filename_sans_extension, array, samplerate):
        """saves the supplied audio data to the cache at the specified stage with the specified filename. The oldest file in
        the cache for the stage is deleted if saving this file would cause the total number of files cached in that stage to
        exceed MAX_FILES_PER_STAGE.
        'stage' should be one of the Stage enums"""
        pass

    @classmethod
    def write_audio_file(cls, stage, filename_sans_extension, array, samplerate):
        """writes audio data to the cache at the specified stage with the specified filename.
        'stage' should be one of the Stage enums"""
        pass

    @classmethod
    def count_audio_cache_files(cls, stage):
        """Return the number of audio files stored in the cache at the specified stage.
        'stage' should be one of the Stage enums"""
        pass

    @classmethod
    def delete_oldest_cache_file(cls, stage):
        """Deletes the oldest file from the cache at the specified stage.
        'stage' should be one of the Stage enums"""
        pass

    @classmethod
    def get_hashes_sorted_by_timestamp(cls, stage):
        """Returns the hashes/filenames (without extension) of the audio files in the cache at the specified stage, sorted
        by their timestamp.
        'stage' should be one of the Stage enums"""
        pass

    @classmethod
    def file_is_already_cached(cls, stage, filename_sans_extension):
        """Return True if the specified file is already present in the cache at the specified stage, otherwise False"""
        pass

    @classmethod
    def delete_all_files_at_stage(cls, stage):
        """Deletes all files, including the metadata file, at the specified stage
        'stage' should be one of the Stage enums"""
        pass

    @classmethod
    def read_file_bytes(cls, stage, filename_sans_extension):
        """Reads the specified file at the specified stage and returns the raw bytes of the file.
        'stage' should be one of the Stage enums"""
        pass
