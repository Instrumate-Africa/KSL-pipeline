import os
import json
import math
import argparse
from pathlib import Path

def __least_cost_path (grid: list[list[float]]) -> list[int]:
    aligned_user_frame_idxs: list[int] = []
    rows = len(grid)
    cols = len(grid[0])

    aligned_user_frame_idxs.append(0)

    r_idx, u_idx = 0, 0
    while (u_idx+1) < cols and (r_idx+1) < rows:
        str8, right, left = grid[r_idx+1][u_idx+1], grid[r_idx][u_idx+1], grid[r_idx+1][u_idx]
        next_cell = min(str8, right, left)
        if next_cell == str8:
            u_idx+=1
            r_idx+=1
        elif next_cell == left:
            r_idx+=1
        else:
            u_idx+=1
        aligned_user_frame_idxs.append(u_idx)

    while u_idx < cols:
        aligned_user_frame_idxs.append(u_idx)
        u_idx+=1

    return aligned_user_frame_idxs

def dynamic_time_warp (reference_frames: list[dict], user_frames: list[dict]) -> list[dict]:

    rows = len(reference_frames)
    cols = len(user_frames)
    grid: list[list[float]] = [[0.0 for _ in range(cols)] for _ in range(rows)]

    for r_idx, r_frame in enumerate(reference_frames):
        r_body, r_rhand, r_lhand = (r_frame.get('body', []), r_frame.get('right_hand', []), r_frame.get('left_hand', []))
        for u_idx, u_frame in enumerate(user_frames):
            u_body, u_rhand, u_lhand = (u_frame.get('body', []), u_frame.get('right_hand', []), u_frame.get('left_hand', []))

            # check if hand's, ie 'left'/'right' in user/ref len is 0 in ref/user
            x: bool = (len(u_lhand) == 0 and len(r_lhand) != 0) or (len(u_rhand) == 0 and len(r_rhand) != 0)
            y: bool = (len(u_lhand) != 0 and len(r_lhand) == 0) or (len(u_rhand) != 0 and len(r_rhand) == 0)
            z = x or y

            if z:
                frame_no = u_frame.get('frame')
                raise Exception(f"[ERROR] left/right hand arrays do not match for frame {frame_no} in both reference and user frames!")

            hands_array = [u_lhand, r_lhand] if len(u_lhand) != 0 or len(r_lhand) != 0 else [u_rhand, r_rhand]

            cumulative_frame_landmark_euclidean_distance = 0
            for u_bone, r_bone in zip(u_body, r_body):
                ux, uy, uz = (u_bone['x'], u_bone['y'], u_bone['z'])
                rx, ry, rz = (r_bone['x'], r_bone['y'], r_bone['z'])
                ed = math.sqrt((ux-rx)**2 + (uy-ry)**2 + (uz-rz)**2)
                cumulative_frame_landmark_euclidean_distance += ed

            for u_bone, r_bone in zip(hands_array[0], hands_array[1]):
                ux, uy, uz = (u_bone['x'], u_bone['y'], u_bone['z'])
                rx, ry, rz = (r_bone['x'], r_bone['y'], r_bone['z'])
                ed = math.sqrt((ux-rx)**2 + (uy-ry)**2 + (uz-rz)**2)
                cumulative_frame_landmark_euclidean_distance += ed

            # grid[row-> refs][col -> user]
            grid[r_idx][u_idx] = round(cumulative_frame_landmark_euclidean_distance, 4)

    aligned_user_frame_idxs = __least_cost_path (grid)
    aligned_user_frames: list[dict] = [user_frames[i] for i in aligned_user_frame_idxs]

    return aligned_user_frames

def main ():

    parser = argparse.ArgumentParser(
            description="""
            Compare input frames to reference frames and produce a JSON file
            with input frames as close as possible to the reference frames.
            """
            )

    parser.add_argument("-i", "--input-file", required=True,
                        help="Path to JSON file to be compared to the reference frames.")
    parser.add_argument("-r", "--reference-file", required=True,
                        help="Path to JSON file to compare <input-file> to.")
    parser.add_argument("-o", "--output-dir", default="out",
                        help="Path to output directory. File will be the same as <input-file>")

    args = parser.parse_args()

    if not os.path.isfile(args.input_file):
        raise Exception(f"[ERROR] '{args.input_file}' is not a valid file!")

    if not os.path.isfile(args.reference_file):
        raise Exception(f"[ERROR] '{args.reference_file}' is not a valid file!")

    if not os.path.isdir(args.output_dir):
        os.makedirs(args.output_dir)

    input_file = open(args.input_file,'r')
    reference_file = open(args.reference_file,'r')

    input_data = json.loads (input_file.read())
    ref_data = json.loads (reference_file.read())

    aligned_user_frames = dynamic_time_warp (reference_frames=ref_data['frames'], user_frames=input_data['frames'])

    full_input_filename = Path(args.input_file)
    out_file = os.path.join(args.output_dir, full_input_filename.stem)
    with open(out_file, 'w') as out:
        out.write(json.dumps(aligned_user_frames))

if __name__ == "__main__":
    main ()
