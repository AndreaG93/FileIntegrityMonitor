from Helpers.HelperAnalyzer import analyze_directory
from Helpers.HelperUserInterface import select_output_file
from Helpers.HelperUserInterface import select_folder

# Ask the user to select the folder to analyze
folder_to_analyze = select_folder()
if not folder_to_analyze:
    exit(1)

# Ask the user to select the output file location
output_hash_file = select_output_file()
if not output_hash_file:
    exit(1)

# Run the analysis and write hashes to the output file
analyze_directory(folder_to_analyze, output_hash_file)
