import grpc
import sys
sys.path.append("./proto/messaging")
from proto.messaging import messaging_pb2_grpc, messaging_pb2 as messaging

def run(chat_content):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = messaging_pb2_grpc.MessagingStub(channel)
        response = stub.textMessaging(messaging.MessageRequest(content=chat_content))
    print(f"Result: {response.result}")

if __name__ == '__main__':
    # Get user Input 
    chat_content = input("Please input the chat: ")
    run(chat_content)