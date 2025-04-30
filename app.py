from flask import Flask, jsonify, request
from flask_cors import CORS  # Install with: pip install flask-cors
from retrieval_pipeline import RetrievalPipeline

app = Flask(__name__)
# Configure CORS to allow all origins during development
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://localhost:8080"]}})

# deprecated
# Route to handle artist matching
# @app.route('/match_artists', methods=['GET']) 
# def match_artists_handler():
#     client_id = request.args.get('client_id')
#     project_id = request.args.get('project_id')

#     if not client_id:
#         return jsonify({"error": "client_id is required"}), 400

#     try:
#         allocator = Allocator(client_id, project_id)
#         matches = allocator.get_best_matches()
#         print("Matches found:", matches)

#         return jsonify({"artist_ids": matches}), 200
#     except Exception as e:
#         # Catch any potential errors from the Allocator
#         return jsonify({"error": str(e)}), 500

@app.route('/match_artists', methods=['GET']) 
def match_artists_handler():
    project_id = request.args.get('project_id')

    try:
        matches = RetrievalPipeline(project_id).get_response()

        return jsonify({"artist_ids": matches}), 200
    except Exception as e:
        # Catch any potential errors from the Allocator
        return jsonify({"error": str(e)}), 500

@app.route('/assist', methods=['GET'])
def assist():
    project_id = request.args.get('project_id')

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5050)