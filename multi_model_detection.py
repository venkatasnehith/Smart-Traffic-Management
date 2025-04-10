import cv2
import torch
import telebot
from ultralytics import YOLO
from telebot import types
import threading
import numpy as np

# Load all YOLO models
model1 = YOLO("C:/Users/Shreeja/PycharmProjects/PythonProject/helmetttttt.pt")  # Helmet detection model
model2 = YOLO("/traffic_management.pt")  # Traffic management model
model3 = YOLO("C:/Users/Shreeja/PycharmProjects/PythonProject/best-10.pt")  # Your existing model

# Use appropriate device
device = "cuda" if torch.cuda.is_available() else "cpu"
model1.to(device)
model2.to(device)
model3.to(device)

# Print the active device
print(f"Using device: {device}")

# Telegram bot setup
BOT_TOKEN = '7668963778:AAEE_D5alny6aGm_pOldeg9Om0cfTGPpJoU'
GROUP_CHAT_ID = -4679346023
bot = telebot.TeleBot(BOT_TOKEN)

def start_bot():
    try:
        @bot.message_handler(commands=['start'])
        def start_message(message):
            bot.reply_to(message, "You have subscribed to multi-model detection alerts!")

        bot.polling(none_stop=True)
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Telegram API Error: {e}")

# Run bot in a separate thread
threading.Thread(target=start_bot, daemon=True).start()

# Open camera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# Wait for camera to warm up
for i in range(10):
    ret, frame = cap.read()
    if ret:
        print("Camera initialized successfully!")
        break
    cv2.waitKey(100)

if not ret:
    print("Error: Failed to capture image.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Lost connection to camera.")
        break

    # Run inference with all models
    results1 = model1(frame)
    results2 = model2(frame)
    results3 = model3(frame)

    # Combine detections from all models
    annotated_frame = frame.copy()
    detected_classes = set()

    # Process results from each model
    for result in results1:
        for box in result.boxes:
            cls_id = int(box.cls[0])
            class_name = model1.names[cls_id]
            detected_classes.add(f"Helmet Model: {class_name}")
            # Draw box
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(annotated_frame, class_name, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    for result in results2:
        for box in result.boxes:
            cls_id = int(box.cls[0])
            class_name = model2.names[cls_id]
            detected_classes.add(f"Traffic Model: {class_name}")
            # Draw box
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(annotated_frame, class_name, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    for result in results3:
        for box in result.boxes:
            cls_id = int(box.cls[0])
            class_name = model3.names[cls_id]
            detected_classes.add(f"Model3: {class_name}")
            # Draw box
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(annotated_frame, class_name, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # If objects are detected, send a message to the group
    if detected_classes:
        alert_message = f"Detected: {', '.join(detected_classes)} at Hyderabad signal 4 area: Kothapet"
        print(alert_message)
        try:
            bot.send_message(GROUP_CHAT_ID, alert_message)
        except telebot.apihelper.ApiTelegramException as e:
            print(f"Failed to send message: {e}")

    # Display the frame
    cv2.imshow("Multi-Model Detection Feed", annotated_frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows() 