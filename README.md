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

### Dependencies

grpcio grpcio-tools python-dotenv openai langchain langchain-community weaviate-client
langchain-weaviate langchain-huggingface langchain-google-genai cerberus unstructured pytest tiktoken

### Features / Fix to be added

- Chat context hallucination
  - An ability to understand the context of the chat well
- Multi or singular object referencing
  - An ability to refer to the fetched objects from the DB
  - Implement RAG usability on referencing
