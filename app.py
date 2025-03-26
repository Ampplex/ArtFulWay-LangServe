#!/usr/bin/env python
import json
from infrastructure.compute.allocator import Allocator

def match_artists_handler():
    client_id = "67bab8b3d8b4179c417669b4"
    if not client_id:
        return json.dumps({"error": "client_id is required"}), 400
    
    allocator = Allocator(client_id)
    matches = allocator.get_best_matches()
    
    return json.dumps({"artist_ids": matches})

# Call function
if __name__ == "__main__":
    result = match_artists_handler()
    print(result)  # Print output as JSON