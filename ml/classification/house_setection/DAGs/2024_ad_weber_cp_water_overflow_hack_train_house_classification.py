from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime
import os

S3_ACCESS_KEY = Variable.get("S3_ACCESS_KEY")
S3_SECRET_KEY = Variable.get("S3_SECRET_KEY")
S3_ENDPOINT = Variable.get("S3_ENDPOINT")
ROBOFLOW_API = Variable.get("ROBOFLOW_API")

def install_packages():
    import subprocess
    subprocess.check_call(["pip", "install", "ultralytics", "roboflow"])

def train_model():
    from ultralytics import YOLO
    from roboflow import Roboflow


    rf = Roboflow(api_key=ROBOFLOW_API)
    project = rf.workspace("new-workspace-cufik").project("train_google")
    version = project.version(3)
    dataset = version.download("yolov8")


    data_yaml = os.path.join(dataset.location, 'data.yaml')


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

    model_path = 'best_model.pt'
    model.save(model_path)
    upload_to_s3(model_path)

def upload_to_s3(filename):
    import boto3
    s3_client = boto3.client(
        's3',
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        endpoint_url=S3_ENDPOINT
    )
    bucket_name = "hack_cp_2024_10_25"
    s3_client.upload_file(filename, bucket_name, filename)

with DAG(
    dag_id="2024_ad_weber_cp_water_overflow_hack_train_house_classification",
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    install_task = PythonOperator(
        task_id="install_packages",
        python_callable=install_packages
    )

    train_task = PythonOperator(
        task_id="train_model",
        python_callable=train_model
    )

    install_task >> train_task
