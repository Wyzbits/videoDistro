from gather_videos import *
from edit_video import *
from upload_video_to_insta import *
from upload_video_to_tiktok import *
from upload_video_to_youtube import *
import subprocess


def main():

    subprocess.run(
        [get_reddit_videos(), "../tieUp.sh",  upload_video_to_youtube()])


if __name__ == "__main__":
    main()
