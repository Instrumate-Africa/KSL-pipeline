## KSL PIPELINE

### Introduction
This is a pipeline designed for the purpose of end-to-end processing of videos of KSL signing and turning them into coordinates which
can be used in 3D environments.

Processes in this pipeline include the following:
#### 1. Extraction
This script lives in `src/extract.py`. It is used to extract the raw pose coordinates from the input video, and can either output them
as json(useful for debugging or checking out the structure, though might be slow) or a numpy array.
```bash
$ python src/extract.py --help
```

#### 2. Normalization
The script is located at `src/normalize.py`. It takes the output of `src/extract.py` and normalizes the coordinates. It calculates the
hip center from both hips and uses that as a stable point of the body, and makes every other point relative to the hip center(normalize),
then scales those points using the shoulder width from each frame.
```bash
$ python src/normalize.py --help
```

#### 3. Saving to a database
This script, located at `src/save_to_db.py`, is used by the batch operation scripts to save coordinates to the database.
Not meant to be used in standalone unless you follow the file structure it expects.

#### 4. Alignment
This script is located at `src/dynamic_time_warp.py`. It uses [dynamic time warping](https://en.wikipedia.org/wiki/Dynamic_time_warping),
which is an algorithm used to measure similarity between two temporal sequences, in this case, it is used to compare between frames extracted
from user videos, and reference frames from our database, and align the ones that are most similar, in preparation for the next step.

```bash
$ python src/dynamic_time_warp.py --help
```

#### 5. Diffing
This script is located at `src/diffing.py`. It takes in the output of the previous part, which is a list of aligned frame indices,
and compares the actual differences between them, on various levels, ie, finger spread/curl, elbow position of both hands, etc. It 
then provides a list of feedback on what is right or wrong with the user's frames.


### Batch Operations
This part of the pipeline utilizes the `extraction`, `normalization` and `saving` parts of the pipeline, to process a group of KSL videos
and save their coordinates into a sqlite database.

Source at `src/batch_procs`.

- `batch_on_cpu.py` -> This script spreads operations on multiple cores, the operations mentioned above. The number of cores/threads
can be passed into the script.
- `batch_on_gpu.py` -> This script spreads operations on multiple GPU workers. Use `--help` to see other flags.
- `batch_videos.py` -> This script separates a whole group of videos into batches, incase you wanna do batched runs. It takes in a batch
limit, and divides the videos into batches whose maximum is `batch-limit`.

The `proc.py` is the actual single unit of processing that will be distributed on the various cores, processing at most one video at a time.
