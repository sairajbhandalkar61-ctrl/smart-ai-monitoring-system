import cv2
import numpy as np
import base64

# Multi-cascade classifiers for accurate crowd monitoring
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)
profile_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_profileface.xml'
)
upperbody_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_upperbody.xml'
)

def detect_people(frame, return_boxes=False):
    """
    Detect people/faces in an OpenCV BGR frame using multi-scale cascade fusion and NMS.
    Returns:
        (frame, count) if return_boxes is False (for backward compatibility with app.py)
        (frame, count, boxes) if return_boxes is True (for server.py & web API)
    """
    if frame is None or frame.size == 0:
        if return_boxes:
            return frame, 0, []
        return frame, 0

    h_img, w_img = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    candidate_boxes = []
    scores = []

    # 1. Frontal faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.12, minNeighbors=3, minSize=(25, 25))
    for (x, y, w, h) in faces:
        candidate_boxes.append([int(x), int(y), int(w), int(h)])
        scores.append(0.95)

    # 2. Profile faces (people walking sideways)
    profiles = profile_cascade.detectMultiScale(gray, scaleFactor=1.12, minNeighbors=3, minSize=(25, 25))
    for (x, y, w, h) in profiles:
        candidate_boxes.append([int(x), int(y), int(w), int(h)])
        scores.append(0.90)

    # 3. Upper body (people seen from behind/distance in crowds)
    bodies = upperbody_cascade.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=2, minSize=(40, 40))
    for (x, y, w, h) in bodies:
        candidate_boxes.append([int(x), int(y), int(w), int(h)])
        scores.append(0.85)

    final_boxes = []
    if len(candidate_boxes) > 0:
        indices = cv2.dnn.NMSBoxes(candidate_boxes, scores, 0.5, 0.4)
        if len(indices) > 0:
            for idx in indices.flatten():
                final_boxes.append(candidate_boxes[idx])

    count = len(final_boxes)
    boxes_meta = []

    # Draw emerald surveillance boxes
    for idx, (x, y, w, h) in enumerate(final_boxes):
        cv2.rectangle(frame, (x, y), (x + w, y + h), (59, 214, 116), 2)
        label = f"Person #{idx + 1}"
        cv2.putText(
            frame,
            label,
            (x, max(18, y - 6)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (59, 214, 116),
            2
        )
        boxes_meta.append({
            "id": idx + 1,
            "x": int(x),
            "y": int(y),
            "w": int(w),
            "h": int(h)
        })

    if return_boxes:
        return frame, count, boxes_meta
    return frame, count

def process_base64_frame(b64_string: str):
    """Processes base64 encoded frame from client browser, detects crowd, and returns boxes & count."""
    try:
        if not b64_string:
            return 0, [], None
        if "," in b64_string:
            b64_string = b64_string.split(",")[1]
        img_data = base64.b64decode(b64_string)
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            return 0, [], None

        frame, count, boxes = detect_people(frame, return_boxes=True)
        _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        annotated_b64 = "data:image/jpeg;base64," + base64.b64encode(buffer).decode("utf-8")
        return count, boxes, annotated_b64
    except Exception as e:
        print(f"Error processing frame: {e}")
        return 0, [], None
