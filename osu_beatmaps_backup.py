import os
import argparse
from enum import Enum, auto
import re
import json
import browser_cookie3
from fake_useragent import UserAgent
import requests
from dataclasses import dataclass


@dataclass
class OsuBeatmap:
    id: int
    name: str


class Action(Enum):
    BACKUP = auto()
    RESTORE = auto()


parser = argparse.ArgumentParser()

parser.add_argument(
    "--backup",
    "-b",
    required=False,
    action="store_true",
    help="Use this flag to backup your beatmaps",
    dest="should_backup",
)

parser.add_argument(
    "--backup-folder",
    "-bf",
    required=False,
    help="The full path to the folder where you want to backup your beatmaps",
    dest="backup_folder_path",
)

parser.add_argument(
    "--restore",
    "-r",
    required=False,
    action="store_true",
    help="Use this flag to restore your beatmaps",
    dest="should_restore",
)

parser.add_argument(
    "--with-video",
    "-video",
    required=False,
    action="store_true",
    help="Use this flag to restore beatmaps with vidwo",
    dest="should_download_video",
)

args = parser.parse_args()

OSU_PATH = os.getenv("LOCALAPPDATA") + "\\osu!\\Songs\\"
BACKUP_FILE_NAME = "osu_beatmaps_backup.json"
BEHAVIOUR = Action.BACKUP


# 1 Get arguments to tell if we should backup or restore
if args.should_restore:
    BEHAVIOUR = Action.RESTORE


# 3 Get the path to the backup folder
BACKUP_FOLDER = args.backup_folder_path or f"""C:\\Users\\{os.getenv("USERNAME")}\\Documents\\"""
BACKUP_FILE = os.path.join(BACKUP_FOLDER, BACKUP_FILE_NAME)


if BEHAVIOUR == Action.BACKUP:
    # 4 Get the list of beatmaps
    OSU_BEATMAPS = []
    OSU_FOLDER_REGEX = re.compile(r"^(\d{1,}) {1}([^-].{1,})")
    for file in os.listdir(OSU_PATH):
        match = OSU_FOLDER_REGEX.match(file)
        if match:
            id, name = match.groups()
            OSU_BEATMAPS.append(OsuBeatmap(id=int(id), name=name))

    output_content = json.dumps([beatmap.__dict__ for beatmap in OSU_BEATMAPS])

    # 5 Write the backup file
    with open(BACKUP_FILE, "w") as f:
        f.write(output_content)

    print(f"{len(OSU_BEATMAPS)} beatmaps have been backed up to {BACKUP_FILE}!")

elif BEHAVIOUR == Action.RESTORE:
    print("Restoring beatmaps...")
    with open(BACKUP_FILE, "r") as f:
        content = f.read()
        beatmaps = json.loads(content)
        beatmaps = [OsuBeatmap(**beatmap) for beatmap in beatmaps]

    for beatmap in beatmaps:
        print(f"Restoring {beatmap.name} ({beatmap.id})")
        download_url = f"https://osu.ppy.sh/beatmapsets/{beatmap.id}/download"
        if args.should_download_video:
            download_url += "?noVideo=1"
        headers = {
            "User-Agent": UserAgent().firefox,
            "referer": f"https://osu.ppy.sh/beatmapsets/{beatmap.id}",
        }
        cookies = browser_cookie3.firefox()
        response = requests.get(download_url, cookies=cookies, headers=headers)

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            continue

        final_file = os.path.join(BACKUP_FOLDER, f"{beatmap.id} {beatmap.name}.osz")
        with open(final_file, "wb") as file:
            file.write(response.content)

    print(f"{len(beatmaps)} beatmaps have been restored to {BACKUP_FOLDER}!")

print("Done!")
