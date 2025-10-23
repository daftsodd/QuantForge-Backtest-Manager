"""
Execution Engine for running Python scripts.
"""
from PyQt6.QtCore import QObject, QProcess, pyqtSignal
from pathlib import Path
import json
import time


class ExecutionEngine(QObject):
    """Manages script execution using QProcess."""
    
    # Signals
    output_received = pyqtSignal(str)  # Emits stdout/stderr output
    execution_started = pyqtSignal(str)  # Emits script path
    execution_finished = pyqtSignal(str, bool)  # Emits script path and success status
    progress_update = pyqtSignal(str)  # Emits progress text for parsing
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = None
        self.current_script = None
        self.start_time = None
        self.output_buffer = []
    
    def execute_script(self, script_path):
        """Execute a Python script."""
        if self.is_running():
            self.output_received.emit("ERROR: Another script is already running.\n")
            return
        
        self.current_script = script_path
        self.start_time = time.time()
        self.output_buffer = []
        
        # Create QProcess
        self.process = QProcess()
        self.process.setWorkingDirectory(str(Path(script_path).parent))
        
        # Connect signals
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.finished.connect(self._handle_finished)
        
        # Start the process
        self.execution_started.emit(script_path)
        self.output_received.emit(f"=== Executing: {Path(script_path).name} ===\n")
        self.output_received.emit(f"Working directory: {Path(script_path).parent}\n\n")
        
        # Use python or python3 depending on system
        self.process.start("python", [script_path])
    
    def _handle_stdout(self):
        """Handle standard output from the process."""
        if self.process:
            data = self.process.readAllStandardOutput()
            text = bytes(data).decode('utf-8', errors='replace')
            self.output_buffer.append(text)
            self.output_received.emit(text)
            self.progress_update.emit(text)
    
    def _handle_stderr(self):
        """Handle standard error from the process."""
        if self.process:
            data = self.process.readAllStandardError()
            text = bytes(data).decode('utf-8', errors='replace')
            self.output_buffer.append(text)
            self.output_received.emit(text)
            self.progress_update.emit(text)  # tqdm often writes to stderr
    
    def _handle_finished(self, exit_code, exit_status):
        """Handle process completion."""
        elapsed_time = time.time() - self.start_time
        success = (exit_code == 0 and exit_status == QProcess.ExitStatus.NormalExit)
        
        self.output_received.emit(f"\n\n=== Execution {'completed' if success else 'failed'} ===\n")
        self.output_received.emit(f"Exit code: {exit_code}\n")
        self.output_received.emit(f"Elapsed time: {elapsed_time:.2f} seconds\n")
        
        # Save execution metadata
        self._save_execution_metadata(success, elapsed_time, exit_code)
        
        # Emit finished signal
        self.execution_finished.emit(self.current_script, success)
        
        # Cleanup
        self.process = None
    
    def _save_execution_metadata(self, success, elapsed_time, exit_code):
        """Save execution metadata to JSON file."""
        if not self.current_script:
            return
        
        metadata = {
            "script_path": self.current_script,
            "timestamp": time.time(),
            "success": success,
            "elapsed_time": elapsed_time,
            "exit_code": exit_code,
            "output": ''.join(self.output_buffer)
        }
        
        script_dir = Path(self.current_script).parent
        script_name = Path(self.current_script).stem
        metadata_file = script_dir / f"{script_name}_execution.json"
        
        try:
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=4)
        except Exception as e:
            self.output_received.emit(f"Warning: Could not save execution metadata: {e}\n")
    
    def is_running(self):
        """Check if a script is currently running."""
        return self.process is not None and self.process.state() == QProcess.ProcessState.Running
    
    def terminate(self):
        """Terminate the currently running process."""
        if self.is_running():
            self.output_received.emit("\n=== Terminating execution ===\n")
            self.process.terminate()
            self.process.waitForFinished(3000)
            if self.process.state() == QProcess.ProcessState.Running:
                self.process.kill()

