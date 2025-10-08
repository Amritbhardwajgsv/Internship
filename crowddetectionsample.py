import tensorflow as tf
import tensorflow_hub as hub
import cv2
import numpy as np

def count_people_tfhub(video_path):
    # Load FasterRCNN model from TF Hub
    model = hub.load("https://tfhub.dev/tensorflow/faster_rcnn/inception_resnet_v2_640x640/1")
    
    cap = cv2.VideoCapture(video_path)
    total_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Convert frame to tensor
        input_tensor = tf.convert_to_tensor(frame)
        input_tensor = input_tensor[tf.newaxis, ...]
        
        # Run detection
        results = model(input_tensor)
        
        # Get detection results
        boxes = results["detection_boxes"].numpy()[0]
        scores = results["detection_scores"].numpy()[0]
        classes = results["detection_classes"].numpy()[0]
        
        current_count = 0
        for i in range(len(scores)):
            if scores[i] > 0.5 and classes[i] == 1:  # Class 1 is person
                current_count += 1
        
        if current_count > total_count:
            total_count = current_count
            
    cap.release()
    return total_count