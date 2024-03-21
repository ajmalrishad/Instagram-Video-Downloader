from io import BytesIO
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
from instaloader import Instaloader, Post
from tkinter import ttk
from PIL import Image, ImageTk
import requests

class VideoDownloaderApp:
    def __init__(self, master):
        self.master = master
        master.title("Instagram Video Downloader")

        # Load Instagram logo image
        self.instagram_logo = Image.open("instagramlogo.png")
        self.instagram_logo_tk = ImageTk.PhotoImage(self.instagram_logo.resize((50, 50)))

        # Create label for Instagram logo
        self.instagram_logo_label = tk.Label(master, image=self.instagram_logo_tk)
        self.instagram_logo_label.pack(pady=50)
        
        self.url_label = tk.Label(master, text="Paste Instagram Video URL", fg="black")
        self.url_label.pack(padx=10, pady=10)

        self.url_entry = tk.Entry(master, width=50)
        self.url_entry.pack(padx=10, pady=10)
        # Bind right-click context menu to the entry widget
        self.url_entry.bind("<Button-3>", self.show_menu)

        self.process_button = tk.Button(master, text="PROCESS", bg="#3b71ca", fg="white", command=self.process_video, font=('Helvetica', 10))
        self.process_button.pack()

        self.resolution_var = tk.StringVar(master)  # Initialize resolution variable

        self.downloading = False  # Flag to track if download is in progress

    def show_menu(self, event):
        # Create a right-click context menu
        menu = tk.Menu(self.master, tearoff=0)
        menu.add_command(label="Paste", command=lambda: self.url_entry.event_generate('<<Paste>>'))
        menu.tk_popup(event.x_root, event.y_root)

    def process_video(self):
        video_link = self.url_entry.get()
        startwith = video_link.startswith('https://www.instagram.com/')
        if video_link and startwith:
            if video_link and not self.downloading:  # Check if URL is valid and no download in progress
                self.master.withdraw()  # Hide the main window
                self.show_success_page(video_link)
            elif self.downloading:
                messagebox.showinfo("Download in Progress", "A download is already in progress. Please wait until it completes.")
            else:
                messagebox.showerror("Error", "No video URL found.")
        else:
            messagebox.showerror("Error", "Please enter a valid video URL.")
            
    #sucess_page 
    def show_success_page(self, video_link):
        success_window = tk.Toplevel(self.master)
        success_window.geometry(self.master.geometry())
        try:
            L = Instaloader()
            post = Post.from_shortcode(L.context, video_link.split("/")[-2])
            # Fetch video thumbnail 
            thumbnail = post._full_metadata_dict['thumbnail_src']
            response = requests.get(thumbnail)
            img = Image.open(BytesIO(response.content))
            img = img.resize((300, 300), Image.ANTIALIAS)
            img = ImageTk.PhotoImage(img)
            thumbnail_label = tk.Label(success_window, image=img)
            thumbnail_label.image = img
            thumbnail_label.pack(pady=10)
            #fetch title
            title = post._full_metadata['edge_media_to_caption']['edges'][0]['node']['text']
            if title:
                self.video_name_label = tk.Label(success_window, text="Video Title: "f'{title}')
                self.video_name_label.pack(pady=10)
            else:
                self.video_name_label = tk.Label(success_window, text="Video Title: Not available")
                self.video_name_label.pack(pady=10)
        except:
            messagebox.showinfo("Error","Instagram video thumbnail not found")
            self.thumbnail = tk.Label(success_window, text="Thumbnail: Not available")
            self.thumbnail.pack(pady=20)
            retry = tk.Button(success_window, text="Retry", bg="red", fg="white", command=lambda: self.retry(success_window))
            retry.pack()

        # Download button
        download_button = tk.Button(success_window, text="Download", bg="green", fg="white", command=lambda: self.download_video(video_link, success_window))
        download_button.pack(padx=20,pady=20)

    def retry(self, success_window):
            success_window.destroy()  # Close the success window
            self.master.deiconify()   # Show the master window


    def download_video(self, video_link, success_window):
        self.downloading = True  # Set downloading flag to True
        self.process_button.config(state='disabled')  # Disable the download button

        download_thread = threading.Thread(target=self.download_video_thread, args=(video_link, success_window))
        download_thread.start()

    #download video 
    def download_video_thread(self, video_link, success_window):
        L = Instaloader()
        try:
            post = Post.from_shortcode(L.context, video_link.split("/")[-2])
            target_filename = str(post.mediaid) + ".mp4"
            if post.is_video:
                # Create a label for download video status
                self.downloadstatus = tk.Label(success_window, fg="green", text="Downloading...")
                self.downloadstatus.pack(pady=10)

                # Create progress bar
                self.progress_bar = ttk.Progressbar(success_window, mode='determinate')
                self.progress_bar.pack()

                self.progress_bar.start()  # Start the progress bar
                L.download_post(post, target=target_filename)  # Download the video
                self.master.deiconify()  # Show the main window again after download
                self.process_button.config(state='normal')
                # Hide the success window and destroy it
                success_window.destroy()
                messagebox.showinfo("Success", "Instagram video downloaded successfully")
                return True
            else:
                messagebox.showinfo("Not a Video", "The provided link is not for a video.")
        except Exception as e:
            messagebox.showerror("Error", f"Error video downloading please try again later: {str(e)}")
            self.master.deiconify()  # Show the main window again after download
            self.process_button.config(state='normal')
            # Hide the success window and destroy it
            success_window.destroy()
            return False
        finally:
            self.downloading = False
            self.process_button.config(state='normal')


def main():
    root = tk.Tk()
    root.iconbitmap(r'favicon.ico')
    root.minsize(500, 500)
    app = VideoDownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
