#!/usr/bin/env python
from flask import Flask, request, jsonify
from allocator import Allocator
import os

app = Flask(__name__)

@app.route("/match-artists", methods=["GET"])
def match_artists():
    client_id = request.args.get("client_id")
    if not client_id:
        return jsonify({"error": "client_id is required"}), 400
    
    allocator = Allocator(client_id)
    matches = allocator.get_best_matches()
    return jsonify({"artist_ids": matches})

@app.route("/test-match-artists", methods=["POST"])
def test_match_artists():
    data = request.json
    print("Received data:", data)
    return jsonify({"message": "Success", "received_client_id": data.get("client_id")})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)