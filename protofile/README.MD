# Possible Error After Compiling Proto

- ModuleNotFoundError: No module named 'messaging_pb2'
    + Just change the generated import "import messaging_pb2 as messaging__pb2 " in messaging_pb2_grpc.py to be from . import messaging_pb2 as messaging__pb2 