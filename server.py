from flask import Flask, request, jsonify

app = Flask(__name__)

# Home route (avoids Cannot GET /)
@app.route("/", methods=["GET"])
def home():
    return "Python JSON Server is running"

# JSON communication route
@app.route("/receive", methods=["POST"])
def receive_data():
    client_data = request.json

    print("Received from client:", client_data)

    response = {
        "status": "success",
        "message": "Hello Client, JSON received",
        "receivedData": client_data
    }
    return jsonify(response)

if __name__ == "__main__":
    app.run(port=5000)
