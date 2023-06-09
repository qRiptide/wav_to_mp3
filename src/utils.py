import os
import pydub
from pathlib import PurePath
from fastapi import UploadFile


def create_dir(dir_path) -> None:
    try:
        os.mkdir(dir_path)
    except FileExistsError:
        pass


def save_bytes(filepath, byte_sting) -> None:
    with open(filepath, 'wb') as rec:
        rec.write(byte_sting)


def wav_to_mp3(wav_filepath, mp3_filepath) -> None:
    wav = pydub.AudioSegment.from_wav(wav_filepath)
    wav.export(mp3_filepath)


def clean_convert(wav_record: UploadFile,
                  dir_path: PurePath,
                  filename: str
                  ) -> None:
    create_dir(dir_path)

    wav_filepath = dir_path / wav_record.filename
    mp3_filepath = dir_path / filename

    save_bytes(wav_filepath, wav_record.file.read())

    wav_to_mp3(wav_filepath, mp3_filepath)

    os.remove(wav_filepath)
