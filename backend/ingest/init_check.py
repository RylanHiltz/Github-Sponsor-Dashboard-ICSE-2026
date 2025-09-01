import json
from pathlib import Path
import datetime


STATE_FILE = Path(__file__).resolve().parent / "worker_state.json"


# Checks the status of the worker
def load_worker_state():
    """Load state from file or initialize if it doesn't exist."""
    if not STATE_FILE.exists():
        state = {"init_run": True, "last_init_run": None}
        save_worker_state(state)
        return state

    with STATE_FILE.open("r") as f:
        state = json.load(f)
    return state


def save_worker_state(state: dict):
    with STATE_FILE.open("w") as f:
        json.dump(state, f, indent=4)
    return


def update_worker_state():
    """Update function used after the initial sponsorable users have been crawled"""
    state = {"init_run": False, "last_init_run": datetime.datetime.now().isoformat()}
    save_worker_state(state)
