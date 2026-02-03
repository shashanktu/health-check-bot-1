from fastapi import APIRouter, BackgroundTasks, Request
import subprocess
import threading
import os
import signal

router = APIRouter()

# Store process globally (for demo; use a better manager for production)
test_impact_process = None
process_lock = threading.Lock()

@router.post("/run-test-impact")
async def run_test_impact(background_tasks: BackgroundTasks, request: Request):
    global test_impact_process
    data = None
    try:
        data = await request.json()
    except Exception:
        pass
    filename = None
    if data and "filename" in data:
        filename = data["filename"]
    def run_playwright():
        global test_impact_process
        npx_path = r"C:\Program Files\nodejs\npx.cmd"  # Update if your Node.js is installed elsewhere
        test_file = filename if filename else "tests/TagAI/*.*"
        cmd = [npx_path, "playwright", "test", test_file, "--reporter=html", "--headed"]
        test_impact_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=".", text=True)
        test_impact_process.wait()
        test_impact_process = None  # Ensure status is updated immediately after completion
    background_tasks.add_task(run_playwright)
    return {"status": "started"}

@router.post("/stop-test-impact")
def stop_test_impact():
    global test_impact_process
    with process_lock:
        if test_impact_process and test_impact_process.poll() is None:
            test_impact_process.terminate()
            return {"status": "stopped"}
        return {"status": "not_running"}

@router.get("/test-impact-status")
def test_impact_status():
    global test_impact_process
    running = test_impact_process is not None and test_impact_process.poll() is None
    return {"running": running}
