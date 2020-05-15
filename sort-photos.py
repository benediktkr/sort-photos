#!/usr/bin/env python3

import argparse
import glob
import os
import shutil

import exifread

import movheaders

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
parser.add_argument("--fileext")
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
    if os.path.splitext(path)[1].lower() == ".mov":
        return movheaders.get_date(path)
    else:
        with open(path, 'rb') as f:
            tags = exifread.process_file(f, stop_tag="EXIF DateTimeOriginal")
        y, m, d = tags["EXIF DateTimeOriginal"].values.split(" ")[0].split(":")
        return (y, m, d)



if __name__ == "__main__":
    #g = glob.glob(args.src)
    # just one dir at a time
    g = os.listdir(args.src)
    # print(g)
    # raise SystemExit
    for a in g:
        try:
            # im gonna have fun with this next time i look at it
            a_ext = os.path.splitext(a)[1].lower()
            if args.fileext and a_ext !=  args.fileext:
                continue
            _path = os.path.join(args.src, a)
            a_mb = os.path.getsize(_path) >> 20
            #print("{}, {} mb".format(a, a_mb))
            y, m, d = get_date(_path)
            if args.fileext and a_ext == ".mov":
                # big videos (actual videos ive taken) have already
                # been uploaded by nextcloud. Trying to single out
                # the live videos around photos
                if a_mb > 5:
                    debug("Too big: {}, {} mb, {}/{}/{}".format(_path, a_mb, y, m, d))
                    # ignore completely, no wasting space on nextcloud
                    continue

            ymdir = os.path.join(PHOTOS_DIR, y, m)
            mkdir(ymdir)
            debug("{} -> {}".format(a, ymdir))
            move(_path, ymdir)
        except ValueError:
            mkdir(UNSORTED_DIR)
            print("{} -> {}".format(a, UNSORTED_DIR))
            move(os.path.join(args.src, a), UNSORTED_DIR)
        except KeyError:
            # Could not parse date
            mkdir(UNSORTED_DIR)
            print("{} -> {}".format(a, UNSORTED_DIR))
            move(os.path.join(args.src, a), UNSORTED_DIR)
        except IsADirectoryError:
            # leave directories, happens if you didn't give the
            # correct full path
            print("Skipping directory: {}".format(os.path.join(args.src, a)))
            continue
