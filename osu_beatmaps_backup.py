import os
import argparse
from enum import Enum, auto
import re
from dataclasses import dataclass
import json


class Action(Enum):
    BACKUP = auto()
    RESTORE = auto()


@dataclass
class OsuBeatmap:
    id: int
    name: str


BACKUP_FILE_NAME = "osu_beatmaps_backup.json"
BEHAVIOUR = Action.BACKUP

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

args = parser.parse_args()

# 1 Get arguments to tell if we should backup or restore
if args.should_restore:
    BEHAVIOUR = Action.RESTORE


# 2 Get the path to the osu! beatmaps folder
osu_path = os.getenv("LOCALAPPDATA") + "\\osu!\\Songs\\"

# 3 Get the path to the backup folder
backup_folder = args.backup_folder_path or f"""C:\\Users\\{os.getenv("USERNAME")}\\Documents\\{BACKUP_FILE_NAME}"""

OSU_BEATMAPS = []
OSU_FOLDER_REGEX = re.compile(r"^(\d{1,}) {1}([^-].{1,})")

# 4 Get the list of beatmaps
for file in os.listdir(osu_path):
    match = OSU_FOLDER_REGEX.match(file)
    if match:
        id, name = match.groups()
        OSU_BEATMAPS.append(OsuBeatmap(id=int(id), name=name))

output_content = json.dumps([beatmap.__dict__ for beatmap in OSU_BEATMAPS])

# 5 Write the backup file
with open(backup_folder, "w") as f:
    f.write(output_content)

print(f"{len(OSU_BEATMAPS)} beatmaps have been backed up to {backup_folder}!")
