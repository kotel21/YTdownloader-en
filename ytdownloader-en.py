import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import threading
import os
import yt_dlp

# DYNAMICZNA ŚCIEŻKA: Automatycznie wykrywa folder "Pobrane" aktualnego użytkownika
output_path = os.path.join(os.path.expanduser("~"), "Downloads")

def browse_folder():
    global output_path
    folder = filedialog.askdirectory(initialdir=output_path, title="Select Output Folder")
    if folder:
        output_path = folder
        folder_label.config(text=f"Save to: ...{output_path[-35:]}" if len(output_path) > 35 else f"Save to: {output_path}")

def paste_from_clipboard():
    try:
        clipboard_text = root.clipboard_get()
        url_entry.delete(0, tk.END)
        url_entry.insert(0, clipboard_text)
        status_label.config(text="Link pasted from clipboard", fg="black")
    except:
        messagebox.showwarning("Clipboard Error", "Your clipboard is empty or does not contain text!")

def download_video():
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("Error", "Please paste a video link first!")
        return

    url_entry.delete(0, tk.END)

    selected_format = format_combo.get()
    selected_res = res_combo.get()

    res_map = {
        "Best Available": "bestvideo",
        "4K (2160p)": "bestvideo[height<=2160]",
        "1080p FullHD": "bestvideo[height<=1080]",
        "720p HD": "bestvideo[height<=720]",
        "480p": "bestvideo[height<=480]"
    }
    
    video_format = res_map.get(selected_res, "bestvideo")
    
    download_btn.config(state=tk.DISABLED)
    status_label.config(text="Analyzing link...", fg="blue")
    progress_bar["value"] = 0
    
    def progress_hook(d):
        if d['status'] == 'downloading':
            try:
                total = d.get('total_bytes') or d.get('max_bytes') or 1
                downloaded = d.get('downloaded_bytes', 0)
                percentage = (downloaded / total) * 100
                root.after(0, update_progress, percentage, f"Downloading: {percentage:.1f}%")
            except:
                pass
        elif d['status'] == 'finished':
            root.after(0, update_progress, 100, "Merging audio and video...")

    def update_progress(value, text):
        progress_bar["value"] = value
        status_label.config(text=text)

    def download_thread():
        ydl_opts = {
            'format': f'{video_format}+bestaudio/best',
            'merge_output_format': selected_format.lower(),
            'progress_hooks': [progress_hook],
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            messagebox.showinfo("Success", f"Download completed successfully!\nFile saved in: {output_path}")
            status_label.config(text="Ready! You can paste another link.", fg="green")
        except Exception as e:
            messagebox.showerror("Error", f"Download failed.\nDetails: {str(e)}")
            status_label.config(text="Download error", fg="red")
        finally:
            download_btn.config(state=tk.NORMAL)

    threading.Thread(target=download_thread, daemon=True).start()

# --- Tkinter GUI Setup ---
root = tk.Tk()
root.title("Advanced Video Downloader")
root.geometry("500x340")
root.resizable(False, False)

# 1. Link Input Section
tk.Label(root, text="Paste YouTube Link:", font=("Arial", 10, "bold")).pack(pady=(15, 2))

link_frame = tk.Frame(root)
link_frame.pack(pady=5)

url_entry = tk.Entry(link_frame, width=42, font=("Arial", 10))
url_entry.pack(side=tk.LEFT, padx=(0, 5))
url_entry.focus()

paste_btn = tk.Button(link_frame, text="Paste", font=("Arial", 8, "bold"), bg="#E0E0E0", command=paste_from_clipboard)
paste_btn.pack(side=tk.LEFT)

ttk.Separator(root, orient='horizontal').pack(fill='x', padx=20, pady=10)

# 2. Options Grid
options_frame = tk.Frame(root)
options_frame.pack(pady=5)

tk.Label(options_frame, text="Resolution:", font=("Arial", 9)).grid(row=0, column=0, padx=10, sticky="w")
res_combo = ttk.Combobox(options_frame, values=["Best Available", "4K (2160p)", "1080p FullHD", "720p HD", "480p"], width=15, state="readonly")
res_combo.set("1080p FullHD")
res_combo.grid(row=0, column=1, padx=10, pady=5)

tk.Label(options_frame, text="Container Format:", font=("Arial", 9)).grid(row=1, column=0, padx=10, sticky="w")
format_combo = ttk.Combobox(options_frame, values=["MP4", "MKV"], width=15, state="readonly")
format_combo.set("MP4")
format_combo.grid(row=1, column=1, padx=10, pady=5)

tk.Label(options_frame, text="Save Location:", font=("Arial", 9)).grid(row=2, column=0, padx=10, sticky="w")
browse_btn = tk.Button(options_frame, text="Browse...", command=browse_folder, font=("Arial", 8))
browse_btn.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

folder_label = tk.Label(root, text=f"Save to: {output_path}", font=("Arial", 8, "italic"), fg="gray")
folder_label.pack(pady=2)

ttk.Separator(root, orient='horizontal').pack(fill='x', padx=20, pady=10)

# 3. Action Button
download_btn = tk.Button(root, text="DOWNLOAD VIDEO", font=("Arial", 11, "bold"), bg="#2196F3", fg="white", padx=20, pady=5, command=download_video)
download_btn.pack(pady=5)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=5)

status_label = tk.Label(root, text="Configure options and click Download", font=("Arial", 9, "italic"), fg="gray")
status_label.pack(pady=2)

root.mainloop()