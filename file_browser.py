"""
File Browser for navigating and managing Python strategy files.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
                              QTreeWidgetItemIterator, QMenu, QLabel)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QBrush
import os
from pathlib import Path


class FileBrowser(QWidget):
    """File browser widget for strategy files."""
    
    # Signals
    file_selected = pyqtSignal(str)  # Emits file path when selected
    execute_requested = pyqtSignal(str)  # Emits file path to execute
    view_results_requested = pyqtSignal(str)  # Emits file path to view results
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_folder = None
        self.file_status = {}  # Track execution status: not_run, running, completed, failed
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        self.header_label = QLabel("Strategy Files")
        self.header_label.setStyleSheet("""
            QLabel {
                background-color: #2D2D30;
                color: #CCCCCC;
                padding: 8px;
                font-weight: bold;
                border-bottom: 1px solid #3E3E42;
            }
        """)
        layout.addWidget(self.header_label)
        
        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["File", "Status"])
        self.tree.setColumnWidth(0, 250)
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: #252526;
                color: #CCCCCC;
                border: none;
                outline: none;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QTreeWidget::item:selected {
                background-color: #094771;
            }
            QTreeWidget::item:hover {
                background-color: #2A2D2E;
            }
        """)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)
        self.tree.itemClicked.connect(self._on_item_clicked)
        
        layout.addWidget(self.tree)
    
    def set_folder(self, folder_path):
        """Set the folder to browse and populate the tree."""
        self.current_folder = folder_path
        self._populate_tree()
        self.header_label.setText(f"Strategy Files - {Path(folder_path).name}")
    
    def _populate_tree(self):
        """Populate tree widget with Python files from the folder."""
        self.tree.clear()
        
        if not self.current_folder or not os.path.exists(self.current_folder):
            return
        
        # Walk through directory
        self._add_directory_items(self.current_folder, self.tree.invisibleRootItem())
    
    def _add_directory_items(self, directory, parent_item):
        """Recursively add directory items to tree."""
        try:
            items = sorted(os.listdir(directory))
        except PermissionError:
            return
        
        # Separate directories and files
        dirs = []
        files = []
        
        for item_name in items:
            item_path = os.path.join(directory, item_name)
            if os.path.isdir(item_path):
                dirs.append((item_name, item_path))
            elif item_name.endswith('.py'):
                files.append((item_name, item_path))
        
        # Add directories first
        for dir_name, dir_path in dirs:
            dir_item = QTreeWidgetItem(parent_item, [dir_name, ""])
            dir_item.setData(0, Qt.ItemDataRole.UserRole, dir_path)
            dir_item.setForeground(0, QBrush(QColor("#4EC9B0")))
            self._add_directory_items(dir_path, dir_item)
        
        # Add Python files
        for file_name, file_path in files:
            file_item = QTreeWidgetItem(parent_item, [file_name, "Not Run"])
            file_item.setData(0, Qt.ItemDataRole.UserRole, file_path)
            file_item.setForeground(0, QBrush(QColor("#DCDCAA")))
            
            # Set initial status
            self.file_status[file_path] = "not_run"
            self._update_item_status(file_item, "not_run")
    
    def _on_item_clicked(self, item, column):
        """Handle item click event."""
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if file_path and os.path.isfile(file_path):
            self.file_selected.emit(file_path)
    
    def _show_context_menu(self, position):
        """Show context menu for tree items."""
        item = self.tree.itemAt(position)
        if not item:
            return
        
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if not file_path or not os.path.isfile(file_path):
            return
        
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #252526;
                color: #CCCCCC;
                border: 1px solid #3E3E42;
            }
            QMenu::item:selected {
                background-color: #094771;
            }
        """)
        
        execute_action = menu.addAction("Execute Script")
        view_results_action = menu.addAction("View Results")
        menu.addSeparator()
        open_location_action = menu.addAction("Open File Location")
        
        action = menu.exec(self.tree.viewport().mapToGlobal(position))
        
        if action == execute_action:
            self.execute_requested.emit(file_path)
        elif action == view_results_action:
            self.view_results_requested.emit(file_path)
        elif action == open_location_action:
            self._open_file_location(file_path)
    
    def _open_file_location(self, file_path):
        """Open the file's directory in file explorer."""
        import subprocess
        directory = os.path.dirname(file_path)
        subprocess.Popen(f'explorer /select,"{file_path}"')
    
    def update_file_status(self, file_path, status):
        """Update the execution status of a file.
        
        Args:
            file_path: Path to the file
            status: One of 'not_run', 'running', 'completed', 'failed'
        """
        self.file_status[file_path] = status
        
        # Find the item in the tree and update it
        iterator = QTreeWidgetItemIterator(self.tree)
        while iterator.value():
            item = iterator.value()
            item_path = item.data(0, Qt.ItemDataRole.UserRole)
            if item_path == file_path:
                self._update_item_status(item, status)
                break
            iterator += 1
    
    def _update_item_status(self, item, status):
        """Update the visual status of a tree item."""
        status_text = {
            'not_run': 'Not Run',
            'running': 'Running...',
            'completed': 'Completed',
            'failed': 'Failed'
        }
        
        status_color = {
            'not_run': QColor("#858585"),
            'running': QColor("#4A9EFF"),
            'completed': QColor("#4EC9B0"),
            'failed': QColor("#F48771")
        }
        
        item.setText(1, status_text.get(status, status))
        item.setForeground(1, QBrush(status_color.get(status, QColor("#CCCCCC"))))
    
    def add_file(self, file_path):
        """Add a single file to the browser."""
        if not file_path.endswith('.py'):
            return
        
        # Check if file already exists in tree
        iterator = QTreeWidgetItemIterator(self.tree)
        while iterator.value():
            item = iterator.value()
            if item.data(0, Qt.ItemDataRole.UserRole) == file_path:
                return  # Already exists
            iterator += 1
        
        # Add to root
        file_name = Path(file_path).name
        file_item = QTreeWidgetItem(self.tree, [file_name, "Not Run"])
        file_item.setData(0, Qt.ItemDataRole.UserRole, file_path)
        file_item.setForeground(0, QBrush(QColor("#DCDCAA")))
        self.file_status[file_path] = "not_run"

