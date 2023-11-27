# EmbedIt: Flask-Powered Video Embedding

EmbedIt is a Python Flask application designed for downloading and embedding videos from popular social media platforms such as TikTok, Instagram Reels, and YouTube.

## Features

* **Download TikTok Videos Without Watermarks:** EmbedIt allows you to download TikTok videos without watermarks for seamless sharing.
* **Embed Videos from Various Platforms:** Embed videos from TikTok, Instagram Reels, and YouTube effortlessly.
* **IP Whitelisting for Enhanced Security:** Ensure enhanced security by whitelisting specific IP addresses.
* **Reliable Video Downloads:** Utilizes `yt-dlp` for quick and reliable video downloads.
* **Request Confirmation System:** Manage downloads effectively with a request confirmation system.
* **Seamless Embedding:** Embed videos seamlessly in various applications and websites.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/szv99/EmbedIt.git
   ```

2. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application:**

   ```bash
   python app.py
   ```

## Usage

* **Embed a Video from YouTube:**

  To download videos from YouTube, ensure `yt-dlp` is in your path.

  ```bash
  http://localhost:8080/watch?v=VIDEO_ID
  http://localhost:8080/VIDEO_ID
  ```

* **Embed a Video from Instagram Reels:**

  To download videos from Instagram, import your Instagram cookies from your browser to a file called `instagram_cookies.txt` in Netscape format.

  ```bash
  http://localhost:8080/reels/REELS_ID
  http://localhost:8080/reel/REELS_ID
  http://localhost:8080/p/POST_ID
  ```

* **Embed a Video from TikTok:**

  ```bash
  http://localhost:8080/VIDEO_ID
  http://localhost:8080/@user/video/VIDEO_ID
  ```

## Customization

* **IP Whitelisting:**
  - Locate `WHITELISTED_IPS` and `NEEDS_CONFIRMATION` in the script.
  - Replace existing IP addresses with the ones you want to whitelist.
  - Set `NEEDS_CONFIRMATION` to True.

* **Server Configuration:**
  - Adjust the `app` parameters at the top of the script to set the desired host and port.

* **Nginx Example Configuration:**

  ```nginx
  location / {
    proxy_pass http://localhost:8080;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  }
  ```