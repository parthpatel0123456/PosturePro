import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import cv2
import numpy as np
import math

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
    dx_eyes = right_eye.x - left_eye.x
    dy_eyes = right_eye.y - left_eye.y
    head_tilt_angle = math.degrees(math.atan2(dy_eyes, dx_eyes))
    head_tilt_angle = abs(head_tilt_angle)

    shoulder_center_x = (left_shoulder.x + right_shoulder.x) / 2
    shoulder_center_z = (left_shoulder.z + right_shoulder.z) / 2
    dx_forward = abs(nose.x - shoulder_center_x)
    dz_forward = nose.z - shoulder_center_z 

    dy_shoulders = abs(left_shoulder.y - right_shoulder.y)

    tilt_bad = head_tilt_angle > 10
    forward_bad = dx_forward > 0.08
    imbalance_bad = dy_shoulders > 0.03

    score = 100
    if tilt_bad:
        score -= 20
    if forward_bad:
        score -= 40
    if imbalance_bad:
        score -= 30

    posture_state = ""
    if score >= 85:
        posture_state = "Good"
    elif score < 85 and score > 70:
        posture_state = "Moderate"
    elif score < 70:
        posture_state = "Poor"

    return {
        "head_tilt_angle": round(head_tilt_angle, 2),
        "forward_head_dx": round(dx_forward, 3),
        "forward_head_dz": round(dz_forward, 3),
        "shoulder_imbalance": round(dy_shoulders, 3),
        "score": score,
        "posture_state": posture_state
    }
    

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

            cv2.putText(annotated_image, f"Posture: {result['posture_state']}", (30,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

            cv2.imshow("AI Posture Detector", annotated_image)
        
        if cv2.waitKey(1) & 0xFF == 27:
            break


cap.release()
cv2.destroyAllWindows()