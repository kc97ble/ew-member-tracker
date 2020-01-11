import os
import subprocess
from datetime import datetime, timedelta
from django.conf import settings

EXTENSION_LIST = [".mp4", ".MP4", ".mov", ".MOV"]


def is_video_file(file):
    return any(file.endswith(ext) for ext in EXTENSION_LIST)


def get_file_list(dir):
    files = []
    for r, d, f in os.walk(dir):
        for file in f:
            if is_video_file(file):
                files.append(os.path.join(r, file))
    return files


def get_video_length(file):
    run = subprocess.run(
        [
            os.path.join(settings.BIN_DIR, "ffprobe.exe"),
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            file,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return float(run.stdout)


def get_modified_dtime(file):
    return datetime.fromtimestamp(os.path.getmtime(file))


def get_file_info(file):
    mtime = get_modified_dtime(file)
    length = get_video_length(file)
    return {
        "file": file,
        "start_at": mtime,
        "ended_at": mtime + timedelta(seconds=length),
        "length": length,
    }


def get_file_list_ex(dir):
    files = get_file_list(dir)
    return list(map(get_file_info, files))
