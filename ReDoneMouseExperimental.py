import os
import json
import time
import threading
import win32api
import win32con
from datetime import datetime
from pynput import mouse
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import GlobalHotKeys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

recording = False
events = []
start_time = None
mouse_controller = MouseController()
mouse_listener = None
playback_thread = None
stop_playback = False

FOLDER = "Mouse Logs"

def on_move(x, y):
    if recording:
        events.append({
            "type": "move",
            "x": x,
            "y": y,
            "t": time.time() - start_time
        })

def on_click(x, y, button, pressed):
    if recording:
        events.append({
            "type": "click",
            "x": x,
            "y": y,
            "b": str(button),
            "p": pressed,
            "t": time.time() - start_time
        })

def start_recording():
    global recording, events, start_time, mouse_listener
    if recording:
        print("⚠️ Already recording.")
        return
    print("🔴 Mouse recording started.")
    recording = True
    events = []
    start_time = time.time()
    mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
    mouse_listener.start()

def stop_recording():
    global recording, mouse_listener
    if not recording:
        print("⚠️ Not currently recording.")
        return
    recording = False
    if mouse_listener:
        mouse_listener.stop()
    ensure_log_dir()
    now = datetime.now()
    timestamp = now.strftime("%m-%d-%Y %H-%M-%S-%f")
    filename = os.path.join(FOLDER, f"mouselog {timestamp}.json")
    with open(filename, "w") as f:
        json.dump(events, f, indent=2)
    print(f"⏹️ Mouse recording stopped. Saved {len(events)} events to:\n  {filename}")

def ensure_log_dir():
    if not os.path.exists(FOLDER):
        os.makedirs(FOLDER)

def choose_file():
    ensure_log_dir()
    files = [f for f in os.listdir(FOLDER) if f.endswith(".json")]
    if not files:
        print("⚠️ No mouse log files found.")
        return None

    print("Available mouse log files:")
    for i, fname in enumerate(files, 1):
        print(f"  {i}: {fname}")

    while True:
        choice = input(f"Enter the number of the file to play (1-{len(files)}): ")
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(files):
                return os.path.join(FOLDER, files[idx - 1])
        print("Invalid input, try again.")

def ask_speed():
    while True:
        speed_str = input("Enter playback speed multiplier (e.g., 1.0 = normal speed): ")
        try:
            speed = float(speed_str)
            if speed > 0:
                return speed
        except ValueError:
            pass
        print("Invalid number, try again.")

def ask_loop_count():
    while True:
        val = input("How many times to play? (e.g., 1, 5, 0 to skip, or 'infinite'): ").strip().lower()
        if val == "infinite":
            return "infinite"
        if val.isdigit():
            return int(val)
        print("Invalid input, try again.")

def move_mouse_relative(dx, dy):
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, dy, 0, 0)

def playback_worker(filepath, speed, loops):
    global stop_playback
    with open(filepath, "r") as f:
        data = json.load(f)

    print("▶️ Starting playback in 5 seconds... Get ready!")
    time.sleep(5)

    loop = 0
    while not stop_playback and (loops == "infinite" or loop < loops):
        loop += 1
        start_time_loop = time.time()
        prev_x = None
        prev_y = None
        for event in data:
            if stop_playback:
                print("⏹️ Playback stopped.")
                return
            delay = event["t"] / speed - (time.time() - start_time_loop)
            if delay > 0:
                time.sleep(delay)
            if event["type"] == "move":
                if prev_x is None:
                    prev_x = event["x"]
                    prev_y = event["y"]
                    continue
                dx = event["x"] - prev_x
                dy = event["y"] - prev_y
                move_mouse_relative(dx, dy)
                prev_x = event["x"]
                prev_y = event["y"]
            elif event["type"] == "click":
                button = win32con.MOUSEEVENTF_LEFTDOWN if "left" in event["b"] else win32con.MOUSEEVENTF_RIGHTDOWN
                up_button = win32con.MOUSEEVENTF_LEFTUP if "left" in event["b"] else win32con.MOUSEEVENTF_RIGHTUP
                if event["p"]:
                    win32api.mouse_event(button, 0, 0, 0, 0)
                else:
                    win32api.mouse_event(up_button, 0, 0, 0, 0)
        print(f"✅ Finished playback loop {loop}")

    print("⏹️ Playback complete.")


def play_events():
    global playback_thread, stop_playback
    if playback_thread and playback_thread.is_alive():
        print("⚠️ Playback already running.")
        return

    filepath = choose_file()
    if not filepath:
        return

    loop_count = ask_loop_count()
    if loop_count == 0:
        print("⏭️ Skipping playback.")
        return

    speed = ask_speed()

    stop_playback = False
    playback_thread = threading.Thread(target=playback_worker, args=(filepath, speed, loop_count), daemon=True)
    playback_thread.start()

def toggle_recording():
    global recording
    if recording:
        stop_recording()
    else:
        start_recording()

def force_quit():
    global stop_playback
    print("🛑 Force quitting script!")
    stop_playback = True
    os._exit(0)

def main():
    print("🖱️ Mouse Recorder & Player ready.")
    print("  Shift+E → Start/Stop recording")
    print("  Shift+W → Play recording")
    print("  Ctrl+Shift+Q → Force quit")

    with GlobalHotKeys({
        '<shift>+e': toggle_recording,
        '<shift>+w': play_events,
        '<ctrl>+<shift>+q': force_quit
    }) as h:
        h.join()

if __name__ == "__main__":
    main()
