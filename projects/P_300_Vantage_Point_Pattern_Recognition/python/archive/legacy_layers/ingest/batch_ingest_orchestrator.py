# Updated Configuration to match Pipeline B
INPUT_FOLDER = BASE_PATH / "data" / "historical_patterns"
ARCHIVE_FOLDER = BASE_PATH / "data" / "processed"  # Consolidated

def run_vault_ingest():
    # Ensure the archive folder exists before we start
    os.makedirs(ARCHIVE_FOLDER, exist_ok=True) 
    
    # ... [rest of the script] ...
    
    for file in INPUT_FOLDER.glob("Pattern_*.csv"):
        # ... [ingest logic] ...
        
        # Archive to the consolidated folder
        shutil.move(str(file), str(ARCHIVE_FOLDER / file.name))