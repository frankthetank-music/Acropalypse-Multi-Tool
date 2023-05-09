from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter.filedialog import askopenfilename, askdirectory, asksaveasfilename
import sv_ttk

import os, sys, subprocess
import time
from threading import Thread
import pathlib

from PIL import Image, ImageTk
from acropalypse import Acropalypse

from gif_lib import acropalypse_gif

import platform
import tempfile
import ctypes
import shutil 


# Get the name of the host operating system
os_name = platform.system()
tempdir = tempfile.gettempdir()

class DetectTool(Frame):

	def open_image(self, event):
		# Get the selected item
		selected_item = self.listbox.get(self.listbox.curselection())
		# Open the image using the default Windows image viewer
		if os_name == "Windows":
			os.startfile(selected_item)
		else:
			opener = "open" if sys.platform == "darwin" else "xdg-open"
			subprocess.call([opener, selected_item])

	def on_resize(self, event):
		self.update_wraplength(self.lower_frame)

	def update_wraplength(self, frame):
		wraplength = self.calculate_wraplength(frame)

	def calculate_wraplength(self, frame):
		return frame.winfo_width() * 0.8
	
	def on_detect(self):
		search_dir = askdirectory(parent=self)
		if search_dir:
			for filename in os.listdir(search_dir):
				search_file = os.path.join(search_dir, filename)
				if os.path.isfile(search_file):
					if pathlib.Path(search_file).suffix == ".gif":
						response = acropalypse_gif.detect(search_file)
						if response:
							if not f"{search_file}" in self.listbox.get(0, "end"):
								self.listbox.insert(END, f"{search_file}")
					elif pathlib.Path(search_file).suffix == ".png":
						response = self.acropalypse_Instance.detect_png(search_file)
						if response:
							if not f"{search_file}" in self.listbox.get(0, "end"):
								self.listbox.insert(END, f"{search_file}")
			self.listbox.pack(side="left", fill="both", expand=True)

	def __init__(self, master, frame):
		super().__init__(master)
		self.acropalypse_Instance = Acropalypse()
		self.frame = frame
		self.master = master
		self.pack(fill=BOTH, expand=1)

		# Calculate the height for the two sections
		upper_height = int(frame.root_height * 0.10)
		lower_height = int(frame.root_height * 0.90)
		window_width = int(frame.root_width)

		# Create the upper section
		upper_frame = Frame(self, height=upper_height, bg="grey")
		upper_frame.grid(row=0, column=0, sticky="nsew")

		# Create a canvas in the upper section
		canvas = Canvas(upper_frame, height=upper_height, bg="grey", highlightthickness=0)
		canvas.pack(fill="both", expand=True)

		# Create and center the button in the upper section
		center_button = ttk.Button(upper_frame, text="Select Folder", command=self.on_detect)
		canvas.create_window(window_width // 2, upper_height // 2, window=center_button, anchor="center")

		# Create the lower section
		lower_frame = Frame(self, height=lower_height)
		lower_frame.grid(row=1, column=0, sticky="nsew")

		# Create a scrollable list of strings in the lower section
		scrollbar = ttk.Scrollbar(lower_frame)
		scrollbar.pack(side="right", fill="y")

		# Add a title for the listbox
		listbox_title = Label(lower_frame, text="Potentially vulnerable Images", font=("Helvetica", 14))
		listbox_title.pack(pady=(20, 20))

		listbox = Listbox(lower_frame, yscrollcommand=scrollbar.set, font=("Helvetica", 10))
		self.listbox = listbox
		scrollbar.config(command=listbox.yview)

		# Configure grid weights to allow for resizing
		self.grid_rowconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=4)
		self.grid_columnconfigure(0, weight=1)

		self.lower_frame = lower_frame
		self.upper_frame = upper_frame

		self.master.bind('<Configure>', self.on_resize)
				
		# Bind the double-click event to the listbox
		listbox.bind("<Double-Button-1>", self.open_image)

