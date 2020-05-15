#!/usr/bin/python


from datetime import datetime
import struct
import sys

def get_mov_dates(filename):
    # borrowed from stackoverflow
    # https://stackoverflow.com/questions/21355316/getting-metadata-for-mov-video
    ATOM_HEADER_SIZE = 8
    # difference between Unix epoch and QuickTime epoch, in seconds
    EPOCH_ADJUSTER = 2082844800

    # open file and search for moov item
    f = open(filename, "rb")
    while 1:
        atom_header = f.read(ATOM_HEADER_SIZE)
        if atom_header[4:8] == b'moov':
            break
        else:
            try:
                atom_size = struct.unpack(">I", atom_header[0:4])[0]
                f.seek(atom_size - 8, 1)
            except struct.error:
                  raise ValueError("no 'moov' header found in {}".format(filename))

    # found 'moov', look for 'mvhd' and timestamps
    atom_header = f.read(ATOM_HEADER_SIZE)
    if atom_header[4:8] == b'cmov':
        print("moov atom is compressed")
    elif atom_header[4:8] != b'mvhd':
        print("expected to find 'mvhd' header")
    else:
        f.seek(4, 1)
        creation_date = struct.unpack(">I", f.read(4))[0]
        modification_date = struct.unpack(">I", f.read(4))[0]

        created = datetime.utcfromtimestamp(creation_date - EPOCH_ADJUSTER)
        #modified = datetime.utcfromtimestamp(modification_date - EPOCH_ADJUSTER)
        # print(created)
        #return modified
        return created

def get_date(path):
    """Returns a tuple of strings (y, m, d) where m and d are zero-padded

    what sort-photos.py expects"""

    date = get_mov_dates(path)
    y, m, d = [str(a).zfill(2) for a in [date.year, date.month, date.day]]

    return (y, m, d)


if __name__ == "__main__":
    path = sys.argv[1]
    date = get_date(path)
    print(date)
