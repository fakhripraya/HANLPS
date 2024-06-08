# HANLPS (Highly Accurate Natural Language Processing Service)
# Instalation

## Create the virtual environment:
```
python -m venv venv

```

## Run the virtual environment:
### Windows
```
venv\Scripts\activate

```
### Linux/MacOS
```
source venv/bin/activate
```

## Install the required Python packages:
```
pip install -r requirements.txt
pre-commit install
```

# Run the App
```
python main.py
```

# To install dependency

```
pip install <package>
pip freeze > requirements.txt

these can install the package aswell as immediately write it in the requirement.txt file
```

# To generate proto files

```
python -m grpc_tools.protoc -I=proto --python_out=proto --grpc_python_out=proto your/proto/path/your_new_service.proto
```