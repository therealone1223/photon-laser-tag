#Quinn Cornia
#Splash Screen
import tkinter as tk
from PIL import Image, ImageTk
import os

class SplashScreen:
    def __init__(self, root, duration=3000, on_close=None):
        self.root = root
        self.on_close = on_close
        self.root.title("Photon Laser Tag")
        
        #Get screen dimensions 
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        #Set the size of window
        window_height = 850
        window_width = 850
        
        # Center the window 
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.configure(bg='black')
        
        # Create frame 
        frame = tk.Frame(self.root, bg='black')
        frame.pack(expand=True, fill='both')
        
        # Try to load image
        try:
            parent_dir = os.path.dirname(os.path.dirname(__file__))
            logo_path = os.path.join(parent_dir, 'logo.jpg')
            
            image = Image.open(logo_path)
            image = image.resize((800, 800), Image.LANCZOS)
            
            self.photo = ImageTk.PhotoImage(image)
            image_label = tk.Label(frame, image=self.photo, bg='black')
            image_label.pack(pady=20)
            
        except Exception as e:
            print(f"Could not load image: {e}")
        
        self.root.after(duration, self.close_splash)
    
    def close_splash(self):
        self.root.destroy()
        if self.on_close:
            self.on_close()

if __name__ == "__main__":
    root = tk.Tk()
    splash = SplashScreen(root, duration=3000)
    root.mainloop()