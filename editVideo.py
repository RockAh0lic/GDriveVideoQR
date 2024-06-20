from moviepy.editor import *
import numpy as np
from PIL import Image 

def overlay_png_on_video(video_path, overlay_image_path, background_image_path, output_path, overlay_coords):
    # Load the main video
    overlay_offset = [0, 0]
    print("Loading video...")
    video = VideoFileClip(video_path)

    # Load and adjust background
    background_image = ImageClip(background_image_path).set_duration(video.duration)

    # Load the overlay image (PNG)
    print("Loading overlay image...")
    qrcode = Image.open(overlay_image_path).convert("RGB")
    qrcode_np = np.array(qrcode)
    overlay_image = ImageClip(qrcode_np).set_duration(video.duration)
    # overlay_image = ImageClip(overlay_image_path).set_duration(video.duration)

    # Calculate the position for the overlay image
    video_width, video_height = (3840, 2160)
    overlay_image = overlay_image.resize(height=video_height // 4)  # Resize overlay image to 1/4 of video height
    overlay_width, overlay_height = overlay_image.size
    third_width = video_width // 3

    # Calculate the x position for the center of the right third
    x_position = (2 * third_width) + (third_width // 2) - (overlay_width // 2) + overlay_offset[0]
    y_position = (video_height // 2) - (overlay_height // 2) + overlay_offset[1]
    
    # Resize the overlay image
    overlay_image = overlay_image.set_position((x_position, y_position))
    
    print(f"Overlay image size: {overlay_image.size}")

    # Composite the video with the background image and overlay image
    print("Compositing video...")
    final_video = CompositeVideoClip([background_image, video.set_position("center"), overlay_image])

    # Write the output video
    print("Writing output video...")
    final_video.write_videofile(output_path, codec='libx264')
    print("Done!")


# overlay_png_on_video("videos/1V2eZYJ1bTSW_xZOuUyUTuWRfbc28QrVX.mp4", "qr_codes/1V2eZYJ1bTSW_xZOuUyUTuWRfbc28QrVX.png", "assets/Background.png", "edited_videos/1V2eZYJ1bTSW_xZOuUyUTuWRfbc28QrVX.mp4", ('right', 'center'))