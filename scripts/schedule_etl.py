import os
import subprocess
import sys
import datetime
import time

# Paths
workspace = r"c:\Datatatatta"
scripts_dir = os.path.join(workspace, "scripts")
live_fetch_path = os.path.join(scripts_dir, "live_nav_fetch.py")
etl_pipeline_path = os.path.join(scripts_dir, "etl_pipeline.py")

def run_job():
    print(f"[{datetime.datetime.now()}] Triggering scheduled weekday ETL job...")
    try:
        # 1. Fetch latest NAV values
        print("Step 1: Fetching live NAV data...")
        subprocess.run([sys.executable, live_fetch_path], check=True)
        
        # 2. Run ETL pipeline
        print("Step 2: Processing and loading database...")
        subprocess.run([sys.executable, etl_pipeline_path], check=True)
        
        print(f"[{datetime.datetime.now()}] Scheduled job completed successfully!")
    except Exception as e:
        print(f"Error executing scheduled job: {e}")

def main():
    print("ETL Scheduler Service started. Monitoring for weekday 8:00 PM trigger...")
    print("To install as a permanent Windows Scheduled Task, run:")
    print("  schtasks /create /tn \"BluestockETL\" /tr \"python c:\\Datatatatta\\scripts\\schedule_etl.py --run\" /sc weekly /d MON,TUE,WED,THU,FRI /st 20:00")
    
    # Check if run argument is provided to run immediately (for Task Scheduler integration)
    if "--run" in sys.argv:
        run_job()
        return

    # Background service loop
    while True:
        now = datetime.datetime.now()
        # Weekday check (0=Mon, 4=Fri) and time check (8:00 PM)
        if now.weekday() <= 4 and now.hour == 20 and now.minute == 0:
            run_job()
            time.sleep(65)  # Sleep to avoid double-triggering in the same minute
        time.sleep(30)      # Check every 30 seconds

if __name__ == "__main__":
    main()
