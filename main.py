from flask import Flask, request, jsonify
from flask_cors import CORS
from ytmusicapi import YTMusic
import requests  # Nayi library Piped API call karne ke liye

app = Flask(__name__)
CORS(app) 
ytmusic = YTMusic()

# 1. Gaane dhoondhne wala route (Same rahega)
@app.route('/search', methods=['GET'])
def search_songs():
    query = request.args.get('q')
    if not query:
        return jsonify([])

    try:
        results = ytmusic.search(query, filter="songs", limit=10)
        songs = []
        for item in results:
            title = item.get('title', 'Unknown Title')
            artists_list = item.get('artists', [])
            artist_name = ", ".join([a['name'] for a in artists_list]) if artists_list else "Unknown Artist"
            
            songs.append({
                'title': title,
                'artist': artist_name,
                'videoId': item.get('videoId')
            })
        return jsonify(songs)
    except Exception as e:
        print(f"Search Error: {e}")
        return jsonify([])

# 2. Gaana play karne ke liye THE SMART ROUTE (Piped API)
@app.route('/play', methods=['GET'])
def get_audio_url():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({'error': 'Video ID missing'}), 400

    try:
        # Piped API ek open-source frontend hai jo YouTube ki restrictions ko server-side handle karta hai
        piped_url = f"https://pipedapi.kavin.rocks/streams/{video_id}"
        headers = {'Accept': 'application/json'}
        
        response = requests.get(piped_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            audio_streams = data.get('audioStreams', [])
            
            if audio_streams:
                # Sabse best M4A/MP4 audio format dhoondhna
                best_audio = audio_streams[-1]['url'] # Default fallback
                for stream in audio_streams:
                    if stream.get('mimeType', '').startswith('audio/mp4'):
                        best_audio = stream['url']
                        break
                        
                return jsonify({'url': best_audio})
        
        return jsonify({'error': 'Audio stream nahi mila'}), 500

    except Exception as e:
        print(f"Play Error: {e}")
        return jsonify({'error': 'Extraction failed'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
