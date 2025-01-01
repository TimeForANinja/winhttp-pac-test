from flask import Flask, jsonify, request
from flasgger import Swagger
from urllib.parse import urlparse

import .actions
import .mytypes

app = Flask(__name__)
swagger = Swagger(app)

@app.route('/up', methods=['GET'])
def up():
    """
    ---
    tags:
      - Status
    summary: Check server status
    description: This route returns the status of the server to confirm it is operational.
    responses:
      200:
        description: Server is operational.
        schema:
          type: object
          properties:
            status:
              type: string
              description: The status of the server.
              example: "success"
    """
    return jsonify({ "status": "success"})

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
        "pacs": actions.list_pac()
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
    if not actions.has_pac(uid):
        return jsonify({"error": "PAC not found"}), 404

    return actions.get_pac(uid).full(), 200


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
    content = request.json.get("content")

    if not content:
        return jsonify({"error": "The 'content' field is required"}), 400

    pac = mytypes.PAC.new_pac(content)

    actions.add_pac(pac)
    return jsonify({"message": "PAC added successfully", "uid": pac.id}), 201


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
    req_data = request.json
    content = req_data.get("content")

    if not content:
        return jsonify({"error": "The 'content' field is required"}), 400

    pac = mytypes.PAC.new_pac(content)
    actions.add_pac(pac)

    return eval(pac, req_data)


@app.route('/api/v1/eval/<uid>', methods=['POST'])
def evaluate_by_uid(uid):
    """
    ---
    tags:
      - PAC
    summary: Evaluate a PAC file by its UID, using the provided input
    parameters:
      - name: uid
        in: path
        required: true
        type: string
        description: Unique identifier of the PAC file
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
          required:
            - dest_host
            - src_ip
    responses:
      200:
        description: Evaluation completed successfully
      400:
        description: Missing required fields
      404:
        description: PAC file does not exist
    """
    if not actions.has_pac(uid):
        return jsonify({"error": f"The PAC file '{uid}' does not exist"}), 404
    pac = actions.get_pac(uid)

    # Parse and validate the required fields
    req_data = request.json

    return eval(pac, req_data)


def validate_url(url):
    try:
        parsed = urlparse(url)
        # Check scheme and hostname
        if not parsed.scheme or not parsed.netloc:
            return False
        return True
    except Exception:
        return False


def eval(pac, req_body):
    dest_host = req_body.get("dest_host")
    src_ip = req_body.get("src_ip")

    if not dest_host or not src_ip:
        return jsonify({"error": "Fields 'dest_host' and 'src_ip' are required"}), 400

    if not validate_url(dest_host) or not validate_url(src_ip):
        return jsonify({"error": "'dest_url' and 'src_ip' must be valid URLs"}), 400

    eval_data = mytypes.EvalData(pac, dest_host, src_ip)
    result = actions.eval_pac(eval_data)

    return jsonify(result.full()), 200


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
    if not actions.has_pac(uid):
        return jsonify({"error": "PAC not found"}), 404

    return actions.get_pac(uid).content, 200, {'Content-Type': 'application/x-ns-proxy-autoconfig'}


if __name__ == '__main__':
    app.run(port=8080, host="0.0.0.0")
