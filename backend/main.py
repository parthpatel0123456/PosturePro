import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import cv2
import numpy as np
import math
import requests

# Lite Model
lite_model = 'pose_landmarker_lite.task'

# Regular Model
regular_model = 'pose_landmarker_full.task'

# Heavy Model
heavy_model = 'pose_landmarker_heavy.task'

model_path = regular_model

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = vision.PoseLandmarker
PoseLandmarkerResult = vision.PoseLandmarkerResult
VisionRunningMode = vision.RunningMode

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
POSE_CONNECTIONS = mp.solutions.pose.POSE_CONNECTIONS

latest_result = None

def print_result(result, output_image, timesamp_ms):
    global latest_result
    latest_result = result

def detector(nose, left_eye, right_eye, left_shoulder, right_shoulder):
    # Head Tilt
    dx_eyes = right_eye.x - left_eye.x
    dy_eyes = right_eye.y - left_eye.y
    head_tilt_angle = abs(math.degrees(math.atan2(dy_eyes, dx_eyes)))

    # Forward Slouch
    z_eyes = (left_eye.z + right_eye.z) / 2
    z_shoulders = (left_shoulder.z + right_shoulder.z) / 2
    dz_leaning_forward = abs(z_shoulders - z_eyes)
    upright_dz_reference = 0.15

    # Shoulder Tilt
    dy_shoulders = abs(left_shoulder.y - right_shoulder.y)

    # Bad Tolerances
    tilt_bad = abs(head_tilt_angle - 180) > 25
    shoulder_imbalance_bad = dy_shoulders > 0.03
    head_slouch_bad = dz_leaning_forward > 0.10

    weights = {
        "head_tilt": 0.3,
        "forward_slouch": 0.4,
        "shoulder_tilt": 0.3
    }

    tilt_score = max(0, 1 - min(abs(head_tilt_angle - 180) / 30, 1))
    forward_score = min(max(0, 1 - (dz_leaning_forward - upright_dz_reference) / upright_dz_reference), 1)
    shoulder_imbalance_score = max(0, 1 - min(dy_shoulders / 0.05, 1))

    score = (
        tilt_score * weights["head_tilt"] +
        forward_score * weights["forward_slouch"] + 
        shoulder_imbalance_score * weights["shoulder_tilt"]
    ) * 100

    posture_state = "Good"
    if score < 85 and score >= 70:
        posture_state = "Moderate"
    elif score < 70:
        posture_state = "Poor"

    data = {
        "score": round(score, 0),
        "tilt_score": round(tilt_score, 1),
        "forward_slouch_score": round(forward_score, 1),
        "shoulder_tilt": round(shoulder_imbalance_score, 1)
    }

    response = requests.post("http://127.0.0.1:8000/score", json=data)

    return data

options = vision.PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path), 
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result
)

cap = cv2.VideoCapture(0)

with PoseLandmarker.create_from_options(options) as landmarker:
    timestamp = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

        landmarker.detect_async(mp_image, timestamp)
        timestamp += 33

        annotated_image = frame.copy()
        if latest_result and latest_result.pose_landmarks:
            pose_landmarks = landmark_pb2.NormalizedLandmarkList()
            for lm in latest_result.pose_landmarks[0]:
                pose_landmarks.landmark.add(
                    x=lm.x, y=lm.y, z=lm.z,
                    visibility=lm.visibility, presence=lm.presence
                )

            mp_drawing.draw_landmarks(
                annotated_image,
                pose_landmarks,
                POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
            )
            
            nose = latest_result.pose_landmarks[0][0]
            left_eye = latest_result.pose_landmarks[0][7]
            right_eye = latest_result.pose_landmarks[0][8]
            left_shoulder = latest_result.pose_landmarks[0][11]
            right_shoulder = latest_result.pose_landmarks[0][12]

            result = detector(nose, left_eye, right_eye, left_shoulder, right_shoulder)

            cv2.putText(annotated_image, f"Score: {result['score']}", (30,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            cv2.putText(annotated_image, f"tilt_score: {result['tilt_score']}", (30,150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            cv2.putText(annotated_image, f"forward_slouch_score: {result['forward_slouch_score']}", (30,200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            cv2.putText(annotated_image, f"shoulder_tilt: {result['shoulder_tilt']}", (30,250), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

            cv2.imshow("AI Posture Detector", annotated_image)
        
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()