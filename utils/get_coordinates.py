"""Helper script to find ROI coordinates.

Run this script to open your camera.
1. Press 'SPACE' to freeze the current frame.
2. Click on the image to print pixel (x, y) coordinates to the console.
3. Press 'c' to unfreeze/continue.
4. Press 'q' to quit.

Copy the printed coordinates into your config/default.yaml.
"""

import cv2
import yaml

# Load default config to get source
with open("config/default.yaml", "r") as f:
    cfg = yaml.safe_load(f)

source = cfg.get("source", 0)
# Handle "0" string
if isinstance(source, str) and source.isdigit():
    source = int(source)

cap = cv2.VideoCapture(source)
if not cap.isOpened():
    print(f"Cannot open source: {source}")
    exit(1)

print(f"Source opened: {source}")
print("Controls:")
print("  SPACE : Freeze frame")
print("  Click : Print (x, y) coordinates (when frozen)")
print("  'c'   : Continue / Unfreeze")
print("  'q'   : Quit")

frozen_frame = None

def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Coordinate: [{x}, {y}]")
        # Visual feedback
        if frozen_frame is not None:
            cv2.circle(frozen_frame, (x, y), 5, (0, 0, 255), -1)
            cv2.putText(frozen_frame, f"[{x},{y}]", (x+10, y), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.imshow("ROI Selector", frozen_frame)

cv2.namedWindow("ROI Selector")
cv2.setMouseCallback("ROI Selector", mouse_callback)

while True:
    if frozen_frame is None:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        display_frame = frame
    else:
        display_frame = frozen_frame

    cv2.imshow("ROI Selector", display_frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord(' '):  # Space
        if frozen_frame is None:
            frozen_frame = display_frame.copy()
            print("Frame frozen. Click to get coordinates.")
        else:
            frozen_frame = None
            print("Unfrozen.")
    elif key == ord('c'):
        frozen_frame = None
        print("Unfrozen.")

cap.release()
cv2.destroyAllWindows()
