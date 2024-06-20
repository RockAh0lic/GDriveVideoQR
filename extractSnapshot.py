import requests
import editVideo

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None

def download_video_from_gdrive(file_id):
    # URL for downloading the file
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    session = requests.Session()
    
    # Initial request to get the confirmation token if needed
    response = session.get(download_url, params={'id': file_id}, stream=True)
    
    confirmation_token = get_confirm_token(response)
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            confirmation_token = value
            break
    
    # If a confirmation token is found, use it to confirm the download
    if confirmation_token:
        params = {'id': file_id, 'confirm': confirmation_token}
        response = session.get(download_url, params=params, stream=True)
    else:
        response = session.get(download_url, stream=True)
    
    # Save the file to the specified output path
    with open(f"videos/{file_id}.mp4", 'wb') as file:
        for chunk in response.iter_content(chunk_size=32768):
            if chunk:
                file.write(chunk)

    editVideo.overlay_png_on_video(f"videos/{file_id}.mp4", f"qr_codes/{file_id}.png", "assets/Background.png", f"edited_videos/{file_id}.mp4", ('right', 'center'))

