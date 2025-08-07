# ReDone: Input Recorder & Playback Tool

ReDone is a lightweight Python project for recording and replaying keyboard and mouse actions with customizable playback options. It is designed for quick, reliable input automation with simple controls.

---

## IMPORTANT

The script sometimes messes up some stuff about Windows Explorer, in that case just click `Shift` and release it, I'm not sure why but the script makes it stuck.

---

## Features

- Record keyboard inputs and mouse movements/clicks with precise timing.
- Play back recorded input logs at adjustable speeds.
- Loop playback with finite or infinite options.
- Cross-platform compatible using the `pynput` library.
- Simple hotkey controls for recording, playback, and quitting.
- Saves logs with timestamped filenames to avoid overwriting.
- Graceful playback stop and force quit capabilities.

---

## Getting Started

### Prerequisites

- Python 3.7 or later
- `pynput` library (`pip install pynput` in your cmd)

### Files

- `ReDoneKeyboard.py` — keyboard recorder and player script
- `ReDoneMouse.py` — mouse recorder and player script
- `ReDoneMouseExperimental.py` (by Xmogus) — mouse recorder and player script but this has a different way of doing it so it works for games like Minecraft

### How to Use
1. Download ZIP:
    
    Click on the Code button on the top right and download ZIP. Extract the ZIP in a folder of your choice.

2. Run the script:
    Right click on one of the scripts and launch with Python.

3. Hotkeys:

    **Note:** You can edit the hotkeys inside the script but I'm not gonna help you with that.

   | Action             | Hotkey           |
   | ------------------ | ---------------- |
   | Start/stop recording | Shift + E |
   | Start playback       | Shift + W |
   | Force quit script    | Ctrl + Shift + Q |

5. When prompted, choose the log file, playback speed, and loop count (or infinite).

---

## Notes

- Logs are saved in folders named `Keyboard Logs` and `Mouse Logs` inside the script directory.
- Playback can be stopped anytime by pressing the quit hotkey.
- Infinite loops require quitting manually via the quit hotkey.
- Hotkeys used by the script are ignored during recording to prevent self-triggering.
- When playback starts, you will have 5 seconds to prepare before it begins.

---

## License

This project is provided under a **custom license** that allows you to:

- Use, modify, and share the code freely for **non-commercial purposes**.
- Provide proper **attribution** to the original author (Kristiyalno), including this repository and its contributors.

**Commercial use, including selling or using this code for profit, is NOT allowed without explicit permission.**

---

If you want to use this project or its code commercially, please contact the author for licensing options.

---

*Note:* This license is not an official open-source license recognized by OSI but is designed to protect the author's rights while allowing free personal and educational use.


---

## Other

This was created with assistance from ChatGPT by OpenAI because I'm not the greatest programmer, nor are you.
