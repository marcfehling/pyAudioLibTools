#!/bin/python

"""
filename_metadata.py
--------------------
Renames and moves all files of a specified music container format on
basis of their metadata.

The script expects a source folder as a first, and a destination folder
as a second argument. The source folder will be parsed recursively, and
all of its contents will be renamed and moved to the destination folder.
To work on the same folder, simply provide it as both source and
destination.

All files belonging to the specified audio container format will be
renamed in the process, according to the specified template. `FLAC` files
will be renamed by default; all other files will be ignored.

By default, the path of any moved file relative to the source folder
will be preserved. However, user specified folder templates based on
metadata can be used as well by changing highlighted sections in the
script.

Example
-------
Calling the script with the following parameters:
  sh ./filename_metadata.py ./path/to/source ./path/to/destination
will move all files from the source folder, e.g.:
  ./path/to/source/genre/album/file_with_metadata.flac
to the destination folder, e.g.:
  ./path/to/destination/genre/album/101_title-of-first-song.flac
"""



# ----- User specifications -----
# Choose music container format on which this script will be applied to:
format_in = "flac"
# Later in the script, choose which path template shall be used.
# -------------------------------



import os, sys
from shutil import move

import mutagen
from slugify import slugify



# Check if enough cmd line parameters are provided.
assert len(sys.argv) == 3, "Please provide two command line arguments!"

# Store directories.
dir_in  = os.path.abspath(sys.argv[1])
dir_out = os.path.abspath(sys.argv[2])

# Check if specified paths are valid.
assert os.path.isdir(dir_in),  "Cannot find source directory!"
assert os.path.isdir(dir_out), "Cannot find destination directory!"



if __name__ == '__main__':
  for root, subdirs, files in os.walk(dir_in):
    print("Parsing '" + root + "'")

    # Specify on which files we have to work on.
    files_in = [f for f in files
                if f.lower().endswith("."+format_in)]

    for file_in in files_in:
      # Get meta information using 'mutagen'.
      meta = mutagen.File(path_in, easy=True)
      
      # Collect a selection of metadata.
      # - Ensure that any file has the desired metadata available.
      #   Make an exception for 'discnumber' data.
      # - Always pick the very first entry of each category to construct
      #   the new filename and/or path.
      # - Replace invalid characters (reserved characters, Umlauts, blanks)
      #   by underscores using 'slugify'.
      if 'album' in meta.keys() and len(meta['album']) > 0:
        album = meta['album'][0]
        album = slugify(album)
      else:
        raise ValueError("No 'album' metadata provided.")
        
      if 'artist' in meta.keys() and len(meta['artist']) > 0:
        artist = meta['artist'][0]
        artist = slugify(artist)
      else:
        raise ValueError("No 'artist' metadata provided.")
        
      if 'date' in meta.keys() and len(meta['date']) > 0:
        date = meta['date'][0]
        date = slugify(date)
      else:
        raise ValueError("No 'date' metadata provided.")
        
      if 'discnumber' in meta.keys() and len(meta['discnumber']) > 0:
        discnumber = meta['discnumber'][0]
        discnumber = slugify(discnumber)
        
      if 'genre' in meta.keys() and len(meta['genre']) > 0:
        genre = meta['genre'][0]
        genre = slugify(genre)
      else:
        raise ValueError("No 'genre' metadata provided.")
        
      if 'title' in meta.keys() and len(meta['title']) > 0:
        title = meta['title'][0]
        title = slugify(title)
      else:
        raise ValueError("No 'title' metadata provided.")
        
      if 'tracknumber' in meta.keys() and len(meta['tracknumber']) > 0:
        tracknumber = meta['tracknumber'][0]
        tracknumber = slugify(tracknumber)
      else:
        raise ValueError("No 'tracknumber' metadata provided.")

      # ----- Provide path template of choice -----
      # Generate output filename by format of choice.
      file_out = ""
      if 'discnumber' in meta.keys() and len(meta['discnumber']) > 0:
        file_out += discnumber
      file_out += tracknumber.zfill(2) + "_" + title + "." + format_in

      # Preserve file structure from source folder.
      root_out = os.path.join(dir_out, root[len(dir_in):].lstrip('/'))
      # Or use unique template, e.g. like:
      # root_out = os.path.join(dir_out, genre, artist, date + "_" + album)
      # --------------------------------------------

      # Move/Rename file
      path_in  = os.path.join(root, file_in)
      path_out = os.path.join(root_out, file_out)
      try:
        move(path_in, path_out)
      except Exception as exc:
        raise IOError() from exc
