import subprocess
import datetime
import os

# Step 1: Create logs directory
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

log_file = os.path.join(LOG_DIR, "pipeline.log")


def log(message):
    timestamp = datetime.datetime.now()
    line = f"{timestamp} - {message}"
    
    print(line)
    
    with open(log_file, "a") as f:
        f.write(line + "\n")


# ✅ UPDATED WITH RETRY
def run_step(command, step_name, retries=2):
    for attempt in range(retries + 1):
        log(f"START: {step_name} (Attempt {attempt+1})")
        
        result = subprocess.run(command, shell=True)
        
        if result.returncode == 0:
            log(f"SUCCESS: {step_name}")
            return
        else:
            log(f"FAILED: {step_name} (Attempt {attempt+1})")
    
    log(f"❌ FINAL FAILURE: {step_name}")
    exit(1)


log("🚀 Pipeline started")

# Fetch
run_step(
    "/Users/anishgulhane/data-engineering-project/venv/bin/python scripts/fetch_crypto.py",
    "Fetch Data"
)

# Load
run_step(
    "/Users/anishgulhane/data-engineering-project/venv/bin/python scripts/load_to_db.py",
    "Load to DB"
)

# Transform
run_step(
    "/opt/homebrew/bin/psql crypto_db -f scripts/transform.sql",
    "Transform Data"
)

log("🎉 Pipeline finished successfully")