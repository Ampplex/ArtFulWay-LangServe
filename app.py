from flask import Flask, jsonify, request
from allocator import Allocator

app = Flask(__name__)

@app.route('/match_artists', methods=['GET'])
def match_artists_handler():
    client_id = request.args.get('client_id')
    
    if not client_id:
        return jsonify({"error": "client_id is required"}), 400
    
    try:
        allocator = Allocator(client_id)
        matches = allocator.get_best_matches()
        
        return jsonify({"artist_ids": matches})
    
    except Exception as e:
        # Catch any potential errors from the Allocator
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)