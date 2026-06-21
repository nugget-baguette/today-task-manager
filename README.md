# Daily Task Manager

Daily Task Manager is a simple and modern desktop application designed for visual and intuitive management of your daily schedule. Built using Python and CustomTkinter.

## Features

* **Daily File Management**: Automatically creates and loads a dedicated task file (`YYYY-MM-DD.json`) based on the current date upon startup.

* **Intuitive Controls**: Click the timeline to add tasks. Drag and drop (or use keyboard controls) to move or resize tasks.

* **Progress Indicator**: The progress bar on the timeline automatically updates according to the current time.

* **Modern UI**: Features a sleek, rounded-design interface.

## How to Use

1. **Add Tasks**: Click an empty slot on the timeline, type the task name, and press `Enter`.

2. **Toggle Completion**: Press `Right Click` or `Ctrl+Enter` (`Command+Enter`) on the task entry field to toggle the completion status.

3. **Task Details**: `Double-click` or press `Ctrl+d` (`Command+d`, `d` is short for **description**) to open a detail window where you can save notes or detailed descriptions. The data is saved as `json` file at

4. **Move/Resize Tasks**:

   * `Shift + Up/Down Arrow`: Adjust the length of the task (resize).

   * `Up/Down Arrow`: Move the selection cursor to navigate tasks.

## Requirements

* Python 3.x

* Required libraries: `customtkinter`

## Installation and Running

1. Clone or download the repository.

2. Install dependencies using `uv`:

   ```
   uv add customtkinter
   ```

3. Run the application:

   ```
   python main.py
   ```

## License

MIT License
