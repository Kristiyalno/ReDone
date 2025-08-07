import json
import os
import time
import threading
from datetime import datetime
from pynput import keyboard
from pynput.keyboard import Key, Controller as KeyboardController, GlobalHotKeys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

recording = False
recorded_keys = []
pressed_keys_set = set()
start_time = None
LOG_DIR = "Keyboard Logs"
stop_playback = False
playback_thread = None

HOTKEY_COMBOS = [
    {Key.shift, 'e'},
    {Key.shift, 'w'},
    {Key.ctrl_l, Key.shift, 'q'},
    {Key.ctrl_r, Key.shift, 'q'}
]

def ensure_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

def get_log_filename():
    now = datetime.now()
    timestamp = now.strftime("%m-%d-%Y %H-%M-%S-%f")
    return os.path.join(LOG_DIR, f"keyboardlog {timestamp}.json")

def is_hotkey_combo():
    for combo in HOTKEY_COMBOS:
        if combo.issubset(pressed_keys_set):
            return True
    return False

def on_press(key):
    if recording:
        pressed_keys_set.add(key if isinstance(key, Key) else key.char)
        if is_hotkey_combo():
            return
        recorded_keys.append({
            'type': 'press',
            'key': str(key),
            'time': time.time() - start_time
        })

def on_release(key):
    if recording:
        if is_hotkey_combo():
            pressed_keys_set.discard(key if isinstance(key, Key) else key.char)
            return
        recorded_keys.append({
            'type': 'release',
            'key': str(key),
            'time': time.time() - start_time
        })
        pressed_keys_set.discard(key if isinstance(key, Key) else key.char)

def start_recording():
    global recording, recorded_keys, start_time, key_listener
    if recording:
        print("⚠️ Already recording.")
        return
    print("🔴 Keyboard recording started.")
    recorded_keys.clear()
    start_time = time.time()
    recording = True
    key_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    key_listener.start()

def stop_recording():
    global recording, key_listener
    if not recording:
        print("⚠️ Not currently recording.")
        return
    recording = False
    key_listener.stop()
    ensure_log_dir()
    filename = get_log_filename()
    with open(filename, 'w') as f:
        json.dump(recorded_keys, f, indent=2)
    print(f"⏹️ Keyboard recording stopped. Saved {len(recorded_keys)} events to:\n  {filename}")

def toggle_recording():
    if recording:
        stop_recording()
    else:
        start_recording()

def choose_file():
    ensure_log_dir()
    files = [f for f in os.listdir(LOG_DIR) if f.lower().startswith("keyboardlog") and f.endswith(".json")]
    if not files:
        print("⚠️ No keyboard log files found.")
        return None

    print("Available keyboard log files:")
    for i, fname in enumerate(files, 1):
        print(f"  {i}: {fname}")

    while True:
        choice = input(f"Enter the number of the file to play (1-{len(files)}): ")
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(files):
                return os.path.join(LOG_DIR, files[idx - 1])
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

def parse_key(key_str):
    if key_str.startswith("Key."):
        try:
            return getattr(Key, key_str.split(".")[1])
        except AttributeError:
            return None
    else:
        return key_str.strip("'")

def playback_worker(filepath, speed, loops):
    global stop_playback
    with open(filepath, 'r') as f:
        events = json.load(f)

    print("▶️ Starting playback in 5 seconds... Get ready!")
    time.sleep(5)

    count = 0
    kb = KeyboardController()

    while not stop_playback and (loops == "infinite" or count < loops):
        count += 1
        start_play = time.time()
        for event in events:
            if stop_playback:
                print("⏹️ Playback stopped.")
                return
            wait = (event['time'] / speed) - (time.time() - start_play)
            if wait > 0:
                time.sleep(wait)
            key = parse_key(event['key'])
            if key:
                try:
                    if event['type'] == 'press':
                        kb.press(key)
                    elif event['type'] == 'release':
                        kb.release(key)
                except Exception:
                    pass
        print(f"✅ Finished playback loop {count}")

    if loops == "infinite":
        print("⏹️ Stopped infinite playback.")
    else:
        print("✅ Playback finished.")

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

def force_quit():
    global stop_playback, recording
    print("🛑 Force quitting script!")
    stop_playback = True
    if recording:
        stop_recording()
    os._exit(0)

def main():
    print("⌨️ Keyboard Recorder & Player ready.")
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
