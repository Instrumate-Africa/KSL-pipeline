import os
import sys
from pathlib import Path
import numpy as np
from typing import cast

current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

import extract, normalize


tmp_dir = "data/npy"
def process_video(video_path, opts):
    os.makedirs(tmp_dir, exist_ok=True)
    try:
        coords_np: np.ndarray = cast(
                np.ndarray,
                extract.extract_sign_poses(video_path=video_path, opts=opts, output_as_ndarray=True)
                )
        if coords_np is None or not isinstance(coords_np, np.ndarray) or coords_np.ndim < 2 or coords_np.size == 0:
            return {
                    "video": str(video_path),
                    "status": "error",
                    "message": "No poses detected or invalid array returned from extractor."
                    }
        hip_centers, shoulder_widths, norm_frames = normalize.np_normalize(coords_np)
        name: str = os.path.splitext(os.path.basename(video_path))[0].lower().strip("- ")
        dir_name = os.path.join(tmp_dir, name)
        os.makedirs(dir_name)
        hc_filepath = os.path.join(dir_name, name + "_hc")
        sw_filepath = os.path.join(dir_name, name + "_sw")
        frames_filepath = os.path.join(dir_name, name + "_f")

        np.save(hc_filepath, hip_centers)
        np.save(sw_filepath, shoulder_widths)
        np.save(frames_filepath, norm_frames)

        return {"video": str(video_path), "status": "success"}

    except Exception as e:
        return {"video": str(video_path), "status": "error", "message": str(e)}


