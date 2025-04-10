from flask import Flask, render_template
import threading
from dashboard import monitor_traffic, traffic_data, violation_data, frame_queue
import cv2
import numpy as np
from datetime import datetime
import json
import os

app = Flask(__name__)

# Global variables for data storage
latest_data = {
    'traffic_status': 'Unknown',
    'vehicle_count': 0,
    'violations': [],
    'last_update': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

def update_data():
    global latest_data
    while True:
        try:
            # Get latest traffic data
            traffic = traffic_data.get_nowait()
            latest_data['traffic_status'] = traffic['traffic_status']
            latest_data['vehicle_count'] = traffic['vehicle_count']
            
            # Get latest violations
            violations = []
            while not violation_data.empty():
                violations.append(violation_data.get_nowait())
            latest_data['violations'] = violations
            
            # Update timestamp
            latest_data['last_update'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        except Exception as e:
            print(f"Error updating data: {e}")
        
        # Sleep for a short time to prevent overwhelming the system
        threading.Event().wait(1)

@app.route('/')
def index():
    return render_template('index.html', data=latest_data)

@app.route('/api/data')
def get_data():
    return json.dumps(latest_data)

@app.route('/api/frame')
def get_frame():
    try:
        frame = frame_queue.get_nowait()
        _, buffer = cv2.imencode('.jpg', frame)
        return buffer.tobytes()
    except:
        return None

if __name__ == '__main__':
    # Start traffic monitoring in a separate thread
    traffic_thread = threading.Thread(target=monitor_traffic, daemon=True)
    traffic_thread.start()
    
    # Start data update thread
    update_thread = threading.Thread(target=update_data, daemon=True)
    update_thread.start()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True) 