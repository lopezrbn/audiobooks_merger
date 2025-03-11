
import os
import subprocess

def main(BOOK_METADATA):
    """Main function to create a merged audiobook file with metadata and cover image."""

    # Define base and subdirectories for input, output, and temporary files
    PATH_BASE = os.getcwd()
    PATHS_DIRS = {
        "input_files": os.path.join(PATH_BASE, "input_files", BOOK_METADATA['title']),
        "output_files": os.path.join(PATH_BASE, "output_files"),
        "temp_files": os.path.join(PATH_BASE, "temp_files")
    }

    # Create directories if they do not exist
    for path in PATHS_DIRS.values():
        os.makedirs(path, exist_ok=True)

    # Define paths for output and temporary files
    PATHS_FILES = {
        "output_file": os.path.join(PATHS_DIRS['output_files'], f"{BOOK_METADATA['title']}.m4b"),
        "output_file_temp": os.path.join(PATHS_DIRS['temp_files'], f"{BOOK_METADATA['title']}.m4b"),
        "chapters_list": os.path.join(PATHS_DIRS['temp_files'], "chapters_list.txt"),
        "chapters_metadata": os.path.join(PATHS_DIRS['temp_files'], "chapters_metadata.txt"),
    }

    # Find cover image file if exists
    try:
        cover_filename = [
            file for file in os.listdir(PATHS_DIRS['input_files'])
            if file.endswith((".jpg", "jpeg", ".png"))
        ][0]
        PATHS_FILES["cover_image"] = os.path.join(PATHS_DIRS['input_files'], cover_filename)
    except IndexError:
        PATHS_FILES["cover_image"] = None

    def execute_command(command):
        """Executes a shell command, streaming the output to stdout."""
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in iter(process.stdout.readline, ''):
            print(line, end='')
        return process.returncode

    # # Generate sorted list of chapter audio files
    chapters_list = sorted([file for file in os.listdir(PATHS_DIRS['input_files']) if file.endswith((".mp3", ".mp4", ".m4a", ".m4b"))])

    # # Write chapters list for ffmpeg
    with open(PATHS_FILES["chapters_list"], "w") as f:
        for chapter in chapters_list:
            f.write(f"file '{os.path.join(PATHS_DIRS['input_files'], chapter)}'\n")

    def detect_max_bitrate():
        """Detect the highest bitrate among input audio chapters."""
        max_bitrate = 0
        for file in chapters_list:
            process = subprocess.Popen([
                "ffprobe", "-v", "error", "-select_streams", "a:0",
                "-show_entries", "stream=bit_rate", "-of", "default=noprint_wrappers=1:nokey=1",
                os.path.join(PATHS_DIRS['input_files'], file)
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            bitrate = int(process.stdout.readline().strip())
            if bitrate > max_bitrate:
                max_bitrate = bitrate
        return max_bitrate // 1000

    MAX_BITRATE = detect_max_bitrate()

    # Merge audio files
    execute_command(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i",
                     PATHS_FILES["chapters_list"], "-acodec", "aac",
                     "-b:a", f"{MAX_BITRATE}k", PATHS_FILES["output_file"]])

    def get_chapter_duration(file_path):
        """Returns the duration of a chapter in seconds."""
        process = subprocess.run(["ffprobe", "-i", file_path, "-show_entries", "format=duration",
                                  "-v", "quiet", "-of", "csv=p=0"],
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return float(process.stdout.strip())

    def generate_chapters_metadata():
        """Generates metadata file with chapters timestamps."""
        accumulated_duration = 0
        with open(PATHS_FILES["chapters_metadata"], "w") as file:
            file.write(";FFMETADATA1\n")
            for key, value in BOOK_METADATA.items():
                if value:
                    file.write(f"{key}={value}\n")
            file.write("\n")

            for chapter in chapters_list:
                duration = int(get_chapter_duration(os.path.join(PATHS_DIRS['input_files'], chapter)) * 1_000_000)
                chapter_without_extension = os.path.splitext(chapter)[0]
                file.write("[CHAPTER]\n")
                file.write("TIMEBASE=1/1000000\n")
                file.write(f"START={accumulated_duration}\n")
                accumulated_duration += duration
                file.write(f"END={accumulated_duration}\n")
                file.write(f"title={chapter_without_extension}\n\n")

    generate_chapters_metadata()

    # Add chapters metadata to audiobook file
    execute_command(["ffmpeg", "-y", "-i", PATHS_FILES["output_file"], "-i", PATHS_FILES["chapters_metadata"],
                     "-map_metadata", "1", "-map_chapters", "1", "-c", "copy", PATHS_FILES["output_file_temp"]])
    os.rename(PATHS_FILES["output_file_temp"], PATHS_FILES["output_file"])

    # Add cover image if exists
    if PATHS_FILES["cover_image"]:
        execute_command(["ffmpeg", "-y", "-i", PATHS_FILES["output_file"], "-i", PATHS_FILES["cover_image"],
                         "-map", "0:a", "-map", "1:v", "-c", "copy", "-metadata:s:v", "title='Cover'",
                         "-metadata:s:v", "comment='Cover (front)'", "-disposition:v", "attached_pic",
                         PATHS_FILES["output_file_temp"]])
        os.rename(PATHS_FILES["output_file_temp"], PATHS_FILES["output_file"])

    # Clean up temporary files
    for file in os.listdir(PATHS_DIRS['temp_files']):
        os.remove(os.path.join(PATHS_DIRS['temp_files'], file))