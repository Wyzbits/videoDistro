import json
from math import floor
import subprocess
import re
import os


SEGEMENT = 50


def extract_last_video():
    with open("videos.json", "r") as f:
        data = json.load(f)
        videos = data["videos"]
        last_video = videos[-1]
        video_url = last_video["video_url"]
        # return the last part after .com/ of the string
        if "youtube" in video_url:
            video_id = video_url.split("=")[-1]
        else:
            video_id = video_url.split("/")[-1]

        video_title = last_video["video_title"]
        video_url = last_video["video_url"]
        return {
            "video_id": video_id,
            "video_title": video_title,
            "video_url": video_url,
        }


def get_video_seconds():
    # get video length
    cmd = "ffmpeg -i ./last_video_download/video.mp4 2>&1 | grep 'Duration' | cut -d ' ' -f 4 | sed s/,//"
    output = subprocess.check_output(cmd, shell=True)
    output = output.decode("utf-8")

    seconds = 0
    for time in output.split(":"):
        seconds = seconds * 60 + float(time)
    return seconds


def update_json_parts(video_id):
    video = extract_last_video()
    parts = []
    # list the files alpabetically
    for file in sorted(os.listdir(f"./video_parts/{video_id}")):
        if file.endswith(".mp4"):
            parts.append(file)
    with open("video_parts.json", "r") as f:
        data = json.load(f)
        videos = data["video_parts"]
        videos.append(
            {
                "video_id": video["video_id"],
                "video_title": video["video_title"],
                "video_url": video["video_url"],
                "parts": parts,
            }
        )
    with open("video_parts.json", "w") as f:
        json.dump(data, f, indent=4)


def get_first_video_with_parts():
    with open("video_parts.json", "r") as file:
        data = json.load(file)
        videos = data["video_parts"]
        for video in videos:
            if len(video["parts"]) > 0:
                return f"./video_parts/{video['video_id']}/{video['parts'][0]}"


def get_video_file_size():
    # get video file size with ff
    cmd_str = "du -h ./last_video_download/video.mp4 | cut -f1"
    output = subprocess.check_output(cmd_str, shell=True)
    output = output.decode("utf-8")
    output = output.replace("M", "")
    # return output as float
    return float(output)


def create_folder(video_id):
    create_folder_cmd = f"mkdir ./video_parts/{video_id}"
    subprocess.run(create_folder_cmd, shell=True)


def cut_video(video_id, seconds_split):
    cut_video_cmd = f"ffmpeg -i ./last_video_download/video.mp4 -f segment -segment_time {seconds_split} -vcodec copy -acodec copy -reset_timestamps 1 -map 0:0 -map 0:1 ./video_parts/{video_id}/{video_id}_video_part_%d.mp4"
    subprocess.run(cut_video_cmd, shell=True)


def compress_video():
    compress_video_cmd = f"ffmpeg -i ./last_video_download/video.mp4 -vcodec libx264 -crf 23 ./edit_video/video.mp4 "
    subprocess.run(compress_video_cmd, shell=True)


def write_to_queue(scrFolder, video_folder_src, title):
    cmd = f"mv {scrFolder} ./video_upload_queue/{video_folder_src}"
    # write to queue json
    with open("queue.json", "r") as f:
        data = json.load(f)
        queue = data["queue"]
        queue.append(
            {
                "video_src": video_folder_src,
                "video_title": title,
            }
        )
    with open("queue.json", "w") as f:
        json.dump(data, f, indent=4)
    subprocess.run(cmd, shell=True)


def clean_up_by_id(video_id):
    with open("video_parts.json", "r") as f:
        data = json.load(f)
        videos = data["video_parts"]
        for video in videos:
            if video["video_id"] == video_id:
                video["parts"].pop(0)
    with open("video_parts.json", "w") as f:
        json.dump(data, f, indent=4)


def cut_last_three_seconds():
    cut_last_three_seconds_cmd = f"ffmpeg -i ./last_video_download/video.mp4 -ss 0 -t 00:00:03 -c copy ./edit_video/video.mp4"
    subprocess.run(cut_last_three_seconds_cmd, shell=True)


def delete_video():
    delete_video_cmd = "rm -rf ./last_video_download/video.mp4"
    subprocess.run(delete_video_cmd, shell=True)


def get_cutting_part(seconds, segment_time=SEGEMENT):
    if seconds % segment_time <= 1 and segment_time <= SEGEMENT:
        return segment_time
    elif segment_time <= 30:
        return segment_time
    return get_cutting_part(seconds=seconds, segment_time=segment_time - 1)


def edit_video():
    video_id = extract_last_video()["video_id"]
    title = extract_last_video()["video_title"]
    file_size = get_video_file_size()
    seconds = get_video_seconds()
    if seconds <= 60 and file_size > 50:
        compress_video()
        write_to_queue("./edit_video/video.mp4", f"{video_id}_video.mp4", title)
    elif seconds > 60:
        segment_time = get_cutting_part(seconds)
        create_folder(video_id)
        cut_video(video_id, segment_time)
        update_json_parts(video_id)
        delete_video()
        write_to_queue(
            f"video_parts/{video_id}/{video_id}_video_part_0.mp4",
            f"{video_id}_video_part_0.mp4",
            title,
        )
        clean_up_by_id(video_id)
    else:
        write_to_queue(
            "./last_video_download/video.mp4", f"{video_id}_video.mp4", title
        )
