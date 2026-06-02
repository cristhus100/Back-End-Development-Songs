"""Songs Microservice - Flask REST API with MongoDB"""
import os
from flask import Flask, jsonify, request
from bson import ObjectId, json_util
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# MongoDB connection (with in-memory fallback)
mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
USE_MONGO = False

try:
    client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=2000)
    client.admin.command('ping')
    db = client['songs_db']
    songs_collection = db['songs']
    USE_MONGO = True
    print("Connected to MongoDB successfully")
except Exception as e:
    print(f"MongoDB not available: {e}")
    print("Using in-memory storage instead")
    # In-memory fallback
    songs_db_memory = {}
    next_id = 1


def get_next_id():
    """Get next ID for in-memory storage"""
    global next_id
    current = next_id
    next_id += 1
    return str(current)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "OK"}), 200


@app.route('/song', methods=['GET'])
def get_songs():
    """Get all songs"""
    if USE_MONGO:
        songs = list(songs_collection.find({}))
        return json_util.dumps(songs), 200, {'Content-Type': 'application/json'}
    else:
        return jsonify(list(songs_db_memory.values())), 200


@app.route('/song/<string:song_id>', methods=['GET'])
def get_song(song_id):
    """Get a single song by ID"""
    if USE_MONGO:
        try:
            song = songs_collection.find_one({"_id": ObjectId(song_id)})
        except:
            return jsonify({"error": "Invalid ID format"}), 400
        if not song:
            return jsonify({"error": "Song not found"}), 404
        return json_util.dumps(song), 200, {'Content-Type': 'application/json'}
    else:
        song = songs_db_memory.get(song_id)
        if not song:
            return jsonify({"error": "Song not found"}), 404
        return jsonify(song), 200


@app.route('/song', methods=['POST'])
def create_song():
    """Create a new song"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    song = {
        "title": data.get("title", ""),
        "artist": data.get("artist", ""),
        "genre": data.get("genre", ""),
        "lyrics": data.get("lyrics", "")
    }

    if USE_MONGO:
        result = songs_collection.insert_one(song)
        song["_id"] = result.inserted_id
        return json_util.dumps(song), 201, {'Content-Type': 'application/json'}
    else:
        song_id = get_next_id()
        song["id"] = song_id
        songs_db_memory[song_id] = song
        return jsonify(song), 201


@app.route('/song/<string:song_id>', methods=['PUT'])
def update_song(song_id):
    """Update an existing song"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    if USE_MONGO:
        try:
            song = songs_collection.find_one({"_id": ObjectId(song_id)})
        except:
            return jsonify({"error": "Invalid ID format"}), 400
        if not song:
            return jsonify({"error": "Song not found"}), 404

        update_data = {}
        for field in ["title", "artist", "genre", "lyrics"]:
            if field in data:
                update_data[field] = data[field]

        songs_collection.update_one({"_id": ObjectId(song_id)}, {"$set": update_data})
        updated = songs_collection.find_one({"_id": ObjectId(song_id)})
        return json_util.dumps(updated), 200, {'Content-Type': 'application/json'}
    else:
        song = songs_db_memory.get(song_id)
        if not song:
            return jsonify({"error": "Song not found"}), 404

        for field in ["title", "artist", "genre", "lyrics"]:
            if field in data:
                song[field] = data[field]

        return jsonify(song), 200


@app.route('/song/<string:song_id>', methods=['DELETE'])
def delete_song(song_id):
    """Delete a song"""
    if USE_MONGO:
        try:
            result = songs_collection.delete_one({"_id": ObjectId(song_id)})
        except:
            return jsonify({"error": "Invalid ID format"}), 400
        if result.deleted_count == 0:
            return jsonify({"error": "Song not found"}), 404
        return jsonify({"result": "Song deleted"}), 200
    else:
        song = songs_db_memory.get(song_id)
        if not song:
            return jsonify({"error": "Song not found"}), 404
        del songs_db_memory[song_id]
        return jsonify({"result": "Song deleted"}), 200


@app.route('/count', methods=['GET'])
def count():
    """Return the number of songs stored"""
    if USE_MONGO:
        count = songs_collection.count_documents({})
    else:
        count = len(songs_db_memory)
    return jsonify({"count": count}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
