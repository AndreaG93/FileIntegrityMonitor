from Helpers.HelperAnalyzer import verify_hashes
from Helpers.HelperUserInterface import select_hash_file, select_folder

# Ask the user to select the hash file using a GUI dialog
hash_file = select_hash_file()
if not hash_file:
    exit(1)

# Ask the user to select the directory to be checked
folder_to_be_checked = select_folder()
if not folder_to_be_checked:
    exit(1)

# Run the verification process on the selected hash file
verify_hashes(folder_to_be_checked, hash_file)
