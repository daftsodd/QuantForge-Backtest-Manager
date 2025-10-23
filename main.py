"""
QuantForge Backtest Manager
Main application window and entry point.
"""
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QSplitter, QTextEdit, QFileDialog,
                              QMessageBox, QMenuBar, QMenu, QStatusBar)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon, QFont

from config_manager import ConfigManager
from file_browser import FileBrowser
from code_viewer import CodeViewer
from execution_engine import ExecutionEngine
from progress_widget import ProgressWidget
from results_parser import ResultsParser
from results_viewer import ResultsViewer


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.execution_engine = ExecutionEngine()
        self.results_parser = ResultsParser()
        self.current_folder = None
        self.current_file = None
        
        self._init_ui()
        self._connect_signals()
        self._restore_state()
    
    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("QuantForge Backtest Manager")
        self.setMinimumSize(QSize(1200, 800))
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Central widget with main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Main splitter (left panel | right panels)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel: File browser
        self.file_browser = FileBrowser()
        main_splitter.addWidget(self.file_browser)
        
        # Right side: vertical splitter
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Top right: Code viewer
        self.code_viewer = CodeViewer()
        right_splitter.addWidget(self.code_viewer)
        
        # Middle right: Execution panel (console output + progress)
        execution_panel = self._create_execution_panel()
        right_splitter.addWidget(execution_panel)
        
        # Bottom right: Results viewer
        self.results_viewer = ResultsViewer()
        right_splitter.addWidget(self.results_viewer)
        
        # Set initial sizes for right splitter (40%, 30%, 30%)
        right_splitter.setSizes([400, 300, 300])
        
        main_splitter.addWidget(right_splitter)
        
        # Set initial sizes for main splitter (25%, 75%)
        main_splitter.setSizes([300, 900])
        
        main_layout.addWidget(main_splitter)
        
        # Store splitters for state saving
        self.main_splitter = main_splitter
        self.right_splitter = right_splitter
        
        # Apply dark theme stylesheet
        self._apply_stylesheet()
    
    def _create_menu_bar(self):
        """Create the menu bar."""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        open_folder_action = QAction("&Open Folder...", self)
        open_folder_action.setShortcut("Ctrl+O")
        open_folder_action.triggered.connect(self._open_folder)
        file_menu.addAction(open_folder_action)
        
        import_file_action = QAction("&Import File...", self)
        import_file_action.setShortcut("Ctrl+I")
        import_file_action.triggered.connect(self._import_file)
        file_menu.addAction(import_file_action)
        
        import_folder_action = QAction("Import Folder...", self)
        import_folder_action.triggered.connect(self._import_folder)
        file_menu.addAction(import_folder_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menu_bar.addMenu("&View")
        
        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._refresh_view)
        view_menu.addAction(refresh_action)
        
        clear_results_action = QAction("&Clear Results", self)
        clear_results_action.triggered.connect(self._clear_results)
        view_menu.addAction(clear_results_action)
        
        # Execute menu
        execute_menu = menu_bar.addMenu("&Execute")
        
        run_script_action = QAction("&Run Current Script", self)
        run_script_action.setShortcut("F5")
        run_script_action.triggered.connect(self._execute_current_script)
        execute_menu.addAction(run_script_action)
        
        stop_execution_action = QAction("&Stop Execution", self)
        stop_execution_action.setShortcut("Ctrl+C")
        stop_execution_action.triggered.connect(self._stop_execution)
        execute_menu.addAction(stop_execution_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_execution_panel(self):
        """Create the execution panel with console and progress."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        from PyQt6.QtWidgets import QLabel
        header = QLabel("Execution Console")
        header.setStyleSheet("""
            QLabel {
                background-color: #2D2D30;
                color: #CCCCCC;
                padding: 8px;
                font-weight: bold;
                border-bottom: 1px solid #3E3E42;
            }
        """)
        layout.addWidget(header)
        
        # Progress widget
        self.progress_widget = ProgressWidget()
        layout.addWidget(self.progress_widget)
        
        # Console output
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setFont(QFont("Consolas", 9))
        self.console_output.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #CCCCCC;
                border: none;
                padding: 10px;
            }
        """)
        layout.addWidget(self.console_output)
        
        return panel
    
    def _connect_signals(self):
        """Connect signals and slots."""
        # File browser signals
        self.file_browser.file_selected.connect(self._on_file_selected)
        self.file_browser.execute_requested.connect(self._execute_script)
        self.file_browser.view_results_requested.connect(self._view_results)
        
        # Execution engine signals
        self.execution_engine.output_received.connect(self._on_output_received)
        self.execution_engine.execution_started.connect(self._on_execution_started)
        self.execution_engine.execution_finished.connect(self._on_execution_finished)
        self.execution_engine.progress_update.connect(self._on_progress_update)
    
    def _apply_stylesheet(self):
        """Apply application-wide stylesheet."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
            }
            QMenuBar {
                background-color: #2D2D30;
                color: #CCCCCC;
                border-bottom: 1px solid #3E3E42;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #3E3E42;
            }
            QMenu {
                background-color: #252526;
                color: #CCCCCC;
                border: 1px solid #3E3E42;
            }
            QMenu::item:selected {
                background-color: #094771;
            }
            QStatusBar {
                background-color: #007ACC;
                color: #FFFFFF;
            }
            QSplitter::handle {
                background-color: #3E3E42;
            }
            QSplitter::handle:horizontal {
                width: 2px;
            }
            QSplitter::handle:vertical {
                height: 2px;
            }
        """)
    
    def _restore_state(self):
        """Restore window state from configuration."""
        geometry = self.config_manager.get("window_geometry", {})
        self.setGeometry(
            geometry.get("x", 100),
            geometry.get("y", 100),
            geometry.get("width", 1400),
            geometry.get("height", 900)
        )
        
        # Load last folder
        last_folder = self.config_manager.get("last_folder", "")
        if last_folder:
            self.file_browser.set_folder(last_folder)
            self.current_folder = last_folder
            self.status_bar.showMessage(f"Loaded folder: {last_folder}")
    
    def _save_state(self):
        """Save window state to configuration."""
        geometry = self.geometry()
        self.config_manager.set("window_geometry", {
            "x": geometry.x(),
            "y": geometry.y(),
            "width": geometry.width(),
            "height": geometry.height()
        })
        
        if self.current_folder:
            self.config_manager.set("last_folder", self.current_folder)
    
    def _open_folder(self):
        """Open a folder for browsing."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Strategy Folder",
            self.current_folder or ""
        )
        
        if folder:
            self.current_folder = folder
            self.file_browser.set_folder(folder)
            self.config_manager.add_recent_folder(folder)
            self.status_bar.showMessage(f"Opened folder: {folder}")
    
    def _import_file(self):
        """Import a single Python file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Python File",
            "",
            "Python Files (*.py)"
        )
        
        if file_path:
            self.file_browser.add_file(file_path)
            self.status_bar.showMessage(f"Imported file: {file_path}")
    
    def _import_folder(self):
        """Import an additional folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Import Folder",
            self.current_folder or ""
        )
        
        if folder:
            # If no folder is set, make this the main folder
            if not self.current_folder:
                self.current_folder = folder
                self.file_browser.set_folder(folder)
            else:
                # Add all Python files from the folder
                import os
                from pathlib import Path
                for root, dirs, files in os.walk(folder):
                    for file in files:
                        if file.endswith('.py'):
                            file_path = os.path.join(root, file)
                            self.file_browser.add_file(file_path)
            
            self.status_bar.showMessage(f"Imported folder: {folder}")
    
    def _refresh_view(self):
        """Refresh the current view."""
        if self.current_folder:
            self.file_browser.set_folder(self.current_folder)
        self.status_bar.showMessage("View refreshed")
    
    def _clear_results(self):
        """Clear results display."""
        self.results_viewer.clear()
        self.status_bar.showMessage("Results cleared")
    
    def _on_file_selected(self, file_path):
        """Handle file selection."""
        self.current_file = file_path
        self.code_viewer.load_file(file_path)
        self.status_bar.showMessage(f"Viewing: {file_path}")
    
    def _execute_current_script(self):
        """Execute the currently selected script."""
        if self.current_file:
            self._execute_script(self.current_file)
        else:
            QMessageBox.warning(self, "No Script Selected", 
                              "Please select a script to execute.")
    
    def _execute_script(self, script_path):
        """Execute a script."""
        if self.execution_engine.is_running():
            QMessageBox.warning(self, "Execution in Progress",
                              "Another script is currently running. Please wait.")
            return
        
        # Clear console
        self.console_output.clear()
        
        # Update status
        self.file_browser.update_file_status(script_path, 'running')
        self.status_bar.showMessage(f"Executing: {script_path}")
        
        # Start execution
        self.execution_engine.execute_script(script_path)
    
    def _stop_execution(self):
        """Stop the current execution."""
        if self.execution_engine.is_running():
            reply = QMessageBox.question(
                self,
                "Stop Execution",
                "Are you sure you want to stop the current execution?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.execution_engine.terminate()
                self.status_bar.showMessage("Execution stopped")
    
    def _view_results(self, script_path):
        """View results for a script."""
        results = self.results_parser.parse_results(script_path)
        self.results_viewer.display_results(results)
        self.status_bar.showMessage(f"Viewing results for: {script_path}")
    
    def _on_output_received(self, output):
        """Handle output from execution."""
        self.console_output.append(output)
        # Auto-scroll to bottom
        self.console_output.verticalScrollBar().setValue(
            self.console_output.verticalScrollBar().maximum()
        )
    
    def _on_execution_started(self, script_path):
        """Handle execution start."""
        from pathlib import Path
        self.progress_widget.start_execution(Path(script_path).name)
    
    def _on_execution_finished(self, script_path, success):
        """Handle execution completion."""
        self.progress_widget.stop_execution(success)
        
        # Update file status
        status = 'completed' if success else 'failed'
        self.file_browser.update_file_status(script_path, status)
        
        # Automatically load results if successful
        if success:
            self._view_results(script_path)
            self.status_bar.showMessage(f"Execution completed: {script_path}")
        else:
            self.status_bar.showMessage(f"Execution failed: {script_path}")
    
    def _on_progress_update(self, output):
        """Handle progress updates from execution output."""
        self.progress_widget.update_from_output(output)
    
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About QuantForge Backtest Manager",
            "<h2>QuantForge Backtest Manager</h2>"
            "<p>Version 1.0</p>"
            "<p>A professional tool for managing and visualizing "
            "quantitative trading strategy backtests.</p>"
            "<p>Built with PyQt6</p>"
        )
    
    def closeEvent(self, event):
        """Handle window close event."""
        self._save_state()
        event.accept()


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("QuantForge Backtest Manager")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

