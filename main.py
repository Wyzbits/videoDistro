from gather_videos import *
from edit_video import *
from upload_video_to_insta import *
from upload_video_to_tiktok import *
from upload_video_to_youtube import *
from upload import upload_video
import subprocess


def main():
    subprocess.run(
        ['python3', '-c', 'import gather_videos; gather_videos.get_reddit_videos()'])
    subprocess.run(["bash", "../tieUp.sh"])
    subprocess.run["python3", "-c", "import upload;" "upload.upload_video()"]


if __name__ == "__main__":
    main()
