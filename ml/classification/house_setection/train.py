from ultralytics import YOLO
from roboflow import Roboflow
import os

rf = Roboflow(api_key="ADD_HERE_YOUR_API_IF_U_WILL_TEST_THIS")
project = rf.workspace("new-workspace-cufik").project("train_google")
version = project.version(3)
dataset = version.download("yolov8")

data_yaml = os.path.join(dataset.location, 'data.yaml')

print(f"data.yaml location: {data_yaml}")

model = YOLO('yolov8s.pt')

model.train(
    data=data_yaml,
    epochs=50,
    imgsz=640,
    batch=16,
    workers=4,
    optimizer='SGD',
    lr0=0.01,
    momentum=0.9,
    weight_decay=0.0005
)

model.save('best_model.pt')