class RestoreTool(Frame):
	def __init__(self, master, frame):
		super().__init__(master)
		self.frame = frame
		self.master = master
		self.rgb_alpha = False
		self.pack(fill=BOTH, expand=1)
		
		self.acropalypse_Instance = Acropalypse()
		self.cropped_image_file = None
		self.reconstructing=False
		left_frame_width = int(frame.root_width * 0.4)
		middle_frame_width = int(frame.root_width * 0.2)
		right_frame_width = int(frame.root_width * 0.4)
		frame_height = int(frame.root_height)

		# GUI-Elemente erstellen
		left_frame = Frame(self, width=left_frame_width, height=frame_height, bg='grey')
		left_frame.grid(row=0, column=0, sticky="ns")
		left_frame.grid_propagate(False)
		left_frame.pack_propagate(0)
		
		middle_frame = Frame(self, width=middle_frame_width, height=frame_height, relief='sunken')
		middle_frame.grid(row=0, column=1, sticky="ns", padx=(middle_frame_width * 0.1, middle_frame_width * 0.1))
		# Make the frame sticky for every case
        # Make the frame sticky for every case
		middle_frame.grid_rowconfigure(0, weight=1)
		middle_frame.grid_rowconfigure(1, weight=1)
		middle_frame.grid_rowconfigure(2, weight=1)
		middle_frame.grid_rowconfigure(3, weight=1)
		middle_frame.grid_rowconfigure(4, weight=1)
		middle_frame.grid_rowconfigure(5, weight=1)
		middle_frame.grid_rowconfigure(6, weight=1)
		middle_frame.grid_rowconfigure(7, weight=1)
		middle_frame.grid_rowconfigure(8, weight=1)
		middle_frame.grid_columnconfigure(0, weight=1)
		middle_frame.grid_columnconfigure(1, weight=1)
		middle_frame.grid_columnconfigure(2, weight=1)
		middle_frame.grid_propagate(False)
		middle_frame.pack_propagate(0)
		
		right_frame = Frame(self, width=right_frame_width, height=frame_height, bg='grey')
		right_frame.grid(row=0, column=2, sticky="ns")
		right_frame.grid_propagate(False)
		right_frame.pack_propagate(0)
		
		self.columnconfigure(0, weight=1)  # Change weight
		self.columnconfigure(1, weight=1)  # Change weight
		self.columnconfigure(2, weight=1)  # Change weight
		self.rowconfigure(0, weight=1)
		
		self.left_label = Label(left_frame, bg='grey')
		self.left_label.grid(row=0, column=0, sticky="ns")
		self.right_label = Label(right_frame, bg='grey')
		self.right_label.grid(row=0, column=0, sticky="ns")

		# Initialize Image Variable
		self.right_label.image = None
		
		padding_top = int(frame_height * 0.08)
		self.button = ttk.Button(middle_frame, text="Select Image", command=self.load_image).grid(row=0, column=1, pady=(padding_top, 0), sticky='ns')
		
		self.label_image_path = ttk.Label(middle_frame, text="No Image selected", anchor='center', justify='center')
		self.label_image_path.grid(row=1, column=1, pady=(int(frame_height * 0.01), 0), padx=(middle_frame_width * 0.1, middle_frame_width * 0.1), sticky='ns')
		self.label_image_path.config(wraplength=self.calculate_wraplength(middle_frame), anchor='center', justify='center')
		
		# Drop-Down Menü Optionen
		options = ["-- select option --", "Custom RGBA", "Custom RGB", "Windows 11 Snipping Tool", "Google Pixel 3", "Google Pixel 3 XL", "Google Pixel 3a", "Google Pixel 3a XL", "Google Pixel 4", "Google Pixel 4 XL", "Google Pixel 4a", "Google Pixel 5", "Google Pixel 5a", "Google Pixel 6", "Google Pixel 6 Pro", "Google Pixel 6a", "Google Pixel 7", "Google Pixel 7 Pro"]
		menu_width = len(max(options, key=len))

		# Standardwert für das Drop-Down Menü
		self.dropdown = StringVar()
		self.dropdown.set(options[0])

		# Drop-Down Menü erstellen
		drop_down_menu = ttk.OptionMenu(middle_frame, self.dropdown, *options, command=self.on_option_changed)
		drop_down_menu.config(width=menu_width)
		drop_down_menu.grid(row=2, column=1, pady=int(frame_height*0.03), sticky='ns')

		self.width_label = ttk.Label(middle_frame, text="Original Width:").grid(row=3, column=1, pady=int(frame_height*0.003))
		self.width_entry = ttk.Entry(middle_frame)
		self.width_entry.grid(row=4, column=1, pady=int(frame_height*0.01), sticky='ns')  # Add this line to place the Entry Box in the grid layout
		self.width_entry.configure(justify='center')  # Add this line to center the text in the Entry

		self.height_label = ttk.Label(middle_frame, text="Original Height:").grid(row=5, column=1, pady=int(frame_height*0.003))
		self.height_entry = ttk.Entry(middle_frame)
		self.height_entry.grid(row=6, column=1, pady=int(frame_height*0.01), sticky='ns')
		self.height_entry.configure(justify='center')  # Add this line to center the text in the Entry


		self.button_acrop = ttk.Button(middle_frame, text="Acropalypse Now!", command=self.on_button, style='my.TButton').grid(row=7, column=1, pady=int(frame_height*0.01), sticky='ns')
		self.label_log = Label(middle_frame, text="Please select an image", anchor='center', justify='center')
		self.label_log.grid(row=8, column=1, pady=int(frame_height*0.06), sticky='ns')
		self.label_image_path.config(wraplength=self.calculate_wraplength(middle_frame))
		self.label_log.config(wraplength=self.calculate_wraplength(middle_frame), anchor='center', justify='center')
		self.on_option_changed()

		self.middle_frame = middle_frame
		self.right_frame = right_frame
		self.left_frame = left_frame

		# Add save button
		self.save_button = ttk.Button(self.right_frame, text="Save Image", command=self.save_image)
		self.save_button.place(relx=1.0, rely=0.0, x=-5, y=5, anchor="ne")
		self.reconstructing = False

		self.master.bind('<Configure>', self.on_resize)

	def on_resize(self, event):
		self.update_wraplength(self.middle_frame)

	def update_wraplength(self, frame):
		wraplength = self.calculate_wraplength(frame)
		self.label_image_path.config(wraplength=wraplength)
		self.label_log.config(wraplength=wraplength)

	def calculate_wraplength(self, frame):
		return frame.winfo_width() * 0.8
	
	def on_option_changed(self, *args):
		"""Diese Funktion wird aufgerufen, wenn die ausgewählte Option im Drop-Down Menü geändert wird."""
		self.selected_option = self.dropdown.get()
		self.rgb_alpha = False
		if self.selected_option == "-- select screenshot program --":
			self.width_entry.delete(0,END)
			self.width_entry.insert(0, "1920")
			self.height_entry.delete(0,END)
			self.height_entry.insert(0, "1080")
		elif self.selected_option == "Windows 11 Snipping Tool":
			self.rgb_alpha = True
			self.width_entry.delete(0,END)
			self.width_entry.insert(0, "1920")
			self.height_entry.delete(0,END)
			self.height_entry.insert(0, "1080")
		elif self.selected_option == "Custom RGBA":
			self.rgb_alpha = True
			self.width_entry.delete(0,END)
			self.width_entry.insert(0, "0")
			self.height_entry.delete(0,END)
			self.height_entry.insert(0, "0")
		elif self.selected_option == "Custom RGB":
			self.width_entry.delete(0,END)
			self.width_entry.insert(0, "0")
			self.height_entry.delete(0,END)
			self.height_entry.insert(0, "0")
		elif self.selected_option == "Google Pixel 3" or self.selected_option == "Google Pixel 3a XL":
			self.width_entry.delete(0,END)
			self.width_entry.insert(0, "1080")
			self.height_entry.delete(0,END)
			self.height_entry.insert(0, "2160")
		elif self.selected_option == "Google Pixel 3 XL":
			self.width_entry.delete(0,END)
			self.width_entry.insert(0, "1440")
			self.height_entry.delete(0,END)
			self.height_entry.insert(0, "2960")
		elif self.selected_option == "Google Pixel 3a":
			self.width_entry.delete(0,END)
			self.width_entry.insert(0, "1080")
			self.height_entry.delete(0,END)
			self.height_entry.insert(0, "2220")
		elif self.selected_option == "Google Pixel 4":
			self.width_entry.delete(0,END)
			self.width_entry.insert(0, "1080")
			self.height_entry.delete(0,END)
			self.height_entry.insert(0, "2280")
		elif self.selected_option == "Google Pixel 4 XL":
			self.width_entry.delete(0,END)
			self.width_entry.insert(0, "1440")
			self.height_entry.delete(0,END)
			self.height_entry.insert(0, "3040")
		elif self.selected_option == "Google Pixel 4a" or self.selected_option =="Google Pixel 5":
			self.width_entry.delete(0,END)
			self.width_entry.insert(0, "1080")
			self.height_entry.delete(0,END)
			self.height_entry.insert(0, "2340")
		elif self.selected_option == "Google Pixel 5a" or self.selected_option =="Google Pixel 6" or self.selected_option =="Google Pixel 6a" or self.selected_option =="Google Pixel 7":
			self.width_entry.delete(0,END)
			self.width_entry.insert(0, "1080")
			self.height_entry.delete(0,END)
			self.height_entry.insert(0, "2400")
		elif self.selected_option == "Google Pixel 6 Pro" or self.selected_option =="Google Pixel 7 Pro":
			self.width_entry.delete(0,END)
			self.width_entry.insert(0, "1440")
			self.height_entry.delete(0,END)
			self.height_entry.insert(0, "3120")
			
		
	def load_image(self):
		# Dialogfenster zum Auswählen einer Datei öffnen
		self.cropped_image_file = askopenfilename(filetypes=[("Images", "*.png *.gif")], parent=self)
				
		# Bild laden und in beide Labels einfügen
		print(self.cropped_image_file)
		if self.cropped_image_file:
			image = Image.open(self.cropped_image_file)
			
			# Größe des Bildes entsprechend anpassen
			max_width = round(self.left_frame.winfo_width() * 0.98)
			max_height = round(self.left_frame.winfo_height() * 0.98)
			width, height = image.size
			if width > max_width:
				new_height = int(height * max_width / width)
				image = image.resize((max_width, new_height))
				width, height = image.size
			if height > max_height:
				new_width = int(width * max_height / height)
				image = image.resize((new_width, max_height))
			
			photo = ImageTk.PhotoImage(image)
			self.left_label.config(image=photo)
			self.left_label.image = photo
			self.left_label.pack()
		
			self.right_label.config(image='')
			# Extract the file name from the path
			file_name = os.path.basename(self.cropped_image_file)
			self.label_image_path.config(text=file_name, anchor='center', justify='center')
			self.label_log.config(text="Select picture mode and press button to reconstruct", anchor='center', justify='center')
			
		
	def on_button(self):
		if not self.reconstructing:
			if not self.cropped_image_file:
				self.label_log.config(text="Please select an image first.", anchor='center', justify='center')
				return
			self.label_log.config(text="Reconstructing image, please wait...", anchor='center', justify='center')
			t= Thread(target=self.acrop_now)
			t.start()
			self.reconstructing=True
		
	def acrop_now(self):
		if pathlib.Path(self.cropped_image_file).suffix == ".gif":
			try:
				acropalypse_gif.restore(self.cropped_image_file, os.path.join(tempdir, 'restored.gif'),int(self.width_entry.get() or 1920), int(self.height_entry.get() or 1080))
			except Exception as e:
				self.label_log.config(text=f"Error reconstructing the image: {e}", anchor='center', justify='center')
				self.reconstructing=False
				return
		elif pathlib.Path(self.cropped_image_file).suffix == ".png":
			try:
				print(self.rgb_alpha)
				self.acropalypse_Instance.reconstruct_image(self.cropped_image_file, int(self.width_entry.get() or 1920), int(self.height_entry.get() or 1080), self.rgb_alpha)
			except Exception as e:
				self.label_log.config(text=f"Error reconstructing the image: {e}", anchor='center', justify='center')
				self.reconstructing=False
				return
		try:
			if pathlib.Path(self.cropped_image_file).suffix == ".gif":
				image = Image.open(os.path.join(tempdir, 'restored.gif'))
			elif pathlib.Path(self.cropped_image_file).suffix == ".png":
				image = Image.open(os.path.join(tempdir, 'restored.png'))
				
			# Größe des Bildes entsprechend anpassen
			max_width = round(self.left_frame.winfo_width() * 0.98)
			max_height = round(self.left_frame.winfo_height() * 0.98)
			width, height = image.size
			if width > max_width:
				new_height = int(height * max_width / width)
				image = image.resize((max_width, new_height))
				width, height = image.size
			if height > max_height:
				new_width = int(width * max_height / height)
				image = image.resize((new_width, max_height))
			
			photo = ImageTk.PhotoImage(image)
			self.right_label.config(image=photo)
			self.right_label.image = photo
			self.right_label.pack()
			self.label_log.config(text=f"Reconstructed the image successfully", anchor='center', justify='center')
			self.reconstructing=False
		except Exception:
			self.label_log.config(text=f"Error reconstructing the image! \nAre you using the right mode and resolution?", anchor='center', justify='center')
			self.reconstructing=False
		
	def save_image(self):
	# Check if the image is reconstructed
		if self.right_label.image:
			# Open save file dialog
			file_path = asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png"), ("GIF Files", "*.gif")], parent=self)

			if file_path:
				# Save the image
				if pathlib.Path(self.cropped_image_file).suffix == ".gif":
					restored_image_path = os.path.join(tempdir, 'restored.gif')
				elif pathlib.Path(self.cropped_image_file).suffix == ".png":
					restored_image_path = os.path.join(tempdir, 'restored.png')

				shutil.copy2(restored_image_path, file_path)
				self.label_log.config(text="Image saved successfully!", anchor='center', justify='center')
		else:
			self.label_log.config(text="No image to save, reconstruct an image first.", anchor='center', justify='center')

