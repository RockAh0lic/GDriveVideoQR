import os
import time
import requests
import qrcode
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from extractSnapshot import download_video_from_gdrive
from PlayVideos import VideoPlayer

# Folder link (make sure it ends with '/view')
folder_link = 'PULBIC GDRIVE FOLDER LINK'
Display_No = 1 #SPECIFY THE OUTPUT DISPLAY ID/No

folder_id_start = folder_link.find("folders/") + 8
folder_id_end = folder_link.find("?usp", folder_id_start + 1)
folder_id = folder_link[folder_id_start:folder_id_end]

# Function to load already processed items from a file
def load_processed_items(filename):
    processed_items = []
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            for line in file:
                print(eval(line.strip()))
                processed_items.append(eval(line.strip()))
    return processed_items

allItems = load_processed_items("items.txt")

# Function to save processed items to a file
def save_processed_items(filename, items):
    with open(filename, 'w', errors='ignore') as file:
        for item in items:
            file.write(str(item) + '\n')
        file.close()

# Function to generate a QR code for a given link
def generate_qr_code(link, output_path):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save(output_path)

# Function to monitor a Google Drive folder for new files using the folder's public link
def monitor_drive_folder(folder_link):
    response = requests.get(folder_link)
    response.raise_for_status()
    folder_content = response.text
    files = []

    # Parse the folder content to find public file links
    for line in folder_content.splitlines():
        while 'drive.google.com/file/d/' in line:
            start = line.find('"https://drive.google.com/file/d/') + 1
            end = line.find('"', start)
            file_link = line[start:end]
            # print(file_link)
            if 'drive.google.com/file/d/' in file_link:
                file_id_start = file_link.find('/d/') + 3
                file_id_end = file_link.find('/', file_id_start + 1)
                file_id = file_link[file_id_start:file_id_end]
                
                line1 = line
                file_name_start = line1.find(f'"{file_id}",["{folder_id}"],"', end) + 75
                file_name_end = line1.find('","video/mp4', file_name_start)
                file_name = line1[file_name_start:file_name_end]

                # file_name_start = line.find('>', end) + 1
                # file_name_end = line.find('<', file_name_start)
                # file_name = line[file_name_start:file_name_end]
                if "null" not in file_name:
                    files.append({'id': file_id, 'name': file_name, 'link': f"https://drive.google.com/uc?export=view&id={file_id}"})
            line = line[end:len(line)]
    return files

# Create a directory for QR codes
if not os.path.exists('qr_codes'):
    os.makedirs('qr_codes')

# Monitor the local directory for new files (optional part)
class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print(f'New file detected: {event.src_path}')
            # Assuming the new file is uploaded to the Drive folder, generate a QR code
            time.sleep(2)  # Wait for the file to be fully uploaded
            items = monitor_drive_folder(folder_link)
            for item in items:
                if item['name'] == os.path.basename(event.src_path):
                    qr_output_path = f"qr_codes/{item['name']}.png"
                    generate_qr_code(item['link'], qr_output_path)
                    print(f"QR code generated for {item['name']}: {qr_output_path}")

player = VideoPlayer(display_number=Display_No)

# Monitor the Google Drive folder
try:
    while True:
        time.sleep(1)
        items = monitor_drive_folder(folder_link)

        for item in items:
            if item not in allItems:
                print(f"New Item: {item['id']}")
                qr_output_path = f"qr_codes/{item['id']}.png"
                if not os.path.exists(qr_output_path):
                    generate_qr_code(item['link'], qr_output_path)
                    print(f"QR code generated for {item['name']}: {qr_output_path}")
                    download_video_from_gdrive(item['id'])
                    # PlayVideo(item['id'])
                    player.play_video(item['id'])
                allItems.append(item)

        save_processed_items("items.txt", allItems)

except KeyboardInterrupt:
    print("Stopped by user")
