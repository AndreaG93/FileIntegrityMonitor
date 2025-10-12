import os
import tkinter as tk
from tkinter import filedialog

def select_folder():
    """
    Opens a GUI dialog for the user to select a folder.

    :return: The full path of the selected folder as a string.
             Returns an empty string if the user cancels.
    """

    root = tk.Tk()
    root.withdraw()

    return filedialog.askdirectory(title="Select folder to analyze")

def select_output_file():
    """
    Opens a GUI dialog for the user to choose where to save the output file.

    :return: Full path to the file selected for saving.
             Returns an empty string if the user cancels.
    """

    # Create a hidden root window
    root = tk.Tk()
    root.withdraw()

    # Open the save file dialog
    return filedialog.asksaveasfilename(
        title="Select output file location",
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )

def select_hash_file():
    """
    Opens a GUI dialog for the user to select a hash file.

    :return: Full path to the selected file as a string.
             Returns an empty string if the user cancels.
    """

    # Create a hidden root window
    root = tk.Tk()
    root.withdraw()

    # Open the file selection dialog
    return filedialog.askopenfilename(
        title="Select hash file",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )

def count_files(directory):
    """
    Counts the number of files in a directory.

    :param directory: The directory to count files from.
    :return: The number of files in the directory.
    """

    output = 0
    for root, dirs, files in os.walk(directory):
        output += len(files)

    return output