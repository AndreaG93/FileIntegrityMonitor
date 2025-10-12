import tkinter as tk
from tkinter import ttk, Frame
from tkinter.ttk import Notebook

from Gui.FrameAnalyzer import FrameAnalyzer
from Gui.FrameEventLog import FrameEventLog


class MainWindow:

    def __init__(self):

        self._root = tk.Tk()
        self._root.title("File Integrity Monitor")
        self._root.configure(padx=0, pady=0)

        # Setup main...
        self._main_frame = ttk.Frame(self._root)
        self._main_frame.pack(expand=True, fill="both")
        self._main_frame.columnconfigure(0, weight=1, minsize=400)  # Analyzer Frame
        self._main_frame.columnconfigure(1, weight=2, minsize=400)
        self._main_frame.grid_rowconfigure(0, weight=1, minsize=300)

        # 'Analyzer Frame'
        self._frame_analyzer = ttk.Frame(self._main_frame, padding=10)
        self._frame_analyzer.grid(row=0, column=0, sticky="nsew")

        # 'Event Log Frame'
        self._frame_event_log = ttk.Frame(self._main_frame, padding=10)
        self._frame_event_log.grid(row=0, column=1, sticky="nsew")

        # Setup...
        FrameAnalyzer(self._frame_analyzer, FrameEventLog(self._frame_event_log))

        self._root.mainloop()

# Run the app
if __name__ == "__main__":
    app = MainWindow()
