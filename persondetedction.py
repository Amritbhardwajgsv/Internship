import torch
import cv2
import csv
from datetime import datetime
import pyautogui
import time

# Load YOLOv5s model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', force_reload=False)
model.classes = [0]  # Only detect persons
model.conf = 0.25

# Load video (replace with your station footage path or use webcam with 0)
video_path = r"C:\Users\bhard\Downloads\videoplayback (1).webm"
cap = cv2.VideoCapture(video_path)

csv_file = open('inflow_data.csv', mode='w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Timestamp', 'Person_Count'])

screen_width, screen_height = pyautogui.size()
window_name = 'YOLOv5 Person Detection'
frame_skip = 10
frame_count = 0
total_persons = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    if frame_count % frame_skip != 0:
        cv2.imshow(window_name, frame)
        if frame_count == 1:
            win_x = (screen_width - frame.shape[1]) // 2
            win_y = (screen_height - frame.shape[0]) // 2
            cv2.moveWindow(window_name, win_x, win_y)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue

    frame = cv2.resize(frame, (640, 360))

    # Inference
    results = model(frame)

    # Extract predictions
    detections = results.pandas().xyxy[0]
    person_detections = detections[detections['name'] == 'person']
    person_count = len(person_detections)
    total_persons += person_count

    # Draw green circles around detected persons
    for _, row in person_detections.iterrows():
        # Get bounding box coordinates
        x1, y1, x2, y2 = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
        # Calculate center and radius
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        radius = int(0.5 * max(x2 - x1, y2 - y1))
        # Draw green circle
        cv2.circle(frame, (center_x, center_y), radius, (0, 255, 0), 2)

    timestamp = datetime.now().strftime("%H:%M:%S")
    csv_writer.writerow([timestamp, person_count])
    print(f"{timestamp}: {person_count} persons")

    # Display count on frame
    cv2.putText(frame, f'Person Count: {person_count}', (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow(window_name, frame)
    if frame_count == 1:
        win_x = (screen_width - frame.shape[1]) // 2
        win_y = (screen_height - frame.shape[0]) // 2
        cv2.moveWindow(window_name, win_x, win_y)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(0.05)  # <-- Add this line to slow down the video

# Cleanup
cap.release()
cv2.destroyAllWindows()
csv_file.close()

print(f"Total persons detected (sum across frames): {total_persons}")
