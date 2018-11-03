# pyAudioLibTools

A collection of basic python scripts to manage your local music library.

## filename_metadata.py

Renames and moves all files of a specified music container format on basis of their metadata.

The script expects a source folder as a first, and a destination folder as a second argument. The source folder will be parsed recursively, and all of its contents will be renamed and moved to the destination folder. To work on the same folder, simply provide it as both source and destination.

All files belonging to the specified audio container format will be renamed in the process, according to the specified template. [FLAC](https://xiph.org/flac/) files will be renamed by default; all other files will be ignored.

By default, the path of any moved file relative to the source folder will be preserved. However, user specified folder templates based on metadata can be used as well by changing highlighted sections in the script.

Requires the additional python packages [mutagen](https://github.com/quodlibet/mutagen) and [slugify](https://github.com/un33k/python-slugify).

### Example

Calling the script with the following parameters:
```bash
sh ./filename_metadata.py ./path/to/source ./path/to/destination
```
will move all files from the source folder, e.g.:
```
./path/to/source/genre/album/file_with_metadata.flac
```
to the destination folder, e.g.:
```
./path/to/destination/genre/album/101_title-of-first-song.flac
```

## convert_directory.py

Converts all audio files in a folder recursively from one audio format to another.

The script requires a source folder as a first, and a destination folder as a second argument. The source folder will be parsed recursively, and the desired encoder will be run on multiple files at once. To work on the same folder, simply provide it as both source and destination. The directory tree relative to the source folder will be preserved in the process.

By default, [FLAC](https://xiph.org/flac/) files will be converted to the [Ogg Vorbis](https://xiph.org/vorbis/) format, with a `quality=5` setting. Further specification on the encoder can be made in highlighted sections of the script. Metadata will be copied from the original file to the converted ones. Files of different types, e.g. album covers, will be copied. 

Requires the additional python package [mutagen](https://github.com/quodlibet/mutagen), as well as encoders for the desired audio formats, i.e. [`oggenc`](https://github.com/xiph/vorbis-tools) for [Ogg Vorbis](https://xiph.org/vorbis/), [`lame`](http://lame.sourceforge.net/) for [MP3](https://mpeg.chiariglione.org/standards/mpeg-1/audio), or [`flac`](https://github.com/xiph/flac) for [FLAC](https://xiph.org/flac/).

### Example

Calling the script with the following parameters:
```bash
sh ./convert_directory.py ./path/to/source ./path/to/destination
```
will convert all files from the source folder, e.g.:
```
./path/to/source/genre/album/101_title-of-first-song.flac
```
to the destination folder, e.g.:
```
./path/to/destination/genre/album/101_title-of-first-song.ogg
```
