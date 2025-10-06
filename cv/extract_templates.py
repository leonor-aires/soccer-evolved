# cv/extract_templates.py
import os, glob, numpy as np, cv2, mediapipe as mp

mp_pose = mp.solutions.pose
L_HIP, R_HIP, L_SH, R_SH = 23, 24, 11, 12

def extract_sequence(video_path: str, sample_fps: int = 15) -> np.ndarray:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open {video_path}")
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30
    step = max(int(round(src_fps / sample_fps)), 1)

    seq = []
    with mp_pose.Pose(model_complexity=1, min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        frame_idx = 0
        while True:
            ok, frame = cap.read()
            if not ok: break
            if frame_idx % step != 0:
                frame_idx += 1
                continue
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = pose.process(rgb)
            if res.pose_landmarks:
                lm = res.pose_landmarks.landmark
                pts = np.array([[p.x, p.y, p.visibility] for p in lm], dtype=np.float32)  # (33,3)
                seq.append(pts)
            frame_idx += 1
    cap.release()
    if not seq: return np.zeros((0,33,3), dtype=np.float32)
    return np.stack(seq, axis=0)

def normalize_xy(seq33x3: np.ndarray) -> np.ndarray:
    if seq33x3.size == 0: return seq33x3
    xy = seq33x3[...,:2].copy()
    hip_mid = (xy[:, L_HIP, :] + xy[:, R_HIP, :]) / 2.0
    xy = xy - hip_mid[:, None, :]
    shoulder_w = np.linalg.norm(xy[:, L_SH, :] - xy[:, R_SH, :], axis=1)
    scale = np.where(shoulder_w > 1e-6, shoulder_w, 1.0)
    xy = (xy / scale[:, None, None]).astype(np.float32)
    return xy

def process_folder(in_dir: str, out_npz: str):
    arrays = []
    for path in sorted(glob.glob(os.path.join(in_dir, "*"))):
        try:
            raw = extract_sequence(path)
            norm = normalize_xy(raw)
            if norm.shape[0] > 0:
                arrays.append(norm)
                print(f"OK: {os.path.basename(path)} -> {norm.shape}")
            else:
                print(f"NO POSE: {os.path.basename(path)}")
        except Exception as e:
            print(f"ERR {os.path.basename(path)}: {e}")
    if arrays:
        np.savez_compressed(out_npz, *arrays)
        print(f"Saved {len(arrays)} templates -> {out_npz}")
    else:
        print("No templates extracted.")

if __name__ == "__main__":
    os.makedirs("templates", exist_ok=True)
    process_folder("videos/remates", "templates/remates.npz")
    process_folder("videos/passes", "templates/passes.npz")
