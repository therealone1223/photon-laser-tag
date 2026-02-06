#Quinn Cornia
#Splash Screen



import tkinter as tk
from PIL import Image, ImageTk
import os
class SplashScreen:
    def __init__(self,root, duration = 3000):
        self.root = root
        self.root.title("Photon Laser Tag")
        
        #photoGet screen dimensions 
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        #Set the size of window
        window_height = 850
        window_width = 850

        # Center the window 
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # Create frame 
        frame = tk.Frame(self.root, bg = 'black')
        frame.pack(expand = True, fill = 'both')

        #Load image 
        
        #
        # Trys to load image
        try:
            parent_dir = os.path.dirname(os.path.dirname(__file__))
            
            #Loads and resizes the image
            logo_path = os.path.join(parent_dir, 'logo.jpg')
            image = Image.open(logo_path)
            image = image.resize((400,400), Image.LANCZOS)
            
            #Creates and packs the label
            self.background = ImageTk.PhotoImage(image)
            image_label = tk.Label(frame,image = self.background)
            image_label.pack(pady = 20)
        
        #If it fails throw exception
        except Exception as e:
            print(f"Could not load image: {e}")

        self.root.after(duration,self.close_splash)
    def close_splash(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    #Screen last 3 seconds
    splash = SplashScreen(root, duration = 3000)
 
    root.mainloop()

            

