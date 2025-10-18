import os
import hashlib

from Gui.AnalysisLogger import AnalysisLogger
from Gui.AnalysisObserver import AnalysisObserver

def analyze_directory(directory_to_be_analyzed, output_file, analysis_observer, analysis_logger):
    """
    Walks through all files in a directory and writes their SHA512 hashes
    along with their full paths to an output file. Each file is represented by two lines:
    the first line contains the hash, and the second line contains the absolute file path.

    :param directory_to_be_analyzed: The root directory to scan for files.
    :param output_file: Path to the file where hash and path pairs will be written.
    :param analysis_observer: An object responsible for notifying progress of the analysis.
    :param analysis_logger: An object responsible for logging analysis events and errors.
    """

    # Validate inputs...
    __validate_inputs(directory_to_be_analyzed, output_file, analysis_observer, analysis_logger)

    # Write hashes to output file
    with open(output_file, 'w', encoding='utf-8') as out:
        for root, _, files in os.walk(directory_to_be_analyzed):
            for name in files:

                # Build full path...
                file_path = os.path.join(root, name)

                # Remove the root prefix to produce a path relative to the analyzed directory...
                file_path_tail = file_path[len(directory_to_be_analyzed):].lstrip(os.sep)

                # Skip the output file itself
                if os.path.samefile(file_path, output_file):
                    continue

                try:
                    hash_value = __sha512sum(file_path)
                    out.write(f"{hash_value}\n{file_path_tail}\n")

                except Exception as e:
                    analysis_logger.log(f"ERROR processing {file_path}: {e}")

                # Notify that analysis for current file has finished...
                analysis_observer.on_file_completed(file_path)

def verify_hashes(directory_to_be_checked, hash_file_path, analysis_observer, analysis_logger):
    """
    Verifies SHA512 hashes listed in a file. The file should contain alternating lines:
    one line with the expected hash value, followed by one line with the relative path
    to the corresponding file. Each pair is processed sequentially.

    :param directory_to_be_checked: Base directory to prepend to each relative file path.
    :param hash_file_path: Path to the file containing alternating lines of expected hash and file path.
    :param analysis_observer: An object responsible for notifying progress of the analysis.
    :param analysis_logger: An object responsible for logging analysis events.

    """

    # Validate inputs...
    __validate_inputs(directory_to_be_checked, hash_file_path, analysis_observer, analysis_logger)

    if not os.path.isfile(hash_file_path):
        raise FileNotFoundError(f"Hash file not found: {hash_file_path}")

    # Start analysis...
    with open(hash_file_path, 'r', encoding='utf-8') as f:
        while True:

            expected_hash = f.readline()
            file_path = f.readline()

            # Skip if either the expected hash or file path is missing...
            if expected_hash == "" or file_path == "":
                return

            expected_hash = expected_hash.strip()
            file_path = os.path.normpath(os.path.join(directory_to_be_checked, file_path.strip()))

            # Check if the file path points to an existing file...
            if not os.path.isfile(file_path):
                analysis_logger.log(f"[MISSING] File not found: {file_path}")
                continue

            # Start integrity analysis...
            try:
                actual_hash = __sha512sum(file_path)
                if actual_hash != expected_hash:
                    analysis_logger.log(f"[MISMATCH] {file_path}")

            except Exception as e:
                analysis_logger.log(f"[ERROR] Error occurred during {file_path} analysis: {e}")

            # Notify that analysis for current file has finished...
            analysis_observer.on_file_completed(file_path)

def __validate_inputs(directory, file, analysis_observer, analysis_logger):
    """
    Ensures correct types and values of input parameters before proceeding with analysis.

    :param directory: The base directory to scan or verify.
    :param file: The file path to read from or write to.
    :param analysis_observer: An object responsible for notifying progress.
    :param analysis_logger: An object responsible for logging events.
    """
    # Check parameter types
    if not isinstance(directory, str):
        raise TypeError(
            f"The 'directory' must be a string, got {type(directory).__name__} instead.")

    if not isinstance(file, str):
        raise TypeError(
            f"The 'file' must to be a string, got {type(file).__name__} instead.")

    if not isinstance(analysis_observer, AnalysisObserver):
        raise TypeError(
            f"Expected 'analysis_observer' to be an 'AnalysisObserver', got {type(analysis_observer).__name__} instead.")

    if not isinstance(analysis_logger, AnalysisLogger):
        raise TypeError(
            f"Expected 'analysis_logger' to be an 'AnalysisLogger', got {type(analysis_logger).__name__} instead.")

    # Check parameter values
    if not directory or not file:
        raise ValueError("Both 'directory' and 'file' must be provided and non-empty.")

    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Provided path is not a directory: {directory}")

def __sha512sum(filepath):
    """
    Calculates the SHA512 hash of a file.

    :param filepath: Full path to the file.
    :return: Hexadecimal string representing the SHA512 hash.
    """

    output = hashlib.sha512()

    # Read the file in binary mode, in chunks (streaming)
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192): # Read 8KB at a time
            output.update(chunk)

    # Return the final hash as a hex string
    return output.hexdigest()