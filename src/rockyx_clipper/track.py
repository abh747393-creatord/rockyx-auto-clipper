import sys
import os
import json
import subprocess
import numpy as np

os.environ.setdefault("OPENCV_LOG_LEVEL", "ERROR")

try:
    import cv2
except ImportError:
    print("Error: cv2 not found", file=sys.stderr)
    sys.exit(1)

import shutil

# YuNet model ships with the project (models/yunet_2023mar.onnx, MIT via OpenClip Studio).
_PKG_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_YUNET_PATH = os.path.normpath(os.path.join(_PKG_DIR, '..', '..', 'models', 'yunet_2023mar.onnx'))
CANDIDATE_YUNET_PATHS = [
    LOCAL_YUNET_PATH,
    os.path.expanduser("~/.cache/huggingface/hub/models--opencv--face_detection_yunet/snapshots/3cc26e7f1014a5ee5d74a42acee58bafc9d0a310/face_detection_yunet_2023mar.onnx"),
    "/app/server/services/models/face_detection_yunet_2023mar.onnx"
]

def get_yunet_model_path():
    for p in CANDIDATE_YUNET_PATHS:
        if os.path.exists(p) and os.path.getsize(p) > 1000:
            return p
    try:
        os.makedirs(os.path.dirname(LOCAL_YUNET_PATH), exist_ok=True)
        import urllib.request
        url = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
        urllib.request.urlretrieve(url, LOCAL_YUNET_PATH)
        if os.path.exists(LOCAL_YUNET_PATH):
            return LOCAL_YUNET_PATH
    except Exception as e:
        print(f"Warning: Failed to auto-download YuNet: {e}", file=sys.stderr)
    return None

def resolve_ffmpeg_bin():
    found = shutil.which('ffmpeg')
    if found:
        return found
    if os.environ.get('FFMPEG_PATH') and os.path.exists(os.environ.get('FFMPEG_PATH')):
        return os.environ.get('FFMPEG_PATH')
    # Try finding ffmpeg-static from project root or server dir
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(script_dir, '..', '..', 'node_modules', 'ffmpeg-static', 'ffmpeg'),
        os.path.join(script_dir, '..', 'node_modules', 'ffmpeg-static', 'ffmpeg'),
        '/opt/render/project/src/node_modules/ffmpeg-static/ffmpeg',
        '/usr/local/bin/ffmpeg',
        '/usr/bin/ffmpeg'
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return 'ffmpeg'

def _median(xs):
    return float(np.median(xs)) if xs else 0.0


def _is_facecam(faces: list[dict]) -> bool:
    """True when a face cluster is a stream webcam overlay, not a speaker:
    a small face sitting in a corner of the frame (top-left / bottom-right
    facecam of a gameplay stream, a reaction video, a news inset). A real
    second speaker in a podcast/interview is large and near the centre."""
    if len(faces) < 6:
        return False
    med_w = _median([f["w"] for f in faces])
    med_cx = _median([f["cx"] for f in faces])
    med_cy = _median([f["cy"] for f in faces])
    small = med_w < 0.15
    corner = med_cx < 0.22 or med_cx > 0.78 or med_cy < 0.30 or med_cy > 0.70
    return bool(small and corner)


def decide_two_speakers(left_faces: list[dict], right_faces: list[dict],
                        center_faces: list[dict]) -> tuple[bool, float, float]:
    """Two-speaker split-screen decision from per-frame face records.

    Returns (has_two_speakers, avg_left_x, avg_right_x). Split-screen is
    only real when BOTH clusters are substantial, together outweigh the
    centre, are far enough apart that the two panels do not show the same
    region twice, and NEITHER cluster is a stream facecam."""
    left_cx = [f["cx"] for f in left_faces]
    right_cx = [f["cx"] for f in right_faces]
    center_cx = [f["cx"] for f in center_faces]
    avg_left = float(np.mean(left_cx)) if left_cx else 0.32
    avg_right = float(np.mean(right_cx)) if right_cx else 0.68
    has_two = (
        len(left_cx) >= 6
        and len(right_cx) >= 6
        and (len(left_cx) + len(right_cx)) > len(center_cx)
        and (avg_right - avg_left) >= 0.30
        and not _is_facecam(left_faces)
        and not _is_facecam(right_faces)
    )
    return bool(has_two), avg_left, avg_right


