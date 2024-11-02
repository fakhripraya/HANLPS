# HANLPS

HANLPS or Highly Accurate Natural Language Processing Service
is an AI focus location retrieval backend service mainly to fetch location based on the input
this service used GRPC Protocol to communicate

## Installation

### Create the virtual environment:

```
python -m venv venv

```

### Run the virtual environment:

#### Windows

```
venv\Scripts\activate

```

#### Linux/MacOS

```
source venv/bin/activate
```

### Install the required Python packages:

```
pip install -r requirements.txt
pre-commit install
```

### Run the App

```
python main.py
```

### To install dependency

```
pip install <package>
pip freeze > requirements.txt

these can install the package aswell as immediately write it in the requirement.txt file
```

### To generate proto files

```
python -m grpc_tools.protoc -I=proto --python_out=proto --grpc_python_out=proto your/proto/path/your_new_service.proto
```

### How to

There are several ways to use HANLPS
The easiest way to use the service is to install GUI API Platform such as Postman, Insomnia, and you name it

If you want to use CLI, you could use app like grpcurl, evans, ghz, BloomRPC, and you name it.
Personally i would go with grpcurl as it is the app that i always use

Basic grpcurl command
```
grpcurl -plaintext \
  -import-path /path/to/protofiles \
  -proto service.proto \
  -d '{"example": "json"}' \
  localhost:50051 Service/Message
```

Example for this project
```
grpcurl -plaintext -import-path ./protofile/messaging/proto/ -proto messaging.proto -d '{"sessionId": "abc123", "content": "cariin kost di daerah tebet dong"}' localhost:51051 MessagingService/textMessaging
```

### Dependencies

grpcio grpcio-tools python-dotenv openai langchain langchain-community weaviate-client
langchain-weaviate langchain-huggingface langchain-google-genai cerberus unstructured pytest tiktoken

### Optionals

grpcurl