def dark_title_bar(window):
    """
    MORE INFO:
    https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/ne-dwmapi-dwmwindowattribute
    """
    window.update()
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
    get_parent = ctypes.windll.user32.GetParent
    hwnd = get_parent(window.winfo_id())
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = 2
    value = ctypes.c_int(value)
    set_window_attribute(hwnd, rendering_policy, ctypes.byref(value),
                         ctypes.sizeof(value))

def maximize(frame):
#Optimize Window Scaling
	try:
		if os_name == 'Linux':
			frame.attributes('-zoomed', True)
		if os_name == 'Windows':
			frame.state('zoomed')
	except:
		pass

def optimize_scaling(frame):
	try:
		if os_name == 'Linux':
			pass
		if os_name == 'Windows':
			ctypes.windll.shcore.SetProcessDpiAwareness(2)
			dark_title_bar(frame)
		frame.tk.call('tk', 'scaling', 2.0)
	except:
		pass

def display_initial_window():
	initial_window = Tk()
	initial_window.title("Select Tool")

	def open_restore_gui():
		restore = Toplevel()
		restore.title('Acropalypse Multi Tool')
		restore.option_add('*foreground', 'black')  # set all tk widgets' foreground to black

		# Fenstergröße setzen
		restore.root_width = round(restore.winfo_screenwidth() * 0.98)
		restore.root_height = round(restore.winfo_screenheight() *0.96)
		min_width = int(restore.root_width * 0.75)
		min_height = int(restore.root_height * 0.75)
		restore.geometry("{}x{}".format(restore.root_width, restore.root_height))
		restore.minsize(min_width, min_height)

		#optimize Scaling
		optimize_scaling(restore)
		maximize(restore)

		app = RestoreTool(restore, restore)
		app.pack()
		sv_ttk.set_theme("dark")
		style = ttk.Style()
		button_text = "Acropalypse Now!"
		button_font = font.nametofont("TkDefaultFont")
		button_width = button_font.measure(button_text) // button_font.measure("0") + 6
		style.configure("TButton", width=button_width, anchor='center')
		style.configure('my.TButton', foreground='white', background='red')

		restore.mainloop()
	
	def open_detect_gui():
		detect = Toplevel()
		detect.title('Acropalypse Multi Tool')
		detect.option_add('*foreground', 'black')  # set all tk widgets' foreground to black

		# Fenstergröße setzen
		detect.root_width = round(detect.winfo_screenwidth() * 0.76)
		detect.root_height = round(detect.winfo_screenheight() *0.76)
		min_width = int(detect.root_width * 0.74)
		min_height = int(detect.root_height * 0.74)
		detect.geometry("{}x{}".format(detect.root_width, detect.root_height))
		detect.minsize(min_width, min_height)

		#optimize Scaling
		optimize_scaling(detect)

		app = DetectTool(detect, detect)
		app.pack()
		sv_ttk.set_theme("dark")

		detect.mainloop()

	# Fenstergröße setzen
	initial_window.root_width = round(initial_window.winfo_screenwidth() * 0.28)
	initial_window.root_height = round(initial_window.winfo_screenheight() *0.15)
	min_width = int(initial_window.root_width * 0.95)
	min_height = int(initial_window.root_height * 0.95)
	initial_window.geometry("{}x{}".format(initial_window.root_width, initial_window.root_height))
	initial_window.minsize(min_width, min_height)

	
	# Create a canvas for buttons
	canvas = Canvas(initial_window, height=initial_window.root_height, highlightthickness=0)
	canvas.pack(fill="both", expand=True)

	button_detection = ttk.Button(initial_window, text="Detection Tool", style="TButton", command=open_detect_gui)
	button_restoring = ttk.Button(initial_window, text="Restoring Tool", style="TButton", command=open_restore_gui)

	# Calculate the center coordinates for each button
	button_detection_x = initial_window.root_width  // 2 - button_detection.winfo_reqwidth()
	button_restoring_x = initial_window.root_width  // 2 + button_restoring.winfo_reqwidth()
	button_y = initial_window.root_height // 2

	canvas.create_window(button_detection_x, button_y, window=button_detection, anchor="center")
	canvas.create_window(button_restoring_x, button_y, window=button_restoring, anchor="center")

	sv_ttk.set_theme("dark")
	optimize_scaling(initial_window)
	initial_window.mainloop()

if __name__ == "__main__":
    display_initial_window()