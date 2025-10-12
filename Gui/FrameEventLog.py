import tkinter as tk
from tkinter import ttk

from Gui.AnalysisLogger import AnalysisLogger


class FrameEventLog(AnalysisLogger):

    def __init__(self, main_frame):

        if main_frame is None:
            raise ValueError("root cannot be None")
        if not isinstance(main_frame, ttk.Frame):
            raise TypeError(f"Expected '{type(ttk.Frame).__name__}', got {type(main_frame).__name__}")

        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        frame = ttk.LabelFrame(main_frame, text="Output", padding=(10, 5, 0, 10))
        frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        self._log_text = tk.Text(frame, wrap="word", width=40, height=30, state="disabled")

        scrollbar = ttk.Scrollbar(frame, command=self._log_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self._log_text.config(yscrollcommand=scrollbar.set)
        self._log_text.grid(row=0, column=0, sticky="nsew")


    def log(self, message: str):
        self._log_text.config(state="normal")
        self._log_text.insert("end", f"{message}\n")
        self._log_text.see("end")  # Auto-scroll to the bottom
        self._log_text.config(state="disabled")

