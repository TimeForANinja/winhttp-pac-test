import requests
from flask import Flask, jsonify, request
import uuid
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

# In-memory storage for PAC files
class PAC:
    def __init__(self, id, content, added_time):
        self.id = id
        self.content = content
        self.added_time = added_time

    def simple(self):
        return {
            "id": self.id,
            "added_time": self.added_time
        }
    def full(self):
        return {
            "id": self.id,
            "content": self.content,
            "added_time": self.added_time
        }
pac_store = {}

# Map of known "pac-engines"
engines = {
    "v8": "http://localhost:8081/",
    "winhttp": "http://localhost:8082/"
}

@app.route('/api/v1/pac', methods=['GET'])
def list_all_pacs():
    """
    ---
    tags:
      - PAC
    summary: List all PACs stored in memory
    responses:
      200:
        description: A JSON object containing all the PAC IDs and their content
    """
    return jsonify({
        "pacs": [pac.simple() for pac in pac_store.values()]
    }), 200


@app.route('/api/v1/pac/<uid>', methods=['GET'])
def get_pac(uid):
    """
    ---
    tags:
      - PAC
    summary: Get a PAC file by its UID
    parameters:
      - name: uid
        in: path
        required: true
        type: string
        description: Unique identifier of the PAC
    responses:
      200:
        description: PAC found successfully
      404:
        description: PAC not found
    """
    if uid in pac_store:
        return pac_store[uid].full(), 200
    else:
        return jsonify({"error": "PAC not found"}), 404


@app.route('/api/v1/pac', methods=['POST'])
def add_pac():
    """
    ---
    tags:
      - PAC
    summary: Add a new PAC file to the in-memory storage
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            content:
              type: string
              description: The PAC content
          required:
            - content
    responses:
      201:
        description: PAC added successfully
      400:
        description: Required field missing or conflict
    """
    data = request.json
    uid = str(uuid.uuid4())
    content = data.get("content")

    if not content:
        return jsonify({"error": "The 'content' field is required"}), 400

    if uid in pac_store:
        return jsonify({"error": "PAC with this UID already exists"}), 400

    pac_store[uid] = content
    return jsonify({"message": "PAC added successfully", "uid": uid}), 201


@app.route('/api/v1/eval', methods=['POST'])
def evaluate_function():
    """
    ---
    tags:
      - PAC
    summary: Evaluate a PAC file based on the provided input
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            dest_host:
              type: string
              description: The destination host for evaluation
            src_ip:
              type: string
              description: The source IP making the request
            pac_file:
              type: string
              description: Unique identifier of the PAC file
          required:
            - dest_host
            - src_ip
            - pac_file
    responses:
      200:
        description: Evaluation completed successfully
      400:
        description: Missing required fields
      404:
        description: PAC file does not exist
    """
    data = request.json

    # Parse the required fields
    dest_host = data.get("dest_host")
    src_ip = data.get("src_ip")
    pac_file = data.get("pac_file")

    # Validate required fields
    if not dest_host or not src_ip or not pac_file:
        return jsonify({"error": "Fields 'dest_host', 'src_ip', and 'pac_file' are required"}), 400

    # Check if the PAC file exists
    if pac_file not in pac_store:
        return jsonify({"error": f"The PAC file '{pac_file}' does not exist"}), 404

    # Simulate selecting an engine (you can customize how the engine is chosen)
    engine = engines["v8"]  # Default to v8 for now

    # Construct the response
    response = {
        "dest_host": dest_host,
        "src_ip": src_ip,
        "pac_file": pac_file,
        "pac_content": pac_store[pac_file].content,
        "engine": engine
    }

    # Placeholder logic (calling the engine can be implemented later)
    eval_results = {}

    # Iterate over all engines and send POST requests
    for engine_name, engine_url in engines.items():
        try:
            # Prepare the payload for the REST call
            payload = {
                "dest_url": dest_host,
                "src_ip": src_ip,
                "pac_url": f"http://127.0.0.1:8080/pac/{pac_file}",
            }
            # Make the REST request
            res = requests.post(engine_url, json=payload, timeout=5)

            # Add the response to eval results based on status
            if res.status_code == 200:
                eval_results[engine_name] = res.json()
            else:
                try:
                    eval_results[engine_name] = res.json()
                except ValueError:
                    eval_results[engine_name] = {
                        "status": "failed",
                        "message": f"Engine responded with status {res.status_code}, and response is not a JSON",
                        "error": res.text,
                        "error_code": res.status_code
                    }
        except requests.exceptions.Timeout:
            eval_results[engine_name] = {"error": "Request to engine timed out"}
        except requests.exceptions.RequestException as e:
            eval_results[engine_name] = {"error": str(e)}

    response["eval"] = eval_results

    return jsonify({"message": "Evaluation completed", "details": response}), 200

@app.route('/pac/<uid>', methods=['GET'])
def get_pac_alternate(uid):
    """
    ---
    tags:
      - PAC
    summary: Retrieve a PAC file by its UID with the correct content type for PAC files
    parameters:
      - name: uid
        in: path
        required: true
        type: string
        description: Unique identifier of the PAC file.
    responses:
      200:
        description: PAC file returned successfully with the appropriate content type.
        content:
          application/x-ns-proxy-autoconfig:
            schema:
              type: string
              example: "function FindProxyForURL(url, host) { return 'DIRECT'; }"
      404:
        description: The requested PAC file was not found.
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "PAC not found"
    """
    if uid in pac_store:
        return pac_store[uid], 200, {'Content-Type': 'application/x-ns-proxy-autoconfig'}
    else:
        return jsonify({"error": "PAC not found"}), 404


if __name__ == '__main__':
    app.run(port=8080, host="0.0.0.0")
