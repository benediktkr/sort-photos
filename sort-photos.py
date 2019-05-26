#!/usr/bin/env python3

import argparse
import glob
import os
import shutil

import exifread

HOME = os.getenv("HOME")
NEXTCLOUD_DIR = os.path.join(HOME, "Nextcloud")
PHOTOS_DIR = os.path.join(NEXTCLOUD_DIR, "Photos")
UNSORTED_DIR = os.path.join(PHOTOS_DIR, "Unsorted")
print("Photos dir: {}".format(PHOTOS_DIR))

parser = argparse.ArgumentParser()
parser.add_argument("--src", required=True)
parser.add_argument("--dst", default=PHOTOS_DIR, required=False)
parser.add_argument("--debug", action="store_true")
parser.add_argument("--dry-run", action="store_true")
args = parser.parse_args()

def debug(s):
    if args.debug:
        print(s)

def move(src, dst):
    if not args.dry_run:
        shutil.move(src, dst)

def mkdir(path):
    if not args.dry_run:
        os.makedirs(path, exist_ok=True)

def get_date(path):
    with open(path, 'rb') as f:
        tags = exifread.process_file(f, stop_tag="EXIF DateTimeOriginal")

    y, m, d = tags["EXIF DateTimeOriginal"].values.split(" ")[0].split(":")
    return (y, m, d)


if __name__ == "__main__":
    g = glob.glob(args.src)
    for a in g:
        try:
            y, m, _ = get_date(a)
            ymdir = os.path.join(PHOTOS_DIR, y, m)
            mkdir(ymdir)
            debug("{} -> {}".format(a, ymdir))
            move(a, ymdir)
        except KeyError:
            # Could not parse date
            mkdir(UNSORTED_DIR)
            print("{} -> {}".format(a, UNSORTED_DIR))
            move(a, UNSORTED_DIR)
        except IsADirectoryError:
            # leave directories, happens if you didn't give the
            # correct full path
            print("Skipping directory: {}".format(a))
            continue
