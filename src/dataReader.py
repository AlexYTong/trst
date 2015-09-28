"""
dataReader.py

Written by Alex Tong Sep 2 2015

This file reads a datafile into a python object

The datafile format is currently:
[pgn] [data]
where pgn is 5 hex dgits and data is 16 hex digits

"""

#import numpy as np
from pgns import Pgns
import time
import subprocess

def hex_to_int(h):
    """ converts hex string (no leading characters) to integer """
    return int(h, base = 16)

def to_can_dump(line):
    """ formats data into analyzer input data

    Format is as follows: [0,0,pgn(base 10),0,0,8,FF,FF,FF,FF,FF,FF,FF,FF] note
    that the F chars indicate hex data with comma separated bytes
    """
    pgn, body = line
    pgn = hex_to_int(pgn)
    assert(len(body) == 16)
    body = [body[i:i+2] for i in range(0, len(body), 2)]
    line = [time.clock(),0, pgn, 0,0, 8]
    line.extend(body)
    return line

def to_can_dump_with_time(line):
    """ formats data into analyzer input data

    Format is as follows: [time,0,pgn(base 10),0,0,8,FF,FF,FF,FF,FF,FF,FF,FF] note
    that the F chars indicate hex data with comma separated bytes
    """
    time_read, pgn, body = line
    pgn = hex_to_int(pgn)
    assert(len(body) == 16)
    body = [body[i:i+2] for i in range(0, len(body), 2)]
    line = [time_read, 0, pgn, 0,0, 8]
    line.extend(body)
    return line


def execute(fp, fun, filt = None, has_time = True):
    """ executes a function on a file, with an optional filter step

    Args:
        fp (str): path to read file
        fun (fun): function to interpret a pgn and bodyfun must take the
            (pgn, body) tuple as the only argument
        filt (fun): if set, filt must be a function that takes a single string
            as an argument. Positive return is interpreted as good, else pgn
            is discarded
    """
    #TODO fix this ugliness
    data = []
    with open(fp) as f:
        for line in f:
            l = line.rstrip().split()
            if has_time:
                assert len(l) == 3
                time_read, pgn, body = l
            else:
                if not len(l) == 2:
                    assert(False)
                pgn, body = l
            if filt is not None and not filt(pgn):
                continue
            if has_time:
                data.append(fun((time_read, pgn, body)))
            else:
                data.append(fun((pgn, body)))
    return data

def pgn_is_good(pgn, good_pgns):
    """ filters a pgns only taking useful pgns returns 1 if pgn is good
    Args:
        pgn (str): 2D python list of data
        good_pgns (set): set of good pgns represented as integers
    """
    return hex_to_int(pgn) in good_pgns

def line_to_csv(line):
    """ converts python list to csv string"""
    s = str(line[0])
    for l in line[1:]:
        s += ',' + str(l)
    return s

if __name__ == '__main__':
    p = Pgns()
    good_pgns = p.valid_set
#    good_pgns = set([129029])
    filt = lambda x: pgn_is_good(x, good_pgns)
    data = execute('../data/1/feed', to_can_dump, filt, has_time = False) #GNSS Position Data
    for d in data[1:]:          # This is very strange... but the first line is malformed
        s =  line_to_csv(d)
        print s
        proc = subprocess.Popen(['analyzer', '-json'],
                                stdin = subprocess.PIPE,
                                stdout = subprocess.PIPE,
                                stderr = subprocess.PIPE)
        stdout_val, stderr_val = proc.communicate(s)
        print stdout_val
        


