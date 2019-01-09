#!/bin/python

"""
convert_directory.py
--------------------
Converts all audio files in a folder recursively from one audio format
to another.

The script requires a source folder as a first, and a destination folder
as a second argument. The source folder will be parsed recursively, and
the desired encoder will be run on multiple files at once. To work on
the same folder, simply provide it as both source and destination. The
directory tree relative to the source folder will be preserved in the
process.

By default, `FLAC` files will be converted to the `Ogg Vorbis` format,
with a `quality=5` setting. Further specification on the encoder can be
made in highlighted sections of the script. Metadata will be copied from
the original file to the converted ones. Files of different types, e.g.
album covers, will be copied. 

Example
-------
Calling the script with the following parameters:
  sh ./filename_metadata.py ./path/to/source ./path/to/destination
will convert all files from the source folder, e.g.:
  ./path/to/source/genre/album/101_title-of-first-song.flac
to the destination folder, e.g.:
  ./path/to/destination/genre/album/101_title-of-first-song.ogg
"""



# ----- User specifications -----
# Choose music container formats on which this script will be applied to:
format_in  = "flac"
format_out = "ogg"
# Currently, only 'ogg' and 'mp3' are supported output formats.
# Feel free to provide another encoder for a different output format
# later in the script.
# -------------------------------



import os, sys
from shutil import copyfile

import multiprocessing, subprocess
from functools import partial

from collections import namedtuple
Encoder = namedtuple("Encoder", "encoder opt_input opt_output opt_misc")

import mutagen



# Check if enough cmd line parameters are provided.
assert len(sys.argv) == 3, "Please provide two command line arguments!"

# Store directories.
dir_in  = os.path.abspath(sys.argv[1])
dir_out = os.path.abspath(sys.argv[2])

# Check if specified paths are valid.
assert os.path.isdir(dir_in),  "Cannot find source directory!"
if not os.path.isdir(dir_out):
  os.mkdir(dir_out)



# ----- Pick encoder based on user's choice -----
# Consult hydrogenaudio for recommended settings.
#  - oggenc: https://wiki.hydrogenaud.io/index.php?title=Recommended_Ogg_Vorbis
#  - lame  : https://wiki.hydrogenaud.io/index.php?title=LAME
if format_out == "ogg":
  encoder = Encoder("oggenc", "", "--output=", "--quality=5")
elif format_out == "mp3":
  if format_in == "flac":
    # LAME does not support the flac container, so we use a workaround.
    encoder = Encoder("flac", "--decode --stdout ", "| lame - ", "-V3")
  else:
    encoder = Encoder("lame", "", "", "-V3")
# -----------------------------------------------

if(encoder == []):
  raise RuntimeError("No encoder specified!")





# Worker function for encoding.
def converter(file_in, root_in):
  assert file_in.lower().endswith("."+format_in)

  # Generate both usable os paths for both input and output files.
  # For the latter, we replace both stem folder and file extension
  # from the original input filename with the corresonding one.
  path_in  = os.path.join(root_in, file_in)
  root_out = os.path.join(dir_out, root_in[len(dir_in):].lstrip('/'))
  file_out = file_in[:-len(format_in)] + format_out
  path_out = os.path.join(root_out, file_out)

  # Encode.
  subprocess.call(encoder.encoder + " " +                      \
                  encoder.opt_input  + "'" + path_in  + "' " + \
                  encoder.opt_output + "'" + path_out + "' " + \
                  encoder.opt_misc,
                  shell=True,
                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
  if not os.path.exists(path_out):
    raise RuntimeError("Converter did not parse file!")

  # Copy metadata.
  meta_in  = mutagen.File(path_in, easy=True)
  meta_out = mutagen.File(path_out, easy=True)
  for meta in meta_in:
    meta_out[meta] = meta_in[meta]
  meta_out.save()



# Copy miscellaneous files.
def copyer(file_in, root_in):
  assert not file_in.lower().endswith("."+format_in)

  # Generate both usable os paths for both input and output files.
  path_in  = os.path.join(root_in, file_in)
  root_out = os.path.join(dir_out, root_in[len(dir_in):].lstrip('/'))
  path_out = os.path.join(root_out, file_in)

  # Copy.
  copyfile(path_in, path_out)





if __name__ == '__main__':
  for root, subdirs, files in os.walk(dir_in):
    print("Parsing '" + root + "'")

    # Specify on which files we have to work on.
    files_in   = [f for f in files
                  if f.lower().endswith("."+format_in)]
    files_misc = [f for f in files
                  if not f.lower().endswith("."+format_in)]


    # Make sure that the output path exists.
    if len(files_in) > 0 or len(files_misc) > 0:
      root_out = os.path.join(dir_out, root[len(dir_in):].lstrip('/'))
      if not os.path.exists(root_out):
        os.mkdir(root_out)


    # Encode 'format_in' files to 'format_out'.
    if len(files_in) > 0:
      # Parallelization approach:
      # Convert each file in 'root' folder on separate processor.
      pool = multiprocessing.Pool(None)
      ret = pool.map_async(partial(converter, root_in=root), files_in)
      ret.get()
      # Wait for all processors to finish and free ressources.
      pool.close()
      pool.join()


    # Copy miscellaneous files.
    if len(files_misc) > 0:
      # Copy remaining files from 'dir_in' to 'dir_out'.
      # We do it sequentially to avoid stress on the DD.
      for file_misc in files_misc:
        copyer(file_misc, root)
