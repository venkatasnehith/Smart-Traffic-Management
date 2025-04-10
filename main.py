from ultralytics import YOLO

# Load a model
model = YOLO("best-10.pt")  # pretrained YOLO model

# Get and print the classes
print("Classes in the model:")
print(model.names)  # This will show all class names in the model