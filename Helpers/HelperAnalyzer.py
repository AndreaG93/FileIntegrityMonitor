import os
import hashlib

def sha512sum(filepath):
    """
    Calculates the SHA512 hash of a file.

    :param filepath: Full path to the file.
    :return: Hexadecimal string representing the SHA512 hash.
    """

    if not filepath:
        raise ValueError("File path is empty or None.")

    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    output = hashlib.sha512()

    # Read the file in binary mode, in chunks (streaming)
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192): # Read 8KB at a time
            output.update(chunk)

    # Return the final hash as a hex string
    return output.hexdigest()


def analyze_directory(directory_to_be_analyzed, output_file, analysis_observer, analysis_logger):
    """
    Walks through all files in a directory and writes their SHA512 hashes
    and full paths to an output file, one hash and path per a pair of lines.

    :param directory_to_be_analyzed: The root directory to scan.
    :param output_file: The file where results will be saved.
    :param analysis_observer:
    :param analysis_logger:
    """

    # Check parameters
    if not directory_to_be_analyzed or not output_file:
        raise ValueError("Both 'directoryToBeAnalyzed' and 'outputFile' must be provided.")

    if not os.path.isdir(directory_to_be_analyzed):
        raise NotADirectoryError(f"Provided path is not a directory: {directory_to_be_analyzed}")

    # Normalize paths
    directory_to_be_analyzed = os.path.abspath(directory_to_be_analyzed)
    output_file = os.path.abspath(output_file)

    # Write hashes to output file
    with open(output_file, 'w', encoding='utf-8') as out:
        for root, _, files in os.walk(directory_to_be_analyzed):
            for name in files:
                filepath = os.path.join(root, name)

                # Skip the output file itself
                if os.path.samefile(filepath, output_file):
                    continue

                try:
                    hash_value = sha512sum(filepath)

                    # Remove the root prefix to produce a path relative to the analyzed directory
                    filepath_tail = filepath[len(directory_to_be_analyzed):].lstrip(os.sep)

                    out.write(f"{hash_value}\n{filepath_tail}\n")

                    # Notify complete analysis on current file
                    analysis_observer.on_file_completed(filepath)

                except Exception as e:
                    analysis_logger.log(f"ERROR processing {filepath}: {e}")

def verify_hashes(directory_to_be_checked, hash_file_path, analysis_observer, analysis_logger):
    """
    Verifies SHA512 hashes listed in a file.
    Each hash is followed by its corresponding file path.

    :param directory_to_be_checked: Base directory to prepend to stored relative paths.
    :param hash_file_path: Path to the file containing alternating lines: hash, file path.
    :param analysis_observer:
    :param analysis_logger:
    """
    if not os.path.isfile(hash_file_path):
        raise FileNotFoundError(f"Hash file not found: {hash_file_path}")

    with open(hash_file_path, 'r', encoding='utf-8') as f:
        while True:

            expected_hash = f.readline()
            file_path = f.readline()

            if not expected_hash or not file_path:
                return

            expected_hash = expected_hash.strip()

            file_path = file_path.strip()
            file_path = os.path.normpath(os.path.join(directory_to_be_checked, file_path))

            if not os.path.isfile(file_path):
                analysis_logger.log(f"[MISSING] {file_path}")
                continue

            try:
                actual_hash = sha512sum(file_path)
                if actual_hash != expected_hash:
                    analysis_logger.log(f"[MISMATCH] {file_path}")

                # Notify complete analysis on current file
                analysis_observer.on_file_completed(file_path)

            except Exception as e:
                analysis_logger.log(f"[ERROR] {file_path}: {e}")