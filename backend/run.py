import uvicorn
import os
import sys

if __name__ == "__main__":
    # Get the directory containing this script (the 'backend' directory)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add it to sys.path so 'app' module can be found
    sys.path.insert(0, current_dir)
    
    # Run Uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)
