import requests
import json

url = "http://localhost:5000/receive"

# JSON data sent to server
data = {
    "name": "Meghana",
    "course": "Web Technologies",
    "role": "Client"
}

# Send POST request with JSON
response = requests.post(url, json=data)

# Display server response
print("Response from server:")
print(json.dumps(response.json(), indent=4))
