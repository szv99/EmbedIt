# Import necessary libraries
import os
import re
import requests
import subprocess
import time
from flask import Flask, Response, request
from urllib.parse import urlparse, parse_qs

# Initialize Flask app
app = Flask(__name__)

# Define app settings
APP_PORT = 8080
APP_DEBUG = False

# List of allowed IP addresses
WHITELISTED_IPS = []  # Example: ["127.0.0.1", "192.168.1.2"]

# Confirmation settings
CONFIRMATION_TIME = 10  # Time in seconds to wait for confirmation
NEEDS_CONFIRMATION = False  # If True, require confirmation before downloading
MAX_DURATION = 240  # Maximum video duration in seconds

# Global cache to track requests
PENDING_REQUESTS = {}

# Function to extract link from TikTok ID or URL
def get_link(link_url, is_tiktok_id):
    if is_tiktok_id:
        tiktok_id = link_url
    else:
        # Get video URL from redirect
        res = requests.get(link_url, allow_redirects=True)
        video_url = res.url

        # Parse video URL to extract TikTok ID
        parsed = urlparse(video_url)
        tiktok_id = parsed.path.split('/')[-1].split('?')[0]

    # Construct API URL to fetch video details
    api_url = f"https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/feed/?aweme_id={tiktok_id}"

    # Set request headers
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'TikTok 26.2.0 rv:262018 (iPhone; iOS 14.4.2; en_US) Cronet'
    }

    # Send API request to fetch video details
    api_res = requests.get(api_url, headers=headers)
    api_res.raise_for_status()

    # Extract download link from API response
    download_link = api_res.json()['aweme_list'][0]['video']['play_addr']['url_list'][0]

    return download_link



# Route handler for Instagram Reels download
@app.route('/reels/<reels_id>/')
@app.route('/reel/<reels_id>/')
@app.route('/p/<reels_id>/')  # Additional route for /p/
def get_reels(reels_id):
    # Get client IP address
    client_ip = request.headers.get('X-Real-IP', request.remote_addr)

    # Construct file name
    file_name = f"reels_{reels_id}.mp4"

    # Check if file exists locally
    if not os.path.exists(file_name):
        if NEEDS_CONFIRMATION and client_ip in WHITELISTED_IPS:
            if reels_id in PENDING_REQUESTS:
                # Confirm download request
                PENDING_REQUESTS[reels_id] = "confirmed"
                return "Confirmed."
            else:
                # No pending request for this ID
                return "No pending request for this ID.", 404
        else:
            # Request from Discord or other source
            # Set request status to pending
            PENDING_REQUESTS[reels_id] = "pending"

            # Wait for confirmation
            start_time = time.time()
            while time.time() - start_time < CONFIRMATION_TIME:  # Wait 10 seconds for confirmation
                if PENDING_REQUESTS[reels_id] == "confirmed" or NEEDS_CONFIRMATION is False:
                    # Download video using yt-dlp
                    reels_url = f"https://www.instagram.com/reel/{reels_id}/"
                    try:
                        subprocess.run(['yt-dlp', '-o', file_name, '--cookies', 'instagram_cookies.txt', reels_url], check=True)
                        # Return video data as response
                        return Response(open(file_name, "rb"), content_type='video/mp4')
                    except subprocess.CalledProcessError as e:
                        print(f"Error: {str(e)}")
                        return f"Error downloading video: {e}", 500
                # Wait for one second before checking again
                time.sleep(1)

            # Remove request from pending list if timed out
            del PENDING_REQUESTS[reels_id]
            return "Video download request timed out.", 408

    # File exists locally, return video data as response
    return Response(open(file_name, "rb"), content_type='video/mp4')

# Route handler for YouTube and TikTok video download
@app.route('/<path:video_id>/', strict_slashes=False)
def get_video(video_id):

    # Handle YouTube video URLs
    if 'watch' in video_id:
        # Extract video ID from query string parameter
        video_id_param = parse_qs(request.query_string.decode('utf-8')).get('v', None)
        if video_id_param:
            video_id = video_id_param[0]

    # Handle TikTok video URLs
    if 'video' in video_id:
        # Extract video ID from URL
        video_id = re.findall(r"\d+", video_id)[-1]

    # Construct file name
    file_name = f"youtube_{video_id}.mp4" if len(video_id) == 9 else f"{video_id}.mp4"

    # Check if file exists locally
    if not os.path.exists(file_name):
        client_ip = request.headers.get('X-Real-IP', request.remote_addr)
        if NEEDS_CONFIRMATION and client_ip in WHITELISTED_IPS:
            if video_id in PENDING_REQUESTS:
                # Confirm download request
                PENDING_REQUESTS[video_id] = "confirmed"
                return "Confirmed."
            else:
                # No pending request for this ID
                return "No pending request for this ID.", 404
        else:
            # Request from Discord or other source
            # Set request status to pending
            PENDING_REQUESTS[video_id] = "pending"

            # Wait for confirmation
            start_time = time.time()
            while time.time() - start_time < CONFIRMATION_TIME:  # Wait 10 seconds for confirmation
                if PENDING_REQUESTS[video_id] == "confirmed" or NEEDS_CONFIRMATION is False:
                    # Download video using appropriate method
                    if len(video_id) == 9:  # YouTube video
                        youtube_url = f"https://youtu.be/{video_id}"
                        try:
                            subprocess.run(['yt-dlp', '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4', '--match-filter', f"duration<{MAX_DURATION}", '-o', file_name, youtube_url], check=True)
                            # Return video data as response
                            return Response(open(file_name, "rb"), content_type='video/mp4')
                        except subprocess.CalledProcessError as e:
                            print(f"Error: {str(e)}")
                            return f"Error downloading video: {e}", 500
                    else:  # TikTok video
                        if len(video_id) > 12:
                            # Use TikTok video URL
                            video_url = get_link(video_id, True)
                        else:
                            # Use TikTok video ID
                            tiktok_url = f"https://vm.tiktok.com/{video_id}"
                            video_url = get_link(tiktok_url, False)

                        # Download video data
                        video_data = requests.get(video_url).content

                        # Save video data to local file
                        with open(file_name, 'wb') as f:
                            f.write(video_data)

                        # Return video data as response
                        return Response(video_data, content_type='video/mp4')
                # Wait for one second before checking again
                time.sleep(1)

            # Remove request from pending list if timed out
            del PENDING_REQUESTS[video_id]
            return "Video download request timed out.", 408

    # File exists locally, return video data as response
    return Response(open(file_name, "rb"), content_type='video/mp4')


if __name__ == "__main__":
    app.run('0.0.0.0', APP_PORT, debug=APP_DEBUG)