import cv2
import torch
import telebot
from ultralytics import YOLO
from telebot import types
import threading
import numpy as np
from datetime import datetime

# Load all YOLO models
model1 = YOLO("C:/Users/Shreeja/PycharmProjects/PythonProject/helmetttttt.pt")  # Helmet detection model
model2 = YOLO("C:/Users/Shreeja/PycharmProjects/PythonProject/traffic_management.pt")  # Traffic management model
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

# Traffic rerouting configurations
TRAFFIC_THRESHOLD = 10  # Number of vehicles to consider heavy traffic
ROUTES_INFO = {
    "kothapet_to_nagole": {
        "destination": "Nagole",
        "routes": [
            {
                "name": "Regular Route (Heavy Traffic)",
                "path": "Kothapet → LB Nagar → Nagole",
                "distance": "8.5 km",
                "normal_time": "20 mins",
                "traffic_time": "45 mins",
                "traffic_status": "Heavy",
                "map_link": "https://maps.app.goo.gl/regular_route"
            },
            {
                "name": "Recommended Route 1",
                "path": "Kothapet → Mohan Nagar → Nagole",
                "distance": "7.2 km",
                "normal_time": "25 mins",
                "traffic_time": "25 mins",
                "traffic_status": "Light",
                "map_link": "https://maps.app.goo.gl/dXKQGHBGqHBWYeYS6"
            },
            {
                "name": "Alternative Route 2",
                "path": "Kothapet → Dilsukhnagar → Chaitanyapuri → Nagole",
                "distance": "9.1 km",
                "normal_time": "30 mins",
                "traffic_time": "35 mins",
                "traffic_status": "Moderate",
                "map_link": "https://maps.app.goo.gl/alternative2"
            },
            {
                "name": "Alternative Route 3",
                "path": "Kothapet → Hayathnagar → Nagole",
                "distance": "10.5 km",
                "normal_time": "35 mins",
                "traffic_time": "35 mins",
                "traffic_status": "Light",
                "map_link": "https://maps.app.goo.gl/alternative3"
            }
        ]
    }
}

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
cap = cv2.VideoCapture(1)

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

# Function to format violation message
def format_violation_message(detected_classes):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    violation_count = sum(1 for cls in detected_classes if "no-helmet" in cls.lower() or "helmet_violation" in cls.lower())
    
    if violation_count > 0:
        route_info = ROUTES_INFO["kothapet_to_nagole"]
        light_traffic_routes = [route for route in route_info["routes"] if route['traffic_status'] == "Light"]
        best_route = light_traffic_routes[0] if light_traffic_routes else route_info["routes"][1]

        base_message = f"""🚨 TRAFFIC VIOLATION & ROUTE ADVISORY 🚨
Location: Hyderabad signal 4 area, Kothapet
Time: {current_time}

⚠️ VIOLATIONS DETECTED:"""
        
        for cls in detected_classes:
            if "no-helmet" in cls.lower() or "helmet_violation" in cls.lower():
                base_message += f"\n• {cls}"
        
        challan_message = f"""
📝 E-CHALLAN DETAILS:
- Fine Amount: ₹2000 per violation
- Total Amount: ₹{2000 * violation_count}
- Please pay within 7 days to avoid additional penalties

🚦 TRAFFIC-FREE ROUTE AVAILABLE:
• Recommended Route: {best_route['path']}
• Distance: {best_route['distance']}
• Travel Time: {best_route['normal_time']}
• Traffic Status: 🟢 Clear Route

🗺️ Get Navigation for Safe Route:
{best_route['map_link']}

💡 Pro Tip: Take {best_route['path'].split('→')[-2].strip()} route to avoid traffic and reach safely!"""
        
        return base_message + challan_message
    return None

# Function to check traffic density and generate rerouting message
def check_traffic_and_reroute(detected_classes):
    vehicle_count = sum(1 for cls in detected_classes if any(vehicle in cls.lower() for vehicle in ["car", "bike", "bus", "truck", "motorcycle"]))
    
    if vehicle_count >= TRAFFIC_THRESHOLD:
        route_info = ROUTES_INFO["kothapet_to_nagole"]
        routes = route_info["routes"]
        
        # Find traffic-free routes
        light_traffic_routes = [route for route in routes if route['traffic_status'] == "Light"]
        
        traffic_message = f"""
🚦 TRAFFIC ALERT & SAFE ROUTE ADVISORY 🚦
Location: Kothapet Signal
Time: {datetime.now().strftime("%H:%M")}

⚠️ Current Traffic Status:
• Heavy Traffic at LB Nagar
• Vehicles Detected: {vehicle_count}

✅ RECOMMENDED TRAFFIC-FREE ROUTES:"""

        # Add traffic-free routes
        for idx, route in enumerate(light_traffic_routes, 1):
            traffic_message += f"""

{idx}. {route['name']}
• Route: {route['path']}
• Distance: {route['distance']}
• Travel Time: {route['normal_time']}
• Status: 🟢 NO TRAFFIC
• Get Directions: {route['map_link']}"""

        traffic_message += f"""

❌ ROUTES TO AVOID:
• {routes[0]['path']}
• Current Delay: {routes[0]['traffic_time']} (Usually {routes[0]['normal_time']})
• Status: 🔴 Heavy Traffic

💡 BEST OPTION:
→ Take: {light_traffic_routes[0]['path']}
→ Save up to {int(int(routes[0]['traffic_time'].split()[0]) - int(light_traffic_routes[0]['normal_time'].split()[0]))} minutes
→ Avoid traffic congestion

🗺️ Get Instant Navigation to Traffic-Free Route:
{light_traffic_routes[0]['map_link']}

Drive Safe! 🚗"""
        return traffic_message
    return None

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
            # Add challan text for violations
            if "no-helmet" in class_name.lower():
                cv2.putText(annotated_frame, "CHALLAN: Rs.2000", (x1, y2+20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    for result in results2:
        for box in result.boxes:
            cls_id = int(box.cls[0])
            class_name = model2.names[cls_id]
            detected_classes.add(f"Traffic Model: {class_name}")
            # Draw box
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(annotated_frame, class_name, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            # Add challan text for violations
            if "helmet_violation" in class_name.lower():
                cv2.putText(annotated_frame, "CHALLAN: Rs.2000", (x1, y2+20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    for result in results3:
        for box in result.boxes:
            cls_id = int(box.cls[0])
            class_name = model3.names[cls_id]
            detected_classes.add(f"Model3: {class_name}")
            # Draw box
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(annotated_frame, class_name, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Send messages to the group
    if detected_classes:
        # Check for violations and send combined message
        violation_message = format_violation_message(detected_classes)
        if violation_message:
            try:
                bot.send_message(GROUP_CHAT_ID, violation_message)
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Failed to send violation message: {e}")
        
        # Check for traffic and send traffic alert
        traffic_alert = check_traffic_and_reroute(detected_classes)
        if traffic_alert:
            try:
                bot.send_message(GROUP_CHAT_ID, traffic_alert)
            except telebot.apihelper.ApiTelegramException as e:
                print(f"Failed to send traffic alert: {e}")

    # Display the frame
    cv2.imshow("Multi-Model Detection Feed", annotated_frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()