# Audiobooks Merger

This script merges individual audiobook chapters in `.mp3` or other audio formats into a single `.m4b` audiobook file, including metadata, chapters, and a cover image.

## Features
- Merges multiple audio chapters into one audiobook file.
- Automatically adds chapters metadata for easy navigation.
- Supports custom metadata fields (title, author, etc.).
- Adds cover images to the resulting audiobook.

## Requirements
- Python 3.x
- `ffmpeg` and `ffprobe`

### Installation of ffmpeg and ffprobe

**Ubuntu/Debian**:
```bash
sudo apt-get install ffmpeg
```

**MacOS (Homebrew)**:
```bash
brew install ffmpeg
```

**Windows (Chocolatey)**:
```bash
choco install ffmpeg
```

## Usage

The project includes a Jupyter notebook `main.ipynb` for easier execution.  
In this notebook, you define the book metadata as a Python dictionary and call the `main` function from `main.py` passing `BOOK_METADATA` dictionary as an argument.

### Suported metadata keys

| Key           | Description                        | Example                    |
|---------------|------------------------------------|----------------------------|
| `title`       | Title of the audiobook             | "The Two Towers"           |
| `album`       | Name of the audiobook/collection   | "The Lord of the Rings"    |
| `artist`      | Author of the book                 | "J.R.R. Tolkien"           |
| `genre`       | Audiobook category                 | "Audiobook"                |
| `date`        | Year of release                    | "1954"                     |
| `track`       | Track number                       | "1"                        |
| `disc`        | Disc number (if applicable)        | "2"                        |
| `disctotal`   | Total number of discs              | "3"                        |
| `language`    | Audio language (ISO code)          | "eng"                      |
| `comment`     | Additional comments or description | "Notes or description"     |


### Example usage of the Jupyter Notebook file:

```python
from main import main
```

```python
BOOK_METADATA = {
    'title': "The Two Towers",
    'album': "The Lord of the Rings",
    'artist': "J. R. R. Tolkien",
    'genre': "Audiobook",
    'date': "1954",
    'track': "1",
    'disc': "2",
    'disctotal': "3",
    'language': 'eng',
    'comment': None,
}
```

```python
main(BOOK_METADATA)
```



## License

This project is licensed under the [MIT License](LICENSE). You can freely use, modify, distribute, and sell this software as long as the original license and copyright notices remain.

## Author

Rubén López - Data Scientist  
[lopezrbn@gmail.com](mailto:lopezrbn@gmail.com)
