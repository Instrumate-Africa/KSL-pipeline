import os

# Force software rendering and disable hardware/OpenGL context sharing
os.environ["LIBGL_ALWAYS_SOFTWARE"] = "1"
os.environ["MEDIAPIPE_DISABLE_GPU"] = "1"

import argparse
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

import proc
import extract, save_to_db

if __name__ == "__main__":
    n_cores = os.cpu_count()
    n_cores = 1 if n_cores is None else n_cores - 1

    parser = argparse.ArgumentParser(description="[CPU version] EXTRACT, NORMALIZE and SAVE a batch of pose video coords to a db.")
    parser.add_argument("-d", "--video-dir", required=True, help="Directory where videos are. [.mp4, .avi, .mov].")
    parser.add_argument("-m", "--model-dir", default=".", help="Directory where models are installed, or are to be installed in.")
    parser.add_argument("-s", "--sqlite-path", default=".", help="Path where sqlite database will be placed or where it exists.")
    parser.add_argument("-t", "--threads", default=n_cores, help="Number of CPU threads to use for processing.")
    args = parser.parse_args()

    if not os.path.isdir(args.video_dir):
        raise Exception(f"[ERROR] '{args.video_dir}' is not a valid directory")

    video_dir = Path(args.video_dir)
    video_files = sorted(list(set(video_dir.glob("*.mp4")) | set(video_dir.glob("*.avi")) | set(video_dir.glob("*.mov"))))

    max_workers = max(1, args.threads)
    print(f"[INFO] Starting pipeline across {max_workers} CPU threads for {len(video_files)} videos...")

    with open("batch.log", "w") as log_file:
        opts = extract.setup_models(args.model_dir)
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            future_to_video = {
                executor.submit(proc.process_video, video, opts): video
                for video in video_files
            }

            for future in as_completed(future_to_video):
                result = future.result(timeout=300)
                if result["status"] == "error":
                    log_file.write(f"[ FAILED]: video: {result['video']} | message: {result['message']}\n")
                    continue
                log_file.write(f"[SUCCESS]: {result['video']}\n")

    db: str = args.sqlite_path
    if os.path.isdir(args.sqlite_path):
        db = os.path.join(db, "dataset_with_hands.sqlite3.db")
    else:
        if len(db) == 0:
            db = "dataset_with_hands.sqlite3.db"

    save_to_db.db_save(db, proc.tmp_dir)
    print (f"[OK] Finished. outputDB: '{db}'.")
