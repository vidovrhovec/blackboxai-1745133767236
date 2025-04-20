import sys
import os
import json
import shutil
import requests
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QListWidget, QSizePolicy, QToolBar, QDialog, QLabel, QLineEdit, QPushButton,
    QComboBox, QTabWidget, QTreeView, QInputDialog, QPlainTextEdit, QAbstractItemView,
    QFileDialog, QCheckBox, QListWidgetItem, QMessageBox, QMenu, QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtGui import QIcon, QAction, QColor, QPalette, QFileSystemModel, QDrag
from PyQt6.QtCore import Qt, QMimeData, QDir

CONFIG_FILE = "config.json"

class TerminalOutput(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setStyleSheet("font: 10pt 'Courier'; background-color: black; color: white;")

class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("font: 10pt 'Courier'; background-color: black; color: white;")
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize reference lists and configurations
        self.url_references = []
        self.file_references = []
        self.use_urls = False
        self.use_files = False

        # Initialize workspace status
        self.workspace_path = None
        self.default_main_prompt = "Your default main prompt here."
        self.current_main_prompt = self.default_main_prompt

        # Load initial configuration
        self.load_config()

        # Main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # Prompt management
        self.prompt_tree = PromptTree()
        self.prompt_tree.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.prompt_tree.itemDoubleClicked.connect(self.populate_input_from_prompt)

        # Buttons for managing prompts
        prompt_buttons_layout = QHBoxLayout()
        add_prompt_button = QPushButton("Add Prompt")
        add_prompt_button.clicked.connect(self.add_prompt)
        add_folder_button = QPushButton("Add Folder")
        add_folder_button.clicked.connect(self.add_folder)
        remove_prompt_button = QPushButton("Remove")
        remove_prompt_button.clicked.connect(self.remove_prompt)
        prompt_buttons_layout.addWidget(add_prompt_button)
        prompt_buttons_layout.addWidget(add_folder_button)
        prompt_buttons_layout.addWidget(remove_prompt_button)

        # Main prompt input
        main_prompt_label = QLabel("Main Prompt:")
        self.main_prompt_input = QLineEdit(self.current_main_prompt)
        main_prompt_button = QPushButton("Set Main Prompt")
        main_prompt_button.clicked.connect(self.set_main_prompt)
        reset_prompt_button = QPushButton("Reset Main Prompt")
        reset_prompt_button.clicked.connect(self.reset_main_prompt)

        # Text input window
        self.text_input_window = QTextEdit()
        self.text_input_window.setPlaceholderText("Text Input Window")

        # Send button
        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_command)

        # File system model for workspace
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.workspace_context_menu)
        self.tree_view.doubleClicked.connect(self.open_file_from_tree)

        # Tabs for code files
        self.code_tabs = QTabWidget()
        self.code_tabs.setTabsClosable(True)
        self.code_tabs.tabCloseRequested.connect(self.close_tab)

        # Terminal output
        self.terminal_output = TerminalOutput()

        # Layout adjustments
        input_layout = QVBoxLayout()
        input_layout.addWidget(main_prompt_label)
        input_layout.addWidget(self.main_prompt_input)
        input_layout.addWidget(main_prompt_button)
        input_layout.addWidget(reset_prompt_button)
        input_layout.addWidget(self.prompt_tree)
        input_layout.addLayout(prompt_buttons_layout)
        input_layout.addWidget(self.text_input_window)
        input_layout.addWidget(send_button)

        workspace_layout = QVBoxLayout()
        workspace_layout.addWidget(self.tree_view)

        code_display_layout = QVBoxLayout()
        code_display_layout.addWidget(self.code_tabs)
        code_display_layout.addWidget(self.terminal_output)

        # Add all widgets to the main layout
        main_layout.addLayout(input_layout, 1)
        main_layout.addLayout(workspace_layout, 3)
        main_layout.addLayout(code_display_layout, 4)

        # Set the central widget of the main window
        self.setCentralWidget(main_widget)

        # Set up toolbar
        self.setup_toolbar()

        # Ensure a workspace is created at startup
        self.create_workspace()

    def setup_toolbar(self):
        # Create toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # Workspace action
        workspace_action = QAction("Create Workspace", self)
        workspace_action.setStatusTip("Create a new workspace")
        workspace_action.triggered.connect(self.create_workspace)
        toolbar.addAction(workspace_action)

        # Save Workflow
        save_workflow_action = QAction("Save Workflow", self)
        save_workflow_action.setStatusTip("Save current workflow with a custom name")
        save_workflow_action.triggered.connect(self.save_workflow_as)
        toolbar.addAction(save_workflow_action)

        # Load Workflow
        load_workflow_action = QAction("Load Workflow", self)
        load_workflow_action.setStatusTip("Load saved workflow and settings")
        load_workflow_action.triggered.connect(self.load_workflow)
        toolbar.addAction(load_workflow_action)

        # Add an icon for API configuration
        icon_path = "path/to/icon.png"  # Replace with the path to your icon
        icon_action = QAction(QIcon(icon_path), "Open API Configuration", self)
        icon_action.setStatusTip("Configure OpenAI API")
        icon_action.triggered.connect(self.open_configuration_window)
        toolbar.addAction(icon_action)

        # Main Prompt Management
        main_prompt_action = QAction("Main Prompt", self)
        main_prompt_action.setStatusTip("Manage main prompts")
        main_prompt_action.triggered.connect(self.open_main_prompt_management)
        toolbar.addAction(main_prompt_action)

        # Add URL or File References
        add_url_file_action = QAction("Add URL or File", self)
        add_url_file_action.setStatusTip("Manage URL and file references")
        add_url_file_action.triggered.connect(self.open_url_file_management)
        toolbar.addAction(add_url_file_action)

    def workspace_context_menu(self, position):
        index = self.tree_view.indexAt(position)
        if not index.isValid():
            return

        menu = QMenu()
        remove_action = QAction("Delete", self)
        remove_action.triggered.connect(lambda: self.remove_file_or_directory(index))
        menu.addAction(remove_action)
        menu.exec(self.tree_view.viewport().mapToGlobal(position))

    def remove_file_or_directory(self, index):
        file_path = self.model.filePath(index)
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
            self.log_to_terminal(f"Directory removed: {file_path}")
        else:
            os.remove(file_path)
            self.log_to_terminal(f"File removed: {file_path}")
        self.model.setRootPath(QDir.rootPath())
        self.tree_view.setRootIndex(self.model.index(self.workspace_path))

    def open_url_file_management(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage URL and File References")
        layout = QVBoxLayout(dialog)

        # URL management
        url_label = QLabel("Add URL:")
        url_input = QLineEdit()
        url_button = QPushButton("Add URL")
        url_list = QListWidget()
        url_list.addItems(self.url_references)
        url_button.clicked.connect(lambda: self.add_url(url_input.text(), url_list))

        url_remove_button = QPushButton("Remove URL")
        url_remove_button.clicked.connect(lambda: self.remove_selected(url_list, self.url_references))

        url_checkbox = QCheckBox("Use URLs")
        url_checkbox.setChecked(self.use_urls)
        url_checkbox.stateChanged.connect(lambda: self.toggle_urls(url_checkbox.isChecked()))

        layout.addWidget(url_label)
        layout.addWidget(url_input)
        layout.addWidget(url_button)
        layout.addWidget(url_remove_button)
        layout.addWidget(url_checkbox)
        layout.addWidget(url_list)

        # File management
        file_button = QPushButton("Add File")
        file_list = QListWidget()
        file_list.addItems(self.file_references)
        file_button.clicked.connect(lambda: self.add_file(file_list))

        file_remove_button = QPushButton("Remove File")
        file_remove_button.clicked.connect(lambda: self.remove_selected(file_list, self.file_references))

        file_checkbox = QCheckBox("Use Files")
        file_checkbox.setChecked(self.use_files)
        file_checkbox.stateChanged.connect(lambda: self.toggle_files(file_checkbox.isChecked()))

        layout.addWidget(file_button)
        layout.addWidget(file_remove_button)
        layout.addWidget(file_checkbox)
        layout.addWidget(file_list)

        dialog.setLayout(layout)
        dialog.exec()

    def add_url(self, url, url_list):
        if url:
            self.url_references.append(url)
            url_list.addItem(QListWidgetItem(url))

    def remove_selected(self, list_widget, reference_list):
        for item in list_widget.selectedItems():
            reference_list.remove(item.text())
            list_widget.takeItem(list_widget.row(item))

    def toggle_urls(self, use):
        self.use_urls = use

    def add_file(self, file_list):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "All Files (*);;PDF Files (*.pdf);;Word Files (*.docx)", options=options)
        for file in files:
            self.file_references.append(file)
            file_list.addItem(QListWidgetItem(file))

    def toggle_files(self, use):
        self.use_files = use

    def create_workspace(self):
        # Prompt for a new workspace directory
        workspace_name, ok = QInputDialog.getText(self, "New Workspace", "Enter workspace name:")
        if ok and workspace_name:
            os.makedirs(workspace_name, exist_ok=True)
            self.workspace_path = os.path.abspath(workspace_name)
            self.model.setRootPath(self.workspace_path)
            self.tree_view.setRootIndex(self.model.index(self.workspace_path))
            self.log_to_terminal(f"Workspace '{workspace_name}' created.")

    def set_main_prompt(self):
        self.current_main_prompt = self.main_prompt_input.text()

    def reset_main_prompt(self):
        self.current_main_prompt = self.default_main_prompt
        self.main_prompt_input.setText(self.default_main_prompt)

    def open_configuration_window(self):
        # Function to open a new window with input fields
        dialog = QDialog(self)
        dialog.setWindowTitle("OpenAI API Configuration")

        dialog_layout = QVBoxLayout()

        # Endpoint input
        endpoint_label = QLabel("API Base Endpoint:")
        endpoint_input = QLineEdit()
        endpoint_input.setText(self.api_endpoint_models)  # Set existing endpoint
        dialog_layout.addWidget(endpoint_label)
        dialog_layout.addWidget(endpoint_input)

        # API Key input
        key_label = QLabel("API Key:")
        key_input = QLineEdit()
        key_input.setEchoMode(QLineEdit.EchoMode.Password)
        key_input.setText(self.api_key)  # Set existing key
        dialog_layout.addWidget(key_label)
        dialog_layout.addWidget(key_input)

        # Dropdown for models
        model_label = QLabel("Select Model:")
        model_dropdown = QComboBox()
        dialog_layout.addWidget(model_label)
        dialog_layout.addWidget(model_dropdown)

        # Refresh button
        refresh_button = QPushButton("Refresh Models")
        refresh_button.clicked.connect(lambda: self.refresh_models(endpoint_input.text(), key_input.text(), model_dropdown))
        dialog_layout.addWidget(refresh_button)

        # Save button
        save_button = QPushButton("Save Configuration")
        save_button.clicked.connect(lambda: self.save_configuration(endpoint_input.text(), key_input.text(), model_dropdown.currentText()))
        dialog_layout.addWidget(save_button)

        dialog.setLayout(dialog_layout)
        dialog.exec()

    def refresh_models(self, endpoint, api_key, dropdown):
        # Headers setup
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        # Fetch and list models using requests
        try:
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            models = response.json().get('data', [])
            dropdown.clear()
            for model in models:
                dropdown.addItem(model['id'])
            if models:  # Automatically select the first model if available
                dropdown.setCurrentIndex(0)
        except Exception as e:
            dropdown.clear()
            dropdown.addItem(f"Error: {str(e)}")

    def save_configuration(self, endpoint, api_key, selected_model):
        self.api_endpoint_models = endpoint
        self.api_endpoint_completions = endpoint.replace("/v1/models", "/v1/completions")
        self.api_key = api_key
        self.selected_model = selected_model
        self.save_config()
        QMessageBox.information(self, "Configuration Saved", "API configuration has been saved successfully.")

    def open_main_prompt_management(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage Main Prompts")

        dialog_layout = QVBoxLayout()
        main_prompt_list = QListWidget()
        main_prompt_list.addItems(self.prompt_tree.get_prompt_list())
        main_prompt_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        dialog_layout.addWidget(main_prompt_list)

        button_layout = QHBoxLayout()
        add_button = QPushButton("+")
        add_button.clicked.connect(lambda: self.add_main_prompt(main_prompt_list))
        remove_button = QPushButton("−")
        remove_button.clicked.connect(lambda: self.remove_main_prompt(main_prompt_list))
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        dialog_layout.addLayout(button_layout)

        main_prompt_list.itemDoubleClicked.connect(lambda: self.set_prompt_from_list(main_prompt_list))

        dialog.setLayout(dialog_layout)
        dialog.exec()

    def add_main_prompt(self, main_prompt_list):
        text, ok = QInputDialog.getText(self, "Add Main Prompt", "Enter your main prompt:")
        if ok and text:
            main_prompt_list.addItem(text)
            self.prompt_tree.add_prompt_to_tree(QTreeWidgetItem([text]))

    def remove_main_prompt(self, main_prompt_list):
        selected_items = main_prompt_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.prompt_tree.main_prompts.remove(item.text())
            main_prompt_list.takeItem(main_prompt_list.row(item))

    def set_prompt_from_list(self, main_prompt_list):
        current_item = main_prompt_list.currentItem()
        if current_item:
            self.main_prompt_input.setText(current_item.text())

    def send_command(self):
        if not self.workspace_path:
            self.text_input_window.append("Please create a workspace first.")
            return

        if not self.selected_model:
            self.text_input_window.append("No model selected. Please configure and refresh models first.")
            return

        user_input = self.text_input_window.toPlainText().strip()
        if not user_input:
            self.text_input_window.append("Please enter a command.")
            return

        # Prepare to send the command to the selected AI model
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            response = requests.post(
                self.api_endpoint_completions,
                headers=headers,
                json={
                    "model": self.selected_model,
                    "prompt": self.modify_prompt_for_structure(user_input),
                    "max_tokens": 1500
                }
            )
            response.raise_for_status()
            choices = response.json().get('choices', [])
            if choices:
                reply = choices[0].get('text', '').strip()
                self.process_ai_response(reply)
            else:
                self.text_input_window.append("No response generated.")

            self.text_input_window.clear()  # Clear the text input after sending
        except Exception as e:
            self.text_input_window.append(f"Error: {str(e)}")

    def modify_prompt_for_structure(self, prompt):
        reference_text = ""
        if self.use_urls:
            reference_text += "Using the following URLs as references: "
            reference_text += ", ".join(self.url_references) + ". "
        if self.use_files:
            reference_text += "Using content from the following files: "
            reference_text += ", ".join(os.path.basename(file) for file in self.file_references) + ". "

        return (
            f"{self.current_main_prompt}\n"
            f"Analyze the existing project structure, including files and directories, in the workspace at: {self.workspace_path}. "
            f"{reference_text}"
            f"Ensure that any generated code integrates seamlessly into the current project structure. The task is: {prompt}. "
            "You must decide where each part of the code should go, create or modify files and directories using appropriate file system commands, "
            "and ensure everything fits together. Log each step you take in the terminal."
        )

    def log_to_terminal(self, message):
        self.terminal_output.appendPlainText(message)

    def process_ai_response(self, response):
        # Process AI instructions for file operations
        lines = response.strip().split("\n")
        current_file = None
        file_contents = []

        for line in lines:
            line = line.strip()
            if len(line) == 0:
                continue

            if line.startswith("mkdir"):
                dir_path = line.split(" ", 1)[1]
                full_dir_path = os.path.join(self.workspace_path, dir_path)
                os.makedirs(full_dir_path, exist_ok=True)
                self.log_to_terminal(f"Directory created: {full_dir_path}")

            elif line.startswith("touch"):
                file_path = line.split(" ", 1)[1]
                full_file_path = os.path.join(self.workspace_path, file_path)
                open(full_file_path, 'a').close()
                self.log_to_terminal(f"File created: {full_file_path}")

            elif line.startswith("echo"):
                parts = line.split(">", 1)
                if len(parts) < 2:
                    continue

                file_content = parts[0].replace("echo ", "").strip()
                target_file = parts[1].strip()

                full_file_path = os.path.join(self.workspace_path, target_file)
                try:
                    with open(full_file_path, 'a', encoding='utf-8') as f:
                        f.write(file_content + "\n")
                    self.log_to_terminal(f"Content written to {full_file_path}")
                except OSError as e:
                    self.log_to_terminal(f"Error writing to file {full_file_path}: {e}")

            elif line.startswith("# File:"):
                if current_file and file_contents:
                    self.write_to_file(current_file, file_contents)
                current_file = line.split(":", 1)[1].strip()
                file_contents = []

            elif current_file:
                file_contents.append(line)

        if current_file and file_contents:
            self.write_to_file(current_file, file_contents)

        self.model.setRootPath(QDir.rootPath())  # Refresh the view
        self.tree_view.setRootIndex(self.model.index(self.workspace_path))

    def write_to_file(self, file_path, contents):
        full_file_path = os.path.join(self.workspace_path, file_path)
        try:
            with open(full_file_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(contents) + "\n")
            self.log_to_terminal(f"File written: {full_file_path}")
            self.display_code_in_editor(file_path, contents)  # Show the file content in the code editor
        except OSError as e:
            self.log_to_terminal(f"Error writing to file {full_file_path}: {e}")

    def display_code_in_editor(self, file_path, code):
        code_editor = CodeEditor()
        code_editor.setPlainText("\n".join(code))

        self.code_tabs.addTab(code_editor, os.path.basename(file_path))
        self.apply_dark_theme(code_editor)

    def open_file_from_tree(self, index):
        file_path = self.model.filePath(index)
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.readlines()
                self.display_code_in_editor(file_path, content)
            except Exception as e:
                self.log_to_terminal(f"Error opening file {file_path}: {e}")

    def apply_dark_theme(self, text_edit):
        # Set dark theme for QTextEdit
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        text_edit.setPalette(palette)

    def close_tab(self, index):
        widget = self.code_tabs.widget(index)
        if widget is not None:
            widget.deleteLater()
        self.code_tabs.removeTab(index)

    def populate_input_from_prompt(self, item):
        self.text_input_window.setText(item.text(0))

    def add_prompt(self):
        text, ok = QInputDialog.getText(self, "Add Prompt", "Enter your prompt:")
        if ok and text:
            current_item = self.prompt_tree.currentItem()
            prompt_item = QTreeWidgetItem([text])
            prompt_item.setExpanded(False)  # Ensure new prompts are collapsed
            if current_item and current_item.parent() is not None:
                # Add as a child to the current folder
                current_item.addChild(prompt_item)
            else:
                # Add to the root if no folder is selected
                self.prompt_tree.addTopLevelItem(prompt_item)

    def add_folder(self):
        folder_name, ok = QInputDialog.getText(self, "Add Folder", "Enter folder name:")
        if ok and folder_name:
            folder_item = QTreeWidgetItem([folder_name])
            folder_item.setFlags(folder_item.flags() | Qt.ItemFlag.ItemIsDropEnabled)
            folder_item.setExpanded(False)  # Ensure new folders are collapsed
            self.prompt_tree.addTopLevelItem(folder_item)

    def remove_prompt(self):
        current_item = self.prompt_tree.currentItem()
        if current_item and current_item.parent() is not None:
            parent = current_item.parent()
            index = parent.indexOfChild(current_item)
            parent.takeChild(index)
        elif current_item:
            index = self.prompt_tree.indexOfTopLevelItem(current_item)
            self.prompt_tree.takeTopLevelItem(index)

    def get_prompts(self):
        return [
            "Generate a Flask server with a simple user interface.",
            "Create a PyQt6 GUI application with a main window and interactive elements.",
            "Add button functionality to the existing interface.",
            "Set up an API endpoint using Flask for data handling.",
            "Implement API key-based authentication for secure access.",
            "Develop the backend logic for handling user requests and responses.",
            "Design a database schema for storing user data.",
            "Integrate a REST API with CRUD operations.",
            "Create unit tests for API endpoints.",
            "Develop a real-time chat application component.",
            "Implement OAuth2 for user authentication.",
            "Set up a Docker container for deployment.",
            "Design a responsive frontend using HTML/CSS.",
            "Create a login and registration system.",
            "Add session management functionality.",
            "Build a dashboard for data visualization.",
            "Implement logging and error handling.",
            "Integrate a payment gateway like Stripe.",
            "Set up WebSocket for live updates.",
            "Develop a file upload feature.",
            "Create a user profile management system.",
            "Add search functionality with filtering.",
            "Implement caching for improved performance.",
            "Design a notification system using Webhooks.",
            "Integrate third-party services via API.",
            "Build an admin panel for managing users and content."
        ]

    def load_config(self):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.api_endpoint_models = config.get('api_endpoint_models', "https://api.openai.com/v1/models")
                self.api_endpoint_completions = self.api_endpoint_models.replace("/v1/models", "/v1/completions")
                self.api_key = config.get('api_key', "")
                self.selected_model = config.get('selected_model', "")
        except FileNotFoundError:
            self.api_endpoint_models = "https://api.openai.com/v1/models"
            self.api_endpoint_completions = self.api_endpoint_models.replace("/v1/models", "/v1/completions")
            self.api_key = ""
            self.selected_model = ""

    def save_config(self):
        config = {
            'api_endpoint_models': self.api_endpoint_models,
            'api_key': self.api_key,
            'selected_model': self.selected_model
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)

    def load_workflow(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Workflow", "", "Workflow Files (*.json)")
        if file_name:
            try:
                with open(file_name, 'r') as f:
                    workflow = json.load(f)
                    self.url_references = workflow.get('url_references', [])
                    self.file_references = workflow.get('file_references', [])
                    self.use_urls = workflow.get('use_urls', False)
                    self.use_files = workflow.get('use_files', False)
                    self.selected_model = workflow.get('selected_model', "")
                    self.prompt_tree.load_from_json(workflow.get('prompts', []))
                    self.workspace_path = workflow.get('workspace_path', None)
                    self.set_open_tabs(workflow.get('open_tabs', []))
                    self.terminal_output.setPlainText(workflow.get('terminal_output', ""))
                self.update_ui_from_workflow()
            except FileNotFoundError:
                QMessageBox.warning(self, "Load Workflow", "Failed to load the selected workflow file.")

    def set_open_tabs(self, open_tabs):
        self.code_tabs.clear()
        for tab_data in open_tabs:
            editor = CodeEditor()
            editor.setPlainText(tab_data['content'])
            self.code_tabs.addTab(editor, tab_data['title'])
            self.apply_dark_theme(editor)

    def save_workflow_as(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Workflow As", "", "Workflow Files (*.json)")
        if file_name:
            workflow = {
                'url_references': self.url_references,
                'file_references': self.file_references,
                'use_urls': self.use_urls,
                'use_files': self.use_files,
                'selected_model': self.selected_model,
                'prompts': self.prompt_tree.save_to_json(),  # Save the current state of prompts
                'workspace_path': self.workspace_path,
                'open_tabs': self.get_open_tabs(),
                'terminal_output': self.terminal_output.toPlainText()
            }
            with open(file_name, 'w') as f:
                json.dump(workflow, f)
            QMessageBox.information(self, "Save Workflow", "Workflow and settings have been saved.")
            self.save_config()  # Also save the current configuration

    def get_open_tabs(self):
        tabs = []
        for i in range(self.code_tabs.count()):
            editor = self.code_tabs.widget(i)
            tabs.append({
                'title': self.code_tabs.tabText(i),
                'content': editor.toPlainText()
            })
        return tabs

    def update_ui_from_workflow(self):
        self.main_prompt_input.setText(self.current_main_prompt)
        if self.workspace_path:
            self.model.setRootPath(self.workspace_path)
            self.tree_view.setRootIndex(self.model.index(self.workspace_path))
        QMessageBox.information(self, "Workflow Loaded", "Workflow settings have been loaded.")

class PromptTree(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setHeaderHidden(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setItemsExpandable(True)
        self.setExpandsOnDoubleClick(True)

    def add_prompt_to_tree(self, item):
        self.addTopLevelItem(item)
        item.setExpanded(False)  # Ensure all items are initially collapsed

    def get_prompt_list(self):
        def collect_prompts(item):
            prompts = []
            for i in range(item.childCount()):
                prompts.append(item.child(i).text(0))
                prompts.extend(collect_prompts(item.child(i)))
            return prompts

        prompts = []
        for i in range(self.topLevelItemCount()):
            top_item = self.topLevelItem(i)
            prompts.append(top_item.text(0))
            prompts.extend(collect_prompts(top_item))
        return prompts

    def save_to_json(self):
        def serialize_item(item):
            return {
                'text': item.text(0),
                'children': [serialize_item(item.child(i)) for i in range(item.childCount())]
            }

        return [serialize_item(self.topLevelItem(i)) for i in range(self.topLevelItemCount())]

    def load_from_json(self, data):
        def deserialize_item(data):
            item = QTreeWidgetItem([data['text']])
            for child_data in data['children']:
                item.addChild(deserialize_item(child_data))
            return item

        self.clear()
        for item_data in data:
            self.addTopLevelItem(deserialize_item(item_data))
            self.expandItem(self.topLevelItem(self.topLevelItemCount() - 1))

app = QApplication(sys.argv)
window = MainWindow()
window.setWindowTitle('PyQt6 Code Editor with Workspace and Terminal')
window.resize(1200, 800)
window.show()
sys.exit(app.exec())
