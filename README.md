# Project Overview

This project consists of two main components:

1. **Flask Web Application**  
   A simple Flask server that serves a web page with a personalized workspace. Users can enter their name, submit it, and receive a customized workspace on the page.

2. **PyQt6 Desktop Application**  
   A feature-rich code editor and workspace manager built with PyQt6. It includes prompt management, API configuration for AI integration, workflow saving/loading, and terminal output. The app supports managing URL and file references and sending commands to an AI model via API.

---

## Features

### Flask Web Application
- Simple user interface with a greeting message
- Input field for user name
- Personalized greeting display after submission
- Runs on `localhost:5000`

### PyQt6 Desktop Application
- Code editor with syntax highlighting and dark theme
- Workspace management with file system tree view
- Prompt management with folders and drag-drop support
- API configuration window for OpenAI API keys and model selection
- Workflow saving and loading (including open tabs, prompts, and terminal output)
- URL and file reference management for AI context
- Terminal output panel for logging actions and responses
- Integration with AI models for code generation and command processing

---

## Installation

### Prerequisites
- Python 3.8 or higher
- Pip package manager

### Required Python Packages
Install the required packages using pip:

```bash
pip install flask pyqt6 requests
```

---

## Usage

### Running the Flask Web Application

1. Navigate to the project directory.
2. Run the Flask app:

```bash
python3 flask_app.py
```

3. Open your web browser and go to `http://localhost:5000`.
4. Enter your name in the input field and click "Submit" to see a personalized greeting.

---

### Running the PyQt6 Desktop Application

1. Navigate to the project directory.
2. Run the PyQt6 app:

```bash
python3 main.py
```

3. Use the toolbar to create a workspace, manage prompts, configure the OpenAI API, and manage URL/file references.
4. Use the text input window to send commands to the AI model.
5. Save and load workflows to preserve your session state.

---

## Configuration

- The `config.json` file stores API endpoint URLs, API keys, and selected AI models.
- Use the "Open API Configuration" option in the PyQt6 app toolbar to update your API key and select models.
- The app automatically saves configuration changes to `config.json`.

---

## Workflow Management

- Save your current workflow (prompts, open tabs, terminal output, references) to a JSON file.
- Load saved workflows to restore your session.
- Use the toolbar buttons "Save Workflow" and "Load Workflow" in the PyQt6 app.

---

## File Structure

- `flask_app.py` - Flask web server application.
- `main.py` - PyQt6 desktop application with code editor and AI integration.
- `config.json` - Configuration file for API keys and endpoints.
- `workflow.json` - Example or saved workflow file.
- `Moj.json`, `poskus.json` - Additional JSON files (possibly data or configuration).
- `README.md` - This file.

---

## License

The license is closed, which means you can upgrade, review, and improve the code, but you cannot create your own project from it without my consent. This does not mean that I do not want to keep the code open for everyone; it is just controlled open source.

---

## Troubleshooting

### Qt Platform Plugin "xcb" Error

If you encounter the following error when running the PyQt6 application:

```
qt.qpa.plugin: From 6.5.0, xcb-cursor0 or libxcb-cursor0 is needed to load the Qt xcb platform plugin.
qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.

Available platform plugins are: eglfs, linuxfb, minimal, minimalegl, offscreen, vkkhrdisplay, vnc, wayland-egl, wayland, xcb.
```

This usually means that the required Qt platform plugin dependencies are missing from your system.

#### Solution

On Debian/Ubuntu-based systems, install the following packages:

```bash

sudo apt-get update && sudo apt-get install -y libxcb-xinerama0 libxcb-cursor0

```

On other Linux distributions, install the equivalent packages that provide the `xcb` platform plugin and its dependencies.

After installing these packages, try running the PyQt6 application again.

---

## Contact

For questions or support, please contact the project maintainer.

