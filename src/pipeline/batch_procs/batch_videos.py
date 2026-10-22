import os
import shutil
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-d", "--video-dir", required=True, help="Directory where videos for processing are. [.mp4, .avi, .mov].")
    parser.add_argument("-b", "--batch-limit", default=250, help="Maximum number of videos to put in each batch.")
    args = parser.parse_args()

    if not os.path.isdir(args.video_dir):
        raise Exception(f"[ERROR] '{args.video_dir}' is not a valid directory")

    batch_no: int = 0
    batch_dir = f"batch-{batch_no}";
    batch_filepath = os.path.join(args.video_dir, batch_dir)
    for i, filename in enumerate([f for f in os.listdir(args.video_dir) if f.endswith((".mp4", ".mov", ".avi"))]):
        batch_no = i // int(args.batch_limit)
        batch_dir = f"batch-{batch_no}";
        batch_filepath = os.path.join(args.video_dir, batch_dir)
        os.makedirs(batch_filepath, exist_ok=True)
        old_filepath = os.path.join(args.video_dir, filename)
        shutil.move(old_filepath, batch_filepath)
