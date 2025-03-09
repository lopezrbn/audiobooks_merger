# Audiobooks Merger

This script merges individual audiobook chapters in MP3 or other audio formats into a single `.m4b` audiobook file, including metadata, chapters, and a cover image.

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
In this notebook, you define the book metadata as a Python dictionary and call the `main` function from `main.py` with this dictionary as an argument.

Example:

```python
BOOK_METADATA = {
    'title': 'Book Title',
    'author': 'Author Name',
    'year': '2025',
    # Add more metadata fields if desired
}

from main import main
main(BOOK_METADATA)
```

## License

This project is licensed under the [MIT License](LICENSE). You can freely use, modify, distribute, and sell this software as long as the original license and copyright notices remain.

## Author

Rubén López - Data Scientist  
[lopezrbn@gmail.com](mailto:lopezrbn@gmail.com)