def track_subject(video_path, start_time, duration, sample_fps=4):
    """
    Cinema-Grade High-Fidelity Active Speaker Tracking:
    - Runs at 4 FPS sampling rate for responsive, lag-free motion capture.
    - Preserves native 16:9 aspect ratio (640x360) so face proportions are not distorted.
    - Employs Gaussian Moving Average & Cinema Deadband for butter-smooth camera panning.
    """
    abs_video_path = os.path.abspath(video_path)
    if not os.path.exists(abs_video_path):
        return {
            "duration": duration,
            "sampleCount": 0,
            "avgX": 0.5,
            "avgXPercent": 50.0,
            "primarySpeakerXPercent": 50.0,
            "hasTwoSpeakers": False,
            "speakerLeftPercent": 30.0,
            "speakerRightPercent": 70.0,
            "trajectory": []
        }

    yunet_path = get_yunet_model_path()
    if not yunet_path:
        print("Warning: Face model not found, falling back to center (50%)", file=sys.stderr)
        return {
            "duration": duration,
            "sampleCount": 0,
            "avgX": 0.5,
            "avgXPercent": 50.0,
            "primarySpeakerXPercent": 50.0,
            "hasTwoSpeakers": False,
            "speakerLeftPercent": 30.0,
            "speakerRightPercent": 70.0,
            "trajectory": []
        }

    # Initialize OpenCV C++ FaceDetectorYN with native 16:9 proportional dimensions (640x360)
    frame_w = 640
    frame_h = 360
    detector = cv2.FaceDetectorYN.create(
        yunet_path,
        '',
        (frame_w, frame_h),
        0.30,  # Score threshold
        0.25,  # NMS threshold
        5000
    )

    ffmpeg_bin = resolve_ffmpeg_bin()

    # Stream frames scaled to 640x360 BGR via fast FFmpeg seeking (preserving 16:9 aspect ratio)
    cmd = [
        ffmpeg_bin,
        '-v', 'quiet',
        '-ss', str(start_time),
        '-t', str(duration),
        '-i', abs_video_path,
        '-vf', f'fps={sample_fps},scale={frame_w}:{frame_h}',
        '-f', 'image2pipe',
        '-vcodec', 'rawvideo',
        '-pix_fmt', 'bgr24',
        '-'
    ]

    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Failed to spawn FFmpeg ({ffmpeg_bin}): {e}", file=sys.stderr)
        return {
            "duration": duration,
            "sampleCount": 0,
            "avgX": 0.5,
            "avgXPercent": 50.0,
            "primarySpeakerXPercent": 50.0,
            "hasTwoSpeakers": False,
            "speakerLeftPercent": 30.0,
            "speakerRightPercent": 70.0,
            "trajectory": []
        }

    frame_size = frame_w * frame_h * 3
    time_step = 1.0 / sample_fps

    frame_detections = []
    current_t = 0.0

    while True:
        raw_frame = proc.stdout.read(frame_size)
        if not raw_frame or len(raw_frame) < frame_size:
            break

        img = np.frombuffer(raw_frame, dtype=np.uint8).reshape((frame_h, frame_w, 3))
        detector.setInputSize((frame_w, frame_h))
        _, raw_faces = detector.detect(img)

        faces = []
        if raw_faces is not None and len(raw_faces) > 0:
            for f in raw_faces:
                box = f[0:4]
                conf = float(f[-1])
                if conf < 0.28:
                    continue
                w_frac = float(box[2] / float(frame_w))
                h_frac = float(box[3] / float(frame_h))
                cx = float((box[0] + box[2] / 2.0) / float(frame_w))
                cy = float((box[1] + box[3] / 2.0) / float(frame_h))
                area = w_frac * h_frac
                faces.append({
                    'cx': cx,
                    'cy': cy,
                    'w': w_frac,
                    'area': area,
                    'conf': conf
                })

        frame_detections.append({'t': current_t, 'faces': faces})
        current_t += time_step

    proc.stdout.close()
    proc.wait()

    # Step 2: Extract all valid face centers
    all_face_centers = []
    for fd in frame_detections:
        for fc in fd['faces']:
            if 0.06 <= fc['cx'] <= 0.94:
                all_face_centers.append(fc['cx'])

    if not all_face_centers:
        default_x = 0.50
        traj = [{"t": round(fd['t'], 2), "x": default_x, "xPercent": 50.0, "activeSpeaker": "center"} for fd in frame_detections]
        return {
            "duration": duration,
            "sampleCount": len(traj),
            "avgX": default_x,
            "avgXPercent": 50.0,
            "primarySpeakerXPercent": 50.0,
            "hasTwoSpeakers": False,
            "speakerLeftPercent": 30.0,
            "speakerRightPercent": 70.0,
            "trajectory": traj
        }

    # Step 3: Spatial Cluster Analysis (Dual-speaker vs Single speaker).
    # Full face records go in so a stream facecam (small, in a corner) is
    # never mistaken for a second speaker — that was doubling the face and
    # the screen in split-screen clips of gameplay streams.
    left_faces = [fc for fd in frame_detections for fc in fd["faces"] if fc["cx"] < 0.44]
    right_faces = [fc for fd in frame_detections for fc in fd["faces"] if fc["cx"] > 0.56]
    center_faces = [fc for fd in frame_detections for fc in fd["faces"] if 0.44 <= fc["cx"] <= 0.56]
    has_two_speakers, avg_left, avg_right = decide_two_speakers(
        left_faces, right_faces, center_faces)
    left_cluster = [f["cx"] for f in left_faces]
    right_cluster = [f["cx"] for f in right_faces]
    center_cluster = [f["cx"] for f in center_faces]

    if has_two_speakers:
        primary_anchor = avg_left if len(left_cluster) >= len(right_cluster) else avg_right
    else:
        primary_anchor = float(np.median(all_face_centers))

    # Step 4: Cinematic Damped Camera Tracking with Deadband & Gaussian Filter
    # 1. Determine raw target X for each frame (plus dominant face width for auto-zoom)
    raw_targets = []
    raw_widths = []
    raw_cys = []
    last_known_x = primary_anchor
    last_known_w = 0.30  # default face-width fraction when no face is visible yet
    last_known_cy = 0.45  # faces usually sit slightly above frame centre

    for fd in frame_detections:
        faces = fd['faces']
        if faces:
            # Pick dominant speaker face weighted by area * confidence
            dominant = max(faces, key=lambda f: f['area'] * (f['conf'] ** 1.5))
            last_known_x = dominant['cx']
            last_known_w = dominant.get('w', last_known_w)
            last_known_cy = dominant.get('cy', last_known_cy)
            raw_targets.append(last_known_x)
            raw_widths.append(last_known_w)
            raw_cys.append(last_known_cy)
        else:
            # If face momentarily hidden, gently hold last known target
            raw_targets.append(last_known_x)
            raw_widths.append(last_known_w)
            raw_cys.append(last_known_cy)

    # 2. Outlier rejection filter (ignore 1-frame spikes)
    cleaned_targets = []
    for i in range(len(raw_targets)):
        window = raw_targets[max(0, i - 1):min(len(raw_targets), i + 2)]
        cleaned_targets.append(float(np.median(window)))

    # 3. Cinematic Exponential Moving Average (EMA) with Gentle Deadband
    # Damping factor alpha = 0.16 gives buttery-smooth, fluid Steadicam motion without lag
    alpha = 0.16
    deadband = 0.035  # 3.5% deadband prevents micro head bobbing from causing camera jitter

    smoothed_camera_x = []
    curr_cam_x = primary_anchor

    for target in cleaned_targets:
        delta = target - curr_cam_x
        if abs(delta) > deadband:
            # Smoothly track target
            effective_target = target - np.sign(delta) * (deadband * 0.5)
            curr_cam_x = curr_cam_x + alpha * (effective_target - curr_cam_x)
        else:
            # Very slow drift to center on the subject
            curr_cam_x = curr_cam_x + 0.02 * delta
        
        # Clamp camera center to avoid black bars in 9:16 vertical crop
        clamped = max(0.20, min(0.80, curr_cam_x))
        smoothed_camera_x.append(clamped)

    # 4. Final 3-tap Gaussian blur pass over camera coordinates to eliminate any residual jerkiness
    kernel = np.array([0.25, 0.5, 0.25])
    padded = np.pad(smoothed_camera_x, (1, 1), mode='edge')
    final_coords = np.convolve(padded, kernel, mode='valid')

    # Same light smoothing for face width (auto-zoom): median filter + EMA
    cleaned_widths = []
    for i in range(len(raw_widths)):
        window = raw_widths[max(0, i - 1):min(len(raw_widths), i + 2)]
        cleaned_widths.append(float(np.median(window)))
    smoothed_widths = []
    curr_w = cleaned_widths[0] if cleaned_widths else 0.30
    for target_w in cleaned_widths:
        curr_w = curr_w + 0.25 * (target_w - curr_w)
        smoothed_widths.append(float(np.clip(curr_w, 0.08, 0.75)))

    # Light smoothing for face height position too.
    smoothed_cys = []
    curr_cy = raw_cys[0] if raw_cys else 0.45
    for target_cy in raw_cys:
        curr_cy = curr_cy + 0.25 * (target_cy - curr_cy)
        smoothed_cys.append(float(np.clip(curr_cy, 0.15, 0.85)))

    # Construct clean trajectory payload
    trajectory = []
    for i, fd in enumerate(frame_detections):
        t = fd['t']
        x_val = float(final_coords[i])
        speaker_label = "left" if x_val < 0.44 else ("right" if x_val > 0.56 else "center")
        trajectory.append({
            "t": round(t, 2),
            "x": round(x_val, 3),
            "xPercent": round(x_val * 100.0, 1),
            "fw": round(smoothed_widths[i], 3),
            "cy": round(smoothed_cys[i], 3),
            "activeSpeaker": speaker_label
        })

    avg_x = float(np.mean([pt['x'] for pt in trajectory]))
    avg_fw = float(np.mean([pt['fw'] for pt in trajectory]))

    return {
        "duration": duration,
        "sampleCount": len(trajectory),
        "avgX": round(avg_x, 3),
        "avgXPercent": round(avg_x * 100.0, 1),
        "avgFw": round(avg_fw, 3),
        "primarySpeakerXPercent": round(primary_anchor * 100.0, 1),
        "hasTwoSpeakers": bool(has_two_speakers),
        "speakerLeftPercent": round(avg_left * 100.0, 1),
        "speakerRightPercent": round(avg_right * 100.0, 1),
        "trajectory": trajectory
    }

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 tracker_local.py <video_path> <start_time> <duration> [out_json]")
        sys.exit(1)

    video = sys.argv[1]
    start = float(sys.argv[2])
    dur = float(sys.argv[3])
    out_json = sys.argv[4] if len(sys.argv) > 4 else None

    result = track_subject(video, start, dur)
    
    if out_json:
        with open(out_json, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Tracking data saved to {out_json}")
    else:
        print(json.dumps(result))
