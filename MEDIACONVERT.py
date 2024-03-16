import os
import re
import sys
import time
import threading
import subprocess
from pathlib import Path

DOWNLOAD_DIRECTORY = os.path.join(os.path.expanduser("~"), "Downloads", "PLAY")

# SET PATHS FOR FFMPEG.EXE
script_directory = os.path.dirname(os.path.abspath(__file__))
quantum = os.path.join(script_directory, r"_RES\QUANTUM.exe")
phantom = os.path.join(script_directory, r"_RES\PHANTOM.exe")

# Check if Quantum executable exists
if not os.path.isfile(quantum):
    print(f"ERROR: QUANTUM.EXE EXECUTABLE FILE NOT FOUND.")

if not os.path.isfile(phantom):
    print(f"ERROR: PHANTOM.EXE EXECUTABLE FILE NOT FOUND.")


def clear_console():
    # CLEAR CONSOLE SCREEN
    if os.name == "nt":
        _ = os.system("cls")  # FOR WINDOWS
    else:
        _ = os.system("clear")  # FOR LINUX/MACOS


def get_duration(file_path):
    command = f'{phantom} -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{file_path}"'
    output = subprocess.check_output(command, shell=True).decode("utf-8").strip()
    return float(output)


def convert_video(
    input_file,
    codec,
    output_format,
    resolution,
    audio_codec,
    audio_bitrate,
    video_number,
):
    output_folder = DOWNLOAD_DIRECTORY
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    file_extension = os.path.splitext(input_file)[1][1:]
    if file_extension.lower() in [
        "mp4",
        "avi",
        "mkv",
        "flv",
        "mov",
        "wmv",
        "m4v",
        "mpeg",
        "mpg",
        "webm",
        "3gp",
        "asf",
        "rm",
        "swf",
        "vob",
    ]:
        output_file = os.path.join(
            output_folder,
            f"{os.path.splitext(os.path.basename(input_file))[0]}_{codec}.{output_format}",
        )
        command = f'{quantum} -y -hide_banner -hwaccel auto -i "{input_file}" -c:v {codec} -s {resolution} -c:a {audio_codec} -b:a {audio_bitrate} -filter:v fps=30 -ar 48000 "{output_file}"'
        # [ -preset slow -preset ultrafast -b:v 5M ]
        duration = get_duration(input_file)
        start_time = time.time()
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            encoding="utf-8",
            shell=True,
        )

        for line in process.stdout:
            match = re.search(r"time=(\d+:\d+:\d+.\d+)", line)
            if match:
                time_str = match.group(1)
                h, m, s = map(float, time_str.split(":"))
                elapsed_time = h * 3600 + m * 60 + s
                progress = min(elapsed_time / duration, 1.0)
                progress_percentage = round(progress * 100, 2)

                if progress > 0.99:
                    progress_percentage = 100.0

                bar_length = 20
                filled_length = int(progress * bar_length)
                empty_length = bar_length - filled_length
                bar = f'[{"=" * filled_length}{" " * (empty_length - 1)}]'
                elapsed_time_sec = time.time() - start_time
                minutes = int(elapsed_time_sec // 60)
                seconds = int(elapsed_time_sec % 60)
                progress_line = f"\r-VIDEO: [{video_number}] PROGRESS: {bar} -{progress_percentage:.2f} - TIME: {minutes}:{seconds} SEC "
                sys.stdout.write(progress_line)
                sys.stdout.flush()

        print(f"\n-VIDEO: [{video_number}] CONVERSION COMPLETED.")


def convert_videos_in_folder(
    folder_path, codec, output_format, resolution, audio_codec, audio_bitrate
):
    folder_path = Path(folder_path)

    if not folder_path.is_dir():
        print("INVALID FOLDER PATH. PLEASE PROVIDE A VALID FOLDER PATH.")
        return

    video_files = list(folder_path.rglob("*.*"))
    video_files = [
        file
        for file in video_files
        if file.suffix.lower()
        in {
            ".mp4",
            ".avi",
            ".mkv",
            ".flv",
            ".mov",
            ".wmv",
            ".m4v",
            ".mpeg",
            ".mpg",
            ".webm",
            ".3gp",
            ".asf",
            ".rm",
            ".swf",
            ".vob",
        }
    ]
    video_count = len(video_files)

    if video_count == 0:
        print("NO VIDEO FILES FOUND IN THE SPECIFIED FOLDER.")
        return

    converted_count = 0
    threads = []

    for i, video_file in enumerate(video_files, start=1):
        clear_console()
        print(f"CONVERTING : RESOLUTION: [{resolution}] | VIDEO CODEC: [{codec}] | OUTPUT FORMAT: [{output_format}] | AUDIO CODEC: [{audio_codec}]", end="")
        print(f"\nCONVERTING VIDEO [{i}] OF [{video_count}]")
        print("CONVERSION START...")
        print(" ")
        thread = threading.Thread(
            target=convert_video,
            args=(
                str(video_file),
                codec,
                output_format,
                resolution,
                audio_codec,
                audio_bitrate,
                i,
            ),
        )
        threads.append(thread)
        thread.start()
        thread.join()

        converted_count += 1  # INCREMENTING THE CONVERTED_COUNT
        print(" ")

    for thread in threads:
        thread.join()

    time.sleep(5)
    clear_console()
    input("VIDEO CONVERSION COMPLETE..\nPRESS ENTER TO RETURN MAIN MENU...")
    clear_console()
    print("WAIT..", end="", flush=True)
    time.sleep(5)
    clear_console()


def convert_videos_to_audio(folder_path, audio_codec, audio_bitrate):
    output_folder = DOWNLOAD_DIRECTORY
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    audio_number = 0  # INITIALIZE AUDIO NUMBER COUNTER

    for i, (root, dirs, files) in enumerate(os.walk(folder_path), start=1):
        clear_console()
        print("AUDIO CONVERSION START...")
        print(f"CONVERTING : AUDIO CODEC: [{audio_codec}] | AUDIO BITRATE: [{audio_bitrate}]", end="")
        print(" ")
        for file in files:
            file_path = os.path.join(root, file)
            file_extension = os.path.splitext(file_path)[1][1:]
            if file_extension.lower() in [
                "mp4",
                "avi",
                "mkv",
                "flv",
                "mov",
                "wmv",
                "m4v",
                "mpeg",
                "mpg",
                "webm",
                "3gp",
                "asf",
                "rm",
                "swf",
                "vob",
            ]:
                audio_number += 1  # Increment audio number counter
                output_file = os.path.join(
                    output_folder,
                    f"{os.path.splitext(os.path.basename(file))[0]}.{audio_codec}",
                )
                command = f'{quantum} -y -hide_banner -hwaccel auto -i "{file_path}" -vn -c:a {audio_codec} -b:a {audio_bitrate} -ar 48000 "{output_file}" 2> NUL'
                subprocess.call(command, shell=True)

                print(f"\nAUDIO: [{audio_number}] CONVERSION COMPLETED.")

    time.sleep(3)
    clear_console()
    input("AUDIO CONVERSION COMPLETED...\nPRESS ENTER TO RETURN MAIN MENU...")
    clear_console()
    print("WAIT..", end="", flush=True)
    time.sleep(3)
    clear_console()


clear_console()


def is_valid_path(path):
    """
    CHECK IF THE PROVIDED PATH EXISTS AND IS A DIRECTORY.
    """
    return os.path.isdir(path)


while True:
    print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    print("┃      CHOOSE AN OPTION     ┃")
    print("┣━━━━━━━━━━━━━━━━━━━━━━━━━━━┫")
    print("┃ 1. CONVERT A VIDEO        ┃")
    print("┃ 2. CONVERT A AUDIO        ┃")
    print("┃ 3. EXIT                   ┃")
    print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")

    option = input("ENTER THE NUMBER OF THE OPTION: ")

    if option == "1":
        folder_path = input("ENTER THE FOLDER PATH: ")

        if not is_valid_path(folder_path):
            clear_console()
            print("INVALID FOLDER PATH. PLEASE PROVIDE A VALID FOLDER PATH.")
            continue

        clear_console()
        print("CHOOSE A RESOLUTION:")
        print("1. 3840p")
        print("2. 1440p")
        print("3. 1080p")
        print("4. 720p")
        print("5. 480p")
        print("6. 360p")
        print("7. 240p")
        print("8. 144p")
        resolution_option = input("ENTER THE NUMBER OF THE RESOLUTION: ")

        resolution_dict = {
            "1": "3840x2160",
            "2": "2560x1440",
            "3": "1920x1080",
            "4": "1280x720",
            "5": "640x480",
            "6": "640x360 ",
            "7": "320x240",
            "8": "256x144",
        }

        resolution = resolution_dict.get(resolution_option)
        if resolution is None:
            clear_console()
            print("INVALID RESOLUTION. PLEASE TRY AGAIN.")
            continue

        clear_console()
        print("CHOOSE A VIDEO CODEC:")
        print("1. VP9")
        print("2. MPEG4")
        print("3. LIBVPX")
        print("4. LIBX264")
        print("5. LIBX265")
        print("6. H264_NVENC")
        codec_option = input("ENTER THE NUMBER OF THE CODEC: ")

        codec_dict = {
            "1": "vp9",
            "2": "mpeg4",
            "3": "libvpx",
            "4": "libx264",
            "5": "libx265",
            "6": "h264_nvenc",
        }

        codec = codec_dict.get(codec_option)
        if codec is None:
            clear_console()
            print("INVALID CODEC. PLEASE TRY AGAIN.")
            continue

        clear_console()
        print("CHOOSE A OUTPUT FORMAT:")
        print("1. MP4")
        print("2. AVI")
        print("3. MKV")
        print("4. MOV")
        print("5. WMV")
        format_option = input("ENTER THE NUMBER OF THE FORMAT: ")

        format_dict = {"1": "mp4", "2": "avi", "3": "mkv", "4": "mov", "5": "wmv"}

        output_format = format_dict.get(format_option)
        if output_format is None:
            clear_console()
            print("INVALID FORMAT. PLEASE TRY AGAIN.")
            continue

        clear_console()
        print("CHOOSE AN AUDIO CODEC:")
        print("1. AAC")
        print("2. MP3")
        print("3. WMA")
        print("4. M4A")
        print("5. FLAC")
        print("6. Dolby Digital (E-AC-3)")
        audio_codec_option = input("ENTER THE NUMBER OF THE AUDIO CODEC: ")

        audio_codec_dict = {
            "1": "aac",
            "2": "mp3",
            "3": "wma",
            "4": "m4a",
            "5": "flac",
            "6": "eac3",  # Dolby Digital (AC-3)
        }

        audio_codec = audio_codec_dict.get(audio_codec_option)
        if audio_codec is None:
            clear_console()
            print("INVALID AUDIO CODEC. PLEASE TRY AGAIN.")
            continue

        clear_console()
        print("CHOOSE AN AUDIO BITRATE:")
        print("1. 128k")
        print("2. 192k")
        print("3. 256k")
        print("4. 320k")
        print("5. 1411k")
        audio_bitrate_option = input("ENTER THE NUMBER OF THE AUDIO BITRATE: ")

        audio_bitrate_dict = {
            "1": "128k",
            "2": "192k",
            "3": "256k",
            "4": "320k",
            "5": "1411k",
        }

        audio_bitrate = audio_bitrate_dict.get(audio_bitrate_option)
        if audio_bitrate is None:
            clear_console()
            print("INVALID AUDIO BITRATE. PLEASE TRY AGAIN.")
            continue
        clear_console()

        convert_videos_in_folder(
            folder_path, codec, output_format, resolution, audio_codec, audio_bitrate
        )

    elif option == "2":
        folder_path = input("ENTER THE FOLDER PATH: ")

        if not is_valid_path(folder_path):
            clear_console()
            print("INVALID FOLDER PATH. PLEASE PROVIDE A VALID FOLDER PATH.")
            continue

        clear_console()
        print("CHOOSE AN OUTPUT FORMAT:")
        print("1. MP3")
        print("2. AAC")
        print("3. AC3")
        print("4. FLAC")
        audio_codec_option = input("ENTER THE NUMBER OF THE AUDIO CODEC: ")
    
        audio_codec_dict = {
            "1": "mp3",
            "2": "aac",  
            "3": "ac3",
            "4": "flac",
        }
        audio_codec = audio_codec_dict.get(audio_codec_option)

        # CHECK IF THE CHOSEN AUDIO CODEC IS VALID
        if audio_codec is None:
            clear_console()
            print("INVALID AUDIO CODEC. PLEASE TRY AGAIN.")
            continue

        clear_console()
        print("CHOOSE AN AUDIO BITRATE:")
        print("1. 128k")
        print("2. 192k")
        print("3. 256k")
        print("4. 320k")
        print("5. 1411k")
        audio_bitrate_option = input("ENTER THE NUMBER OF THE AUDIO BITRATE: ")

        audio_bitrate_dict = {
            "1": "128k",
            "2": "192k",
            "3": "256k",
            "4": "320k",
            "5": "1411k",
        }

        audio_bitrate = audio_bitrate_dict.get(audio_bitrate_option)
        if audio_bitrate is None:
            clear_console()
            print("INVALID AUDIO BITRATE. PLEASE TRY AGAIN.")
            continue

        convert_videos_to_audio(folder_path, audio_codec, audio_bitrate)

    elif option == "3":
        clear_console()
        print("EXITING TOOL..")
        time.sleep(5)
        clear_console()
        break
    else:
        clear_console()
        print("INVALID OPTION. PLEASE ENTER 1, 2, OR 3.")
        continue


