import requests

ipfs_api_url = 'http://localhost:5001/api/v0/add'
ipfs_gateway_url = 'http://localhost:9090/ipfs/'

# Function to upload and pin a file to IPFS
def upload_and_pin_file(file_path):
    # Upload the file
    with open(file_path, 'rb') as file:
        response = requests.post(ipfs_api_url, files={'file': file})

    if response.status_code == 200:
        ipfs_hash = response.json()['Hash']
        print(f"File uploaded successfully. CID: {ipfs_hash}")
        
        # Pin the file to IPFS
        pin_file(ipfs_hash)
        return ipfs_hash
    else:
        print(f"Error uploading file: {response.text}")
        return None
    
# Function to pin the uploaded file
def pin_file(ipfs_hash):
    pin_api_url = f'http://localhost:5001/api/v0/pin/add?arg={ipfs_hash}'

    response = requests.post(pin_api_url)
    if response.status_code == 200:
        print(f"File with CID {ipfs_hash} pinned successfully.")
    else:
        print(f"Error pinning file: {response.text}")

# Main logic
if __name__ == "__main__":
    file_path = 'files/pintrail.png'  # Replace with your image path
    ipfs_hash = upload_and_pin_file(file_path)