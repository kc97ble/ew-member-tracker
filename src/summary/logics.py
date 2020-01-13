import os
import json
import subprocess
from pprint import pprint
from django.conf import settings
from summary.models import Folder
from datetime import datetime, timedelta
from django.core.serializers.json import DjangoJSONEncoder

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


# def get_file_list_ex(dir):
#     files = get_file_list(dir)
#     return list(map(get_file_info, files))


def get_info_list(files):
    return list(map(get_file_info, files))


def intersection(a, b, c, d, zero):
    return max(min(b, d) - max(a, c), zero)


def get_background_color(ratio):
    H = ratio / 3
    # L = ((ratio - 1) ** 3 + 1) * 0.5
    L = ratio * 0.5
    S = 1.0
    return "hsl({}, {}%, {}%)".format((H % 1) * 360, S * 100, L * 100)


def get_heat_map(info_list, num=400):
    start_time = min(map(lambda info: info["start_at"], info_list))
    ended_time = max(map(lambda info: info["ended_at"], info_list))
    step = (ended_time - start_time) / num
    result = []
    for i in range(num):
        start_at = start_time + step * i
        ended_at = start_at + step
        acc_time = timedelta(0)
        for info in info_list:
            acc_time += intersection(
                info["start_at"], info["ended_at"], start_at, ended_at, timedelta(0)
            )
        help = "{} - {}\n{} seconds\n{}%".format(
            start_at.strftime("%H:%M:%S"),
            ended_at.strftime("%H:%M:%S"),
            str(acc_time),
            str(acc_time / step * 100),
        )
        result.append(
            {
                "start_at": start_at,
                "ended_at": ended_at,
                "acc_time": acc_time,
                "ratio": acc_time / step,
                "background_color": get_background_color(acc_time / step),
                "help": help,
            }
        )
    return result


def get_heat_map_from_dir(dir):
    files = get_file_list(dir)
    info_list = get_info_list(files)
    heat_map = get_heat_map(info_list)
    return heat_map


def reload_big_dir(big_dir):
    pprint(big_dir)
    entries = [os.path.join(big_dir, d) for d in os.listdir(big_dir)]
    dirs = [d for d in entries if os.path.isdir(d)]
    pprint(dirs)

    Folder.objects.exclude(dir__in=[dirs]).delete()
    old_dirs = Folder.objects.values_list("dir")
    for d in dirs:
        if d not in old_dirs:
            Folder.objects.create(dir=d)


def generate_heat_map(dir):
    heat_map = get_heat_map_from_dir(dir)
    f = Folder.objects.get(dir=dir)
    f.heat_map_str = json.dumps(heat_map, cls=DjangoJSONEncoder)
    f.save()
