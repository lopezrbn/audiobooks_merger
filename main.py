import os
import subprocess


def main(BOOK_METADATA):

    ###########################################################################
    #                           Paths and functions                           #
    ###########################################################################

    PATH_BASE = os.getcwd()
    PATHS_DIRS = {
        "input_files": os.path.join(PATH_BASE, "input_files", BOOK_METADATA['title']),
        "output_files": os.path.join(PATH_BASE, "output_files", BOOK_METADATA['title']),
        "temp_files": os.path.join(PATH_BASE, "temp_files")
    }

    for path in PATHS_DIRS.values():
        os.makedirs(path, exist_ok=True)

    PATHS_FILES = {
        "output_file": os.path.join(PATHS_DIRS['output_files'], f"{BOOK_METADATA['title']}.m4b"),
        "output_file_temp": os.path.join(PATHS_DIRS['temp_files'], f"{BOOK_METADATA['title']}.m4b"),
        "chapters_list": os.path.join(PATHS_DIRS['temp_files'], "chapters_list.txt"),
        "chapters_metadata": os.path.join(PATHS_DIRS['temp_files'], "chapters_metadata.txt"),
    }

    try:
        cover_filename = [file for file in os.listdir(PATHS_DIRS['input_files']) if (file.endswith(".jpg") or file.endswith(".png"))][0]
        PATHS_FILES["cover_image"] = os.path.join(PATHS_DIRS['input_files'], cover_filename)
    except IndexError:
        PATHS_FILES["cover_image"] = None


    def execute_command(command):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in iter(process.stdout.readline, ''):
            print(line, end='')
        return process.returncode


    ###########################################################################
    #                      Generate chapters list                             #
    ###########################################################################

    chapters_list = os.listdir(PATHS_DIRS['input_files'])
    chapters_list = [chapter for chapter in chapters_list if chapter.endswith(".mp3")]
    chapters_list.sort()

    with open(PATHS_FILES["chapters_list"], "w") as f:
        for chapter in chapters_list:
            f.write(f"""file '{os.path.join(PATHS_DIRS["input_files"], chapter)}'\n""")


    ###########################################################################
    #               Detect maximum bitrate of chapter files                   #
    ###########################################################################

    def detect_max_bitrate():
        max_bitrate = 0
        for file in os.listdir(PATHS_DIRS['input_files']):
            if file.endswith(".mp3"):
                process = subprocess.Popen(
                    ["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=bit_rate", "-of", "default=noprint_wrappers=1:nokey=1", f"{os.path.join(PATHS_DIRS['input_files'], file)}"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                for line in iter(process.stdout.readline, ''):
                    bitrate = int(line)
                    if bitrate > max_bitrate:
                        max_bitrate = bitrate
        return max_bitrate / 1000
    
    MAX_BITRATE = int(detect_max_bitrate())


    ###########################################################################
    #               Merge audio files into a unique file                      #
    ###########################################################################

    command = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", PATHS_FILES["chapters_list"], "-acodec", "aac", "-b:a", f"{MAX_BITRATE}k", PATHS_FILES["output_file"]]
    execute_command(command)


    ###########################################################################
    #                          Add chapters metadata                          #
    ###########################################################################

    # Generate chapters metadata

    def get_chapter_duration(file_path):
        command = ["ffprobe", "-i", file_path, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"]
        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return float(process.stdout.strip())
    
    def generate_chapters_metadata():

        accumulated_duration = -1000000

        with open(PATHS_FILES["chapters_metadata"], "w") as file:
            file.write(";FFMETADATA1\n")
            
            for key, value in BOOK_METADATA.items():
                if value:
                    file.write(f"{key}={value}\n")
            file.write("\n")

            for chapter in chapters_list:
                chapter_path = f"{os.path.join(PATHS_DIRS['input_files'], chapter)}"
                duration = int(get_chapter_duration(chapter_path) * 1000000)
                file.write("[CHAPTER]\n")
                file.write(f"TIMEBASE=1/1000000\n")
                file.write(f"START={accumulated_duration + 1000000}\n")
                accumulated_duration += duration
                file.write(f"END={accumulated_duration}\n")
                file.write(f"title={chapter}\n\n")
    
    generate_chapters_metadata()

    # Insert chapters metadata

    command = ["ffmpeg", "-y", "-i", PATHS_FILES["output_file"], "-i", PATHS_FILES["chapters_metadata"], "-map_metadata", "1", "-map_chapters", "1", "-c", "copy", PATHS_FILES["output_file_temp"]]
    execute_command(command)
    os.rename(PATHS_FILES["output_file_temp"], PATHS_FILES["output_file"])


    ###########################################################################
    #                           Add cover image                               #
    ###########################################################################

    if PATHS_FILES["cover_image"] is not None:
        command = ["ffmpeg", "-y", "-i", PATHS_FILES["output_file"], "-i", PATHS_FILES["cover_image"], "-map", "0:a", "-map", "1:v", "-c", "copy", "-metadata:s:v", "title='Cover'", "-metadata:s:v", "comment='Cover (front)'", "-disposition:v", "attached_pic", PATHS_FILES["output_file_temp"]]
        execute_command(command)
        os.rename(PATHS_FILES["output_file_temp"], PATHS_FILES["output_file"])

    
    ###########################################################################
    #                           Remove temp files                             #
    ###########################################################################

    for file in os.listdir(PATHS_DIRS['temp_files']):
        os.remove(os.path.join(PATHS_DIRS['temp_files'], file))