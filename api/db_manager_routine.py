import subprocess
import time

def run_db_manager():
    while True:
        # Start the db_manager.py script
        process = subprocess.Popen(['python', 'db_manager.py'])
        
        # Run for a day (24 hours)
        time.sleep(86400)
        
        # Terminate the process
        process.terminate()
        
        # Wait for the process to terminate
        process.wait()

if __name__ == "__main__":
    run_db_manager()