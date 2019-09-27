python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. object_detection.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. image_reco.proto
