##############################################################################################################################################################################################


import time
from pynput.keyboard import Key, Listener, Controller
from PIL import ImageGrab
import numpy as np
import threading
import tkinter as tk

__version__ = 'v2.4'
__author__ = 'siwel'


##############################################################################################################################################################################################


# Controller for keyboard
keyboard = Controller()

# Define the running and future variables
running = False
counter = 0
max_count = 5000
script_thread = None

# Toggle keys
toggle_key = Key.insert
exit_key = Key.end

# Lookup for the keys we expect to be pressed
lookup_key = {
    'space': Key.space,
    'q': 'q'
}

# Colour list for the RGB check
colour_list = [
    (255, 0, 0),
    (150, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (0, 0, 0),
    (255, 255, 255),
    (150, 150, 150)
]


##############################################################################################################################################################################################


# Find the closest match for a color out of a list of colors
def closest(colors, color):
    colors = np.array(colors)
    color = np.array(color)
    distances = np.sqrt(np.sum((colors - color)**2, axis=1))
    index_of_smallest = np.argmin(distances)
    return tuple(colors[index_of_smallest])


# Get the pixel color
def get_pixel_colour(x, y):
    screenshot = ImageGrab.grab(bbox=(x, y, x+1, y+1))
    colour = screenshot.getpixel((0, 0))
    colour = tuple(closest(colour_list, colour))
    return colour


# Simulate a key press
def press_key(key, delay_1=1, delay_2=0.1, delay_3=1):
    key = lookup_key.get(key, key)
    time.sleep(delay_1)  # initial delay
    keyboard.press(key)  # key down
    time.sleep(delay_2)
    keyboard.release(key)  # key up
    time.sleep(delay_3)  # cooldown


# Define the script function to toggle (1.6s total)
def my_script():
    global running, counter
    while running:
        # Check if dead
        colour = get_pixel_colour(868, 30)
        if colour == (255, 0, 0):
            app.update_status(app.alive_status, 'Alive: ', 'False')
            press_key('space', 0.1, 0.05, 0.1)
        else:
            app.update_status(app.alive_status, 'Alive: ', 'True')

        # Throw grenade
        press_key('q', 0.1, 0.05, 0.3)

        # Counter reached
        counter += 1
        if counter % 25 == 0:
            print(f'Counter: {counter}')
        if counter == max_count:
            running = False
            counter = 0

        time.sleep(0.1)  # Small sleep to reduce CPU usage

    app.update_status(app.toggle_status, 'Toggle: ', 'False')


##############################################################################################################################################################################################


# Define the function to toggle the script
def toggle_script():
    global running, script_thread
    if running:
        running = False
        if script_thread:
            script_thread.join()
        app.update_status(app.toggle_status, 'Toggle: ', 'False')
    else:
        running = True
        app.update_status(app.toggle_status, 'Toggle: ', 'True')
        script_thread = threading.Thread(target=my_script)
        script_thread.start()


# Handle key presses
def on_press(key):
    if key == toggle_key:
        toggle_script()
    elif key == exit_key:
        print('Exiting program.')
        stop_script()
        root.quit()
        return False  # Stop listener


# Define a function to stop the script
def stop_script():
    global running
    running = False
    if script_thread:
        script_thread.join()
    app.close_window()


##############################################################################################################################################################################################


# info window
class App:
    # config settings
    app_name = f'EasyAFK {__version__}'

    # style settings
    clr_bg = '#111'
    clr_tx = '#fff'
    clr_bd = '#fa0'
    clr_True = '#0f0'
    clr_False=  '#f00'

    # font choice
    fnt_tb = ('Fixedsys', 12, 'bold')
    fn_main = ('Terminal', 8, 'bold')
    fnt_close = ('Fixedsys', 8)

    def __init__(self, root):
        """
        Configuration section
        - Configure the root settings
        - Create and set the stylings
        - Create the custom titlebar
        """


        # config root options
        self.root = root
        root.title(self.app_name)
        root.resizable(False, False)
        root.overrideredirect(1)
        root.configure(bg=self.clr_bg)
        root.attributes('-topmost', True, '-alpha', 0.7, '-fullscreen', False)


        # stylesheet
        styles = {
            # fonts
            '*Label.Font': self.fn_main,

            # background colour
            '*Text.Background': self.clr_bg,
            '*Label.Background': self.clr_bg,
            '*Frame.Background': self.clr_bg,
            '*Button.Background': self.clr_bg,

            # foreground colour#
            '*Text.Foreground': self.clr_tx,
            '*Label.Foreground': self.clr_tx,
            '*Button.Foreground': self.clr_tx,

            # button stuff
            '*Button.activeBackground': '#D9534F',
            '*Button.activeForeground': '#f00'
        }
        for widget_option, style in styles.items():
            root.option_add(widget_option, style)




        """
        Window content section
        - Sets up the window border
        - Creates the labels for toggle status and dead status
        - Creates the instruction label
        - Sets status labels as instance variables so that I can access them as object attributes
        """

        # coloured border
        border = tk.Frame(root, padx=2, pady=2, bg=self.clr_bd) # explicitly set background here
        border.pack(expand=True, fill='both')

        # frame inside border to give the border effect
        content = tk.Frame(border)
        content.pack(expand=True, fill='both')


        # custom titlebar
        tb_frame = tk.Frame(content, relief='flat', height=2) #, bd=0, highlightthickness=0
        tb_frame.pack(side='top', fill='x')

        # window title
        tb_title = tk.Label(tb_frame, text=self.app_name, font=self.fnt_tb)
        tb_title.pack(side='left', pady=2)

        # close button
        close_button = tk.Button(
            tb_frame, text='🞪', font=self.fnt_close,
            relief='flat', borderwidth=0,
            command=self.close_window)
        close_button.pack(side='right', padx=1, pady=1)

        # assign the dragging ability to these widgets
        for widget in [tb_frame, tb_title]:
            widget.bind('<Button-1>', self.on_click)
            widget.bind('<B1-Motion>', self.on_drag)


        # create labels for status and dead status
        status_frame = tk.Frame(content)
        status_frame.pack(expand=True, fill='both', pady=3)

        toggle_status = tk.Text(status_frame, height=1, width=20, borderwidth=0)
        toggle_status.pack(anchor='w')
        self.update_status(toggle_status, 'Toggle: ', 'False')

        alive_status = tk.Text(status_frame, height=1, width=20, borderwidth=0)
        alive_status.pack(anchor='w')
        self.update_status(alive_status, 'Alive: ', 'True')


        # instruction labels
        instruction_frame = tk.Frame(content)
        instruction_frame.pack(expand=True, fill='both', pady=3)
        for instruction in ['Toggle: `Insert`', 'Close: `End`']:
            label = tk.Label(instruction_frame, text=instruction)
            label.pack(anchor='w')


        # setting as self to access outside of the app object
        self.toggle_status = toggle_status
        self.alive_status = alive_status




    # on titlebar drag
    def on_drag(self, event):
        """update the geometry attribute (specifically the offset part) to move the window by the current window x, y to the x y offset"""
        x = self.root.winfo_pointerx() - offset_x
        y = self.root.winfo_pointery() - offset_y
        self.root.geometry(f'+{x}+{y}')


    # on titlebar click
    def on_click(self, event):
        """get the current x, y offset and set to global variables"""
        global offset_x, offset_y
        offset_x = event.x
        offset_y = event.y


    # close the window
    def close_window(self):
        self.root.destroy()


    # update status
    def update_status(self, widget, status, value):
        # enable widget to allow changes
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", tk.END)

        # insert new text
        widget.insert(tk.END, status)
        widget.insert(tk.END, value)
        
        # set status label
        status_len = f'1.{len(status)}'
        widget.tag_add('status', '1.0', status_len)
        widget.tag_config('status', foreground=self.clr_tx, background=self.clr_bg)

        # set the value label
        value_len = f'1.{len(status) + len(value)}'
        widget.tag_add('value', status_len, value_len)
        if value == 'True':
            widget.tag_config('value', foreground=self.clr_True, background=self.clr_bg)
        elif value == 'False':
            widget.tag_config('value', foreground=self.clr_False, background=self.clr_bg)
        
        # disable widget to set the changes
        widget.config(state=tk.DISABLED)


##############################################################################################################################################################################################


# Main function to create the Tkinter window and listen for the toggle key
if __name__ == '__main__':
    # create the main window
    root = tk.Tk()
    app = App(root)

    # Start listening for key presses
    listener_thread = threading.Thread(target=lambda: Listener(on_press=on_press).start())
    listener_thread.daemon = True  # Ensure the listener thread exits with the main program
    listener_thread.start()

    # start the Tkinter main loop
    root.mainloop()