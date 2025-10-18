import threading
import time

from Gui.AnalysisObserver import AnalysisObserver
import tkinter as tk
from tkinter import ttk, messagebox

from Helpers import HelperUserInterface
from Helpers.HelperAnalyzer import analyze_directory, verify_hashes
from Helpers.HelperUserInterface import select_hash_file


class FrameAnalyzer(AnalysisObserver):

    def on_file_completed(self, file_path: str) -> None:
       self._file_analyzed_count += 1
       self._refresh_ui()

    def __init__(self, root, logger):

        if root is None:
            raise ValueError("root cannot be None")
        elif logger is None:
            raise ValueError("logger cannot be None")
        elif not isinstance(root, ttk.Frame):
            raise TypeError(f"Expected 'ttk.Frame', got {type(root).__name__}")

        self._root = root

        # Internal state
        self._logger = logger
        self._thread = None
        self._file_count = 0
        self._file_analyzed_count = 0
        self._selected_directory = ""
        self._selected_file = ""
        self._is_analysis_mode_selected =  tk.BooleanVar(value=True)

        # UI setup
        self._create_task_selector()
        self._create_file_and_directory_selectors()
        self._create_progress_section()
        self._create_action_buttons()

        # Configure layout behavior
        self._root.grid_columnconfigure(0, weight=1)
        self._root.grid_rowconfigure(2, weight=1)

        self._refresh_ui()

    def _create_task_selector(self):
        """
        Create radio buttons to select between 'Analyze' and 'Verify' tasks.

        :return: None
        """

        # Analysis Radio Button...
        frame = ttk.LabelFrame(self._root, text="Analysis Type", padding=(10, 5, 0, 10))
        frame.grid(row=0, column=0, padx=5, pady=5, sticky="nesw")

        self._analyze_radio = tk.Radiobutton(frame,
                                             text="Analyze",
                                             variable=self._is_analysis_mode_selected,
                                             value=True,
                                             command=self._on_analysis_mode_selected_change)

        self._analyze_radio.grid(row=0, sticky="w", pady=5)

        # Verify Radio Button...
        tk.Label(frame, text="Generate SHA512 hashes for all files and save the results to an output file.",
                 font=("TkDefaultFont", 8)).grid(row=1, column=0, sticky="w", padx=20)

        self._verify_radio = tk.Radiobutton(frame,
                                            text="Verify",
                                            variable=self._is_analysis_mode_selected,
                                            value=False,
                                            command=self._on_analysis_mode_selected_change)

        self._verify_radio.grid(row=2, sticky="w", pady=5)

        tk.Label(frame, text="Verify files by comparing their SHA512 hashes against a provided reference file.",
                 font=("TkDefaultFont", 8)).grid(row=3, column=0, sticky="w", padx=20)

    def _on_analysis_mode_selected_change(self):
        self._refresh_ui()


    def _create_file_and_directory_selectors(self):
        """
        Create and setup widgets for directory and file selection.

        :return: None
        """
        frame = ttk.LabelFrame(self._root, text="Analysis Options", padding=(10, 5, 10, 10))
        frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        frame.grid_columnconfigure(0, weight=0, minsize=150)
        frame.grid_columnconfigure(1, weight=1)

        # Directory
        self._label_selected_directory_header = tk.Label(frame)
        self._label_selected_directory_header.grid(row=1, column=0, sticky="w", pady=5)

        self._label_selected_directory = tk.Label(frame, text="", anchor="w", width=50, relief="sunken")
        self._label_selected_directory.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self._button_directory_selection = tk.Button(frame,
                                                     text="Browse",
                                                     command=self._open_directory_selection_dialog)
        self._button_directory_selection.grid(row=1, column=2, padx=5)

        # File
        self._label_selected_file_header = tk.Label(frame)
        self._label_selected_file_header.grid(row=2, column=0, sticky="w", pady=5)

        self._label_selected_file = tk.Label(frame, text="", anchor="w", width=50, relief="sunken")
        self._label_selected_file.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self._button_file_selection = tk.Button(frame, text="Browse",
                                                       command=self._open_file_selection_dialog)
        self._button_file_selection.grid(row=2, column=2, padx=5)

    def _create_progress_section(self):
        """
        Create progress bar and info label inside a frame.
        :return: None
        """

        frame = ttk.Frame(self._root, padding=10)
        frame.grid(row=3, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)

        self._progress_info_label = tk.Label(frame, anchor="e")
        self._progress_info_label.grid(row=0, pady=(10, 5), sticky="ew")

        self._progress_bar = ttk.Progressbar(frame)
        self._progress_bar.grid(row=1, pady=(0, 15), sticky="ew")

    def _create_action_buttons(self):
        """
        Create actions buttons.

        :return: None
        """

        button_frame = ttk.Frame(self._root, padding=10)
        button_frame.grid(row=4, column=0, sticky="se")

        self._start_button = tk.Button(button_frame, text="Start", width=20, command=self.analyze)
        self._start_button.grid(row=0, column=0, padx=5)

    def _open_directory_selection_dialog(self):
        """
        Opens a folder selection dialog for directory selection.

        :return: None
        """

        self._selected_directory = HelperUserInterface.select_folder()
        self._refresh_ui()

    def _open_file_selection_dialog(self):
        """
        Opens a file save dialog file selection.

        :return: None
        """

        if self._is_analysis_mode_selected.get():
            self._selected_file = HelperUserInterface.select_output_file()
        else:
            self._selected_file = select_hash_file()

        self._refresh_ui()

    def _refresh_ui(self):
        """
        Refresh UI

        :return: None
        """
        # Analysis not running
        if self._thread is None:

            self._label_selected_directory["text"] = self._selected_directory
            self._label_selected_file["text"] = self._selected_file

            # Update labels regarding file and directory section...
            if self._is_analysis_mode_selected.get():
                self._label_selected_directory_header["text"] = "Directory to Analyze:"
                self._label_selected_file_header["text"] = "Output File:"

            else:
                self._label_selected_directory_header["text"] = "Directory to Verify:"
                self._label_selected_file_header["text"] = "Input Hash File:"

            # Setup 'Progress Bar'...
            self._progress_bar["value"] = 0
            self._progress_info_label["text"] = ""

            # Setup 'Browse' buttons...
            self._button_directory_selection.config(state="active")
            self._button_file_selection.config(state="active")

            # Setup 'Task Selection'...
            self._analyze_radio.config(state="active")
            self._verify_radio.config(state="active")

            # Setup 'Action Button'...
            if ((self._selected_file and self._selected_file.strip()) and
                    (self._selected_directory and self._selected_directory.strip())):

                self._start_button.config(state="active")
            else:
                self._start_button.config(state="disabled")

        # Analysis running
        else:

            # Setup 'Browse' buttons...
            self._button_directory_selection.config(state="disabled")
            self._button_file_selection.config(state="disabled")

            # Setup 'Task Selection'...
            self._analyze_radio.config(state="disabled")
            self._verify_radio.config(state="disabled")

            # Setup 'Action Button'...
            self._start_button.config(state="disabled")

            # Setup 'Progress Bar'...
            self._progress_bar["value"] = self._file_analyzed_count - 1
            self._progress_info_label["text"] = f"Analyzing file {self._file_analyzed_count} of {self._file_count}"


    def analyze(self):
        """
        Start analysis

        :return: None
        """
        try:
            self._thread = threading.Thread(target=self._analyze_task)

            self._file_analyzed_count = 0
            self._refresh_ui()

            self._thread.start()
            self._root.after(50, lambda param : self.analyze_check_status(), None)

        except Exception as e:
            self._logger.log(f"An unexpected error occurred:\n{str(e)}")

    def analyze_check_status(self):
        """

        :return:
        """

        if self._thread.is_alive():
            self._root.after(50, lambda param : self.analyze_check_status(), None)
        else:
            self._thread.join()

            self._thread = None
            self._refresh_ui()
            messagebox.showinfo("Analysis Complete", "The analysis has finished. Check the logs for more information")

    def _analyze_task(self):
        """
        Executes the analysis task based on the selected mode.
        It either scans the directory and writes SHA512 hashes to a file,
        or verifies existing hashes against files in the directory.

        :return: None
        """
        try:

            self._file_count = HelperUserInterface.count_files(self._selected_directory)
            self._progress_bar.config(maximum=self._file_count)

            if self._is_analysis_mode_selected.get():
                analyze_directory(self._selected_directory, self._selected_file, self, self._logger)
            else:
                verify_hashes(self._selected_directory, self._selected_file, self, self._logger)

        except Exception as e:
            messagebox.showerror("Analysis Error", f"An error occurred during analysis:\n{str(e)}")