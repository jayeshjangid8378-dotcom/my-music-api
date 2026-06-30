from flask import Flask, request, jsonify
from flask_cors import CORS
from ytmusicapi import YTMusic
from pytubefix import YouTube

app = Flask(__name__)
CORS(app) 
ytmusic = YTMusic()

# 1. Gaane dhoondhne wala route
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

# 2. Gaana play karne ke liye NAYA ROUTE (TV Client Bypass)
@app.route('/play', methods=['GET'])
def get_audio_url():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({'error': 'Video ID missing'}), 400

    try:
        yt_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # 'TV' client sabse stable hai, yeh 400 Error aur PO Token dono bypass kar deta hai
        yt = YouTube(yt_url, client='TV') 
        
        # Sirf best audio stream nikal rahe hain
        audio_stream = yt.streams.get_audio_only()
        
        if audio_stream and audio_stream.url:
            return jsonify({'url': audio_stream.url})
        else:
            return jsonify({'error': 'Audio stream nahi mila'}), 500

    except Exception as e:
        print(f"Play Error: {e}")
        return jsonify({'error': 'Extraction failed'}), 500

    except Exception as e:
        print(f"Play Error: {e}")
        return jsonify({'error': 'Extraction failed'}), 500

    except Exception as e:
        print(f"Play Error: {e}")
        return jsonify({'error': 'Extraction failed'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
