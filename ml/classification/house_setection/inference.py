import grpc
from concurrent import futures
import os
from ultralytics import YOLO
from PIL import Image
from grpc_tools import protoc

proto_content = """
syntax = "proto3";

package yoloservice;

service YoloService {
  rpc Predict (PredictRequest) returns (PredictResponse) {}
}

message PredictRequest {
  string image_path = 1;
}

message PredictResponse {
  repeated Detection detections = 1;
}

message Detection {
  string label = 1;
  float confidence = 2;
  float x = 3;
  float y = 4;
  float width = 5;
  float height = 6;
}
"""

with open("yolo_service.proto", "w") as f:
    f.write(proto_content)

protoc.main((
    '',
    '-I.',
    '--python_out=.',
    '--grpc_python_out=.',
    'yolo_service.proto',
))

import yolo_service_pb2
import yolo_service_pb2_grpc


class YoloServiceServicer(yolo_service_pb2_grpc.YoloServiceServicer):
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def Predict(self, request, context):
        image = Image.open(request.image_path)
        results = self.model(image)
        response = yolo_service_pb2.PredictResponse()
        for result in results:
            for box in result.boxes:
                detection = response.detections.add()
                detection.label = box.cls
                detection.confidence = box.conf
                detection.x = box.xyxy[0].item()
                detection.y = box.xyxy[1].item()
                detection.width = box.xywh[2].item()
                detection.height = box.xywh[3].item()
        return response


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    yolo_service_pb2_grpc.add_YoloServiceServicer_to_server(YoloServiceServicer('best_model.pt'), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC сервер запущен на порту 50051.")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
