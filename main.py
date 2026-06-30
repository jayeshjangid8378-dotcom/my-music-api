# 2. Gaana play karne ke liye (Multi-Server Fallback Logic)
@app.route('/play', methods=['GET'])
def get_audio_url():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({'error': 'Video ID missing'}), 400

    # 4 alag-alag backup servers ka array 
    backup_servers = [
        f"https://api.piped.projectsegfau.lt/streams/{video_id}",
        f"https://pipedapi.tokhmi.xyz/streams/{video_id}",
        f"https://pipedapi.smnz.de/streams/{video_id}",
        f"https://pipedapi.kavin.rocks/streams/{video_id}"
    ]

    # Array par iterate karenge, jo server zinda hoga wahan se audio nikal lenge
    for api_url in backup_servers:
        try:
            # Sirf 4 second wait karenge, agar timeout hua toh agle par jump
            response = requests.get(api_url, timeout=4) 
            
            if response.status_code == 200:
                data = response.json()
                audio_streams = data.get('audioStreams', [])
                
                if audio_streams:
                    best_audio = audio_streams[-1]['url']
                    for stream in audio_streams:
                        # MP4 audio format sabse stable hota hai mobile players ke liye
                        if stream.get('mimeType', '').startswith('audio/mp4'):
                            best_audio = stream['url']
                            break
                    
                    print(f"🔥 Successfully fetched from: {api_url}")
                    return jsonify({'url': best_audio})
                    
        except Exception as e:
            print(f"Skipping {api_url} due to error...")
            continue # Ek block hua toh turant agle server par skip karo

    return jsonify({'error': 'Saare servers fail ho gaye'}), 500
