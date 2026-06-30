from flask import Flask, request, jsonify
from flask_cors import CORS
from ytmusicapi import YTMusic
import yt_dlp

app = Flask(__name__)
CORS(app) 
ytmusic = YTMusic()

# 1. Gaane dhoondhne wala route (Pehle jaisa hi hai)
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

# 2. NAYA ROUTE: Gaana play karne ke liye Audio URL nikalna
@app.route('/play', methods=['GET'])
def get_audio_url():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({'error': 'Video ID missing'}), 400

    # yt-dlp ki settings taaki sirf best quality audio mile
    ydl_opts = {
        'format': 'bestaudio',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'prefer_ffmpeg': False,
        'extractor_args': {'youtube': {'player_client': ['android']}}, # Yeh line YouTube ko confuse karti hai ki request phone se aa rahi hai
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Video ID se direct stream link nikal rahe hain
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            return jsonify({'url': info['url']})
    except Exception as e:
        print(f"Play Error: {e}")
        return jsonify({'error': 'Audio link nahi mila'}), 500

if __name__ == '__main__':
    print("🔥 Upgraded Engine Start ho gaya! Running on http://127.0.0.1:5000")
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
