Daily Task Manager

Daily Task Manager is a simple, modern, and keyboard-centric desktop application designed for intuitive daily schedule management. Built with Python and CustomTkinter.

🚀 Key Features

Keyboard-Driven Workflow: Experience seamless task management without your hands ever leaving the keyboard. Navigate, create, resize, and move tasks instantly using simple keystrokes.

Daily "Tear-off Calendar" System: Automatically creates and loads a dedicated JSON file for the current day (YYYY-MM-DD.json). Start fresh every morning while keeping a pristine record of your past days.

Real-time Progress Tracker: A visual progress bar on the timeline updates dynamically alongside the current time.

Modern & Sleek UI: A highly polished, distraction-free interface featuring rounded corners and adaptive layouts.

⌨️ How to Use (Keyboard Shortcuts)

This app is built for speed. Here is how you can manage your entire day using just your keyboard:

Navigate: Use ↑ / ↓ keys to move the cursor smoothly across the timeline.

Add a Task: Type your task name in an empty time slot and hit Enter. The task will be created and instantly "grabbed".

Select/Grab a Task: Press Enter on an existing task. The border will highlight (yellow), indicating it's ready to be modified.

Move a Task: While grabbed, use ↑ / ↓ to move the task up or down the timeline.

Resize (Change Duration): While grabbed, use Shift + ↑ / Shift + ↓ to extend or shrink the task's time block.

Toggle Completion: Press Ctrl + Enter (or Command + Enter on Mac) to cross out a task and mark it as done.

Add Details/Notes: Press Ctrl + D (or Command + D on Mac) to pop open a detailed description window for memos and links.

Release/Deselect: Press Esc (or Enter again) to drop the task and return to navigation mode.

⚠️ Troubleshooting (Important!)

Keyboard shortcuts not working or acting weird?
Please check if your NumLock key is ON.
Due to how the underlying GUI library (Tkinter) handles keystrokes, having NumLock turned ON can interfere with the Enter and Arrow keys, making the app think a modifier key is constantly pressed. If you experience unexpected behavior (e.g., tasks completing randomly instead of being selected), turn off NumLock.

💻 Requirements

uv (An extremely fast Python package and project manager)

Required library: customtkinter

🛠️ Installation & Quick Start

Clone or download this repository.

Add the dependency using uv:

uv add customtkinter


Run the application:

uv run main.py


Pro Tip: Silent Launch (Windows)

We recommend using a .vbs script to launch the app entirely in the background without the black command-prompt window. You can create a start_app.vbs file for a seamless, native-app-like experience.

📄 License

MIT License