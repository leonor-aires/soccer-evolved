# cv/pose_preview.py
import os, sys, glob
import cv2
import mediapipe as mp

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles

def preview_video(input_path: str, output_path: str, sample_every: int = 1):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {input_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    w   = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h   = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Video writer (mp4)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    with mp_pose.Pose(model_complexity=1, enable_segmentation=False,
                      min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        frame_idx = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if frame_idx % sample_every != 0:
                frame_idx += 1
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = pose.process(rgb)

            if res.pose_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    res.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_styles.get_default_pose_landmarks_style()
                )

            out.write(frame)
            frame_idx += 1

    cap.release()
    out.release()
    print(f"Saved overlay preview -> {output_path}")

def batch_preview(folder_in: str, folder_out: str):
    os.makedirs(folder_out, exist_ok=True)
    for path in sorted(glob.glob(os.path.join(folder_in, "*.*"))):
        name = os.path.splitext(os.path.basename(path))[0]
        out = os.path.join(folder_out, f"{name}_overlay.mp4")
        preview_video(path, out)

if __name__ == "__main__":
    # Example usage:
    # python cv/pose_preview.py data/videos/shooting data/previews/shooting
    in_dir = sys.argv[1] if len(sys.argv) > 1 else "data/videos/shooting"
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "data/previews/shooting"
    batch_preview(in_dir, out_dir)
