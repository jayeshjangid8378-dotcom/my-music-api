from flask import Flask, request, jsonify
from flask_cors import CORS
from ytmusicapi import YTMusic
import yt_dlp
import os 

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
    
# 2. Gaana play karne ke liye Audio URL nikalna
@app.route('/play', methods=['GET'])
def get_audio_url():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({'error': 'Video ID missing'}), 400

    # Puraane sabhi complicated formats hata rahe hain
    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
    }
    
    # Agar cookies file maujood hai, toh iska use karo
    if os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            
            # Agar direct url na mile, toh formats list me se dhoondho
            audio_url = info.get('url') or ''
            if not audio_url and 'formats' in info:
                for f in info['formats']:
                    if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                        audio_url = f.get('url', '')
                        break
            
            if audio_url:
                return jsonify({'url': audio_url})
            else:
                return jsonify({'error': 'Format extraction failed'}), 500

    except Exception as e:
        print(f"Play Error: {e}")
        return jsonify({'error': 'Audio link nahi mila'}), 500
    
if __name__ == '__main__':
    print("🔥 Upgraded Engine Start ho gaya! Running on http://127.0.0.1:5000")
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
