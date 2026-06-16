"""
Bluestock Mutual Fund Capstone Master Execution Pipeline.
This script orchestrates the entire data processing and analytics flow:
1. Live NAV API Ingestion (live_nav_fetch.py)
2. Ingestion, Cleaning & SQL Database Load (etl_pipeline.py)
3. Risk-Return Analytics Performance Calculator (compute_metrics.py)
4. PDF Report and Slide Presentation Compiler (generate_pdf_pptx.py)
"""

import os
import sys
import subprocess
import time

def run_script(script_path):
    """
    Executes a Python script as a subprocess and logs its output.
    """
    print(f"\n================================================================================")
    print(f"RUNNING STEP: {os.path.basename(script_path)}")
    print(f"================================================================================")
    start_time = time.time()
    
    # Run the script with the current python executable
    res = subprocess.run([sys.executable, script_path], capture_output=False)
    
    elapsed = time.time() - start_time
    if res.returncode == 0:
        print(f"SUCCESS: {os.path.basename(script_path)} completed in {elapsed:.2f} seconds.")
    else:
        print(f"FAILURE: {os.path.basename(script_path)} failed with exit code {res.returncode}.")
        sys.exit(res.returncode)

def main():
    """
    Main pipeline coordinator.
    """
    workspace = os.path.dirname(os.path.abspath(__file__))
    scripts_dir = os.path.join(workspace, "scripts")
    
    # Define steps in order
    steps = [
        os.path.join(scripts_dir, "live_nav_fetch.py"),
        os.path.join(scripts_dir, "etl_pipeline.py"),
        os.path.join(scripts_dir, "compute_metrics.py"),
        os.path.join(scripts_dir, "generate_pdf_pptx.py")
    ]
    
    print("================================================================================")
    print("           BLUESTOCK MUTUAL FUND CAPSTONE: MASTER PIPELINE RUNNER               ")
    print("================================================================================")
    
    pipeline_start = time.time()
    for step in steps:
        if not os.path.exists(step):
            print(f"Error: Required pipeline step script '{step}' does not exist.")
            sys.exit(1)
        run_script(step)
        
    pipeline_elapsed = time.time() - pipeline_start
    print(f"\n================================================================================")
    print(f"COMPLETE PIPELINE EXECUTED SUCCESSFULLY in {pipeline_elapsed:.2f} seconds!")
    print(f"================================================================================")
    print(f"Deliverables generated:")
    print(f"  - Database: data/db/bluestock_mf.db")
    print(f"  - Performance Metrics: data/processed/computed_performance_metrics.csv")
    print(f"  - Final PDF Report: Final_Report.pdf and reports/Final_Report.pdf")
    print(f"  - Presentation Slides: Bluestock_MF_Presentation.pptx and reports/Presentation.pptx")
    print(f"================================================================================")

if __name__ == "__main__":
    main()
