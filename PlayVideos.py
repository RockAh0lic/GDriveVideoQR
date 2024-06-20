import cv2
from ffpyplayer.player import MediaPlayer
from screeninfo import get_monitors
import threading

class VideoPlayer:
    def __init__(self, display_number=1):
        self.display_number = display_number
        self.window_name = "Video"
        self.is_playing = False
        self.thread = None
        self.stop_event = threading.Event()
    
    def get_display_info(self, display_number):
        monitors = get_monitors()
        if display_number >= len(monitors):
            raise ValueError(f"Display number {display_number} is not available. Only {len(monitors)} display(s) found.")
        return monitors[display_number]
    
    def play_video(self, video_path):
        if self.is_playing:
            self.stop_video()
        
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._play_video, args=(video_path,))
        self.thread.start()
    
    def _play_video(self, video_path):
        self.is_playing = True
        video_p = f"edited_videos/{video_path}.mp4"
        
        # Get the display info for the chosen display number
        display_info = self.get_display_info(self.display_number)
        screen_x = display_info.x
        screen_y = display_info.y
        screen_width = display_info.width
        screen_height = display_info.height
        
        while not self.stop_event.is_set():
            video = cv2.VideoCapture(video_p)
            player = MediaPlayer(video_p)

            if not video.isOpened():
                print("Error: Could not open video.")
                self.is_playing = False
                break
            
            # Create the window and set it to fullscreen
            cv2.namedWindow(self.window_name, cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            
            # Move the window to the selected display
            cv2.moveWindow(self.window_name, screen_x, screen_y)
            print(f"Window moved to display {self.display_number} at position ({screen_x}, {screen_y})")
            
            while not self.stop_event.is_set():
                grabbed, frame = video.read()
                audio_frame, val = player.get_frame()
                if not grabbed:
                    print("End of video")
                    break
                if cv2.waitKey(28) & 0xFF == ord("q"):
                    self.stop_event.set()
                    break
                cv2.imshow(self.window_name, frame)
                if val != 'eof' and audio_frame is not None:
                    # audio
                    img, t = audio_frame
            
            video.release()
            player.close_player()
            cv2.destroyAllWindows()

        self.is_playing = False
        print("Released video and destroyed all windows")

    def stop_video(self):
        if self.is_playing:
            self.stop_event.set()
            self.thread.join()
            self.is_playing = False
            print("Video stopped")

