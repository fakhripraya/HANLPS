from proto.messaging import messaging_pb2_grpc, messaging_pb2 as messaging

class MessagingServicer(messaging_pb2_grpc.MessagingServicer):
    def TextMessaging(self, request, context):
        result = "Received: " + request.content
        return messaging.MessageResponse(result=result)