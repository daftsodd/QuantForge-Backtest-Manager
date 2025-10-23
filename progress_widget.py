"""
Progress Widget for tracking script execution.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QProgressBar, QLabel
from PyQt6.QtCore import Qt, QTimer, QTime
import re


class ProgressWidget(QWidget):
    """Widget for displaying execution progress."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_time = None
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_elapsed_time)
        
        # Track total progress across chunks
        self.total_chunks = 0
        self.completed_chunks = 0
        self.current_chunk_progress = 0
        self.last_chunk_items = (0, 0)  # (current, total)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #CCCCCC;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3E3E42;
                border-radius: 3px;
                background-color: #1E1E1E;
                color: #CCCCCC;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #0E639C;
                border-radius: 2px;
            }
        """)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Time and info layout
        info_layout = QHBoxLayout()
        
        self.elapsed_label = QLabel("Elapsed: 00:00:00")
        self.elapsed_label.setStyleSheet("QLabel { color: #858585; font-size: 11px; }")
        info_layout.addWidget(self.elapsed_label)
        
        info_layout.addStretch()
        
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("QLabel { color: #858585; font-size: 11px; }")
        info_layout.addWidget(self.info_label)
        
        layout.addLayout(info_layout)
    
    def start_execution(self, script_name):
        """Start tracking execution."""
        self.start_time = QTime.currentTime()
        self.timer.start(1000)  # Update every second
        self.status_label.setText(f"Executing: {script_name}")
        self.progress_bar.setValue(0)
        self.info_label.setText("")
        
        # Reset tracking variables
        self.total_chunks = 0
        self.completed_chunks = 0
        self.current_chunk_progress = 0
        self.last_chunk_items = (0, 0)
    
    def stop_execution(self, success=True):
        """Stop tracking execution."""
        self.timer.stop()
        if success:
            self.status_label.setText("Execution completed successfully")
            self.progress_bar.setValue(100)
        else:
            self.status_label.setText("Execution failed")
    
    def reset(self):
        """Reset the progress widget."""
        self.timer.stop()
        self.status_label.setText("Ready")
        self.progress_bar.setValue(0)
        self.elapsed_label.setText("Elapsed: 00:00:00")
        self.info_label.setText("")
        self.start_time = None
        
        # Reset tracking
        self.total_chunks = 0
        self.completed_chunks = 0
        self.current_chunk_progress = 0
        self.last_chunk_items = (0, 0)
    
    def update_from_output(self, output_text):
        """Parse output text and update progress if possible."""
        # Clean the output text (remove carriage returns and other control chars)
        cleaned_text = output_text.replace('\r', '\n').strip()
        
        # Try to detect tqdm-style progress bar first: "Chunk:  45%|████| 225/500"
        # Pattern: optional text, percentage, pipe chars, fraction
        tqdm_pattern = re.search(r'(\d+)%\|[█░\-\s]*\|\s*(\d+)/(\d+)', cleaned_text)
        if tqdm_pattern:
            chunk_progress = int(tqdm_pattern.group(1))
            current = int(tqdm_pattern.group(2))
            total = int(tqdm_pattern.group(3))
            
            # Update chunk tracking
            self._update_chunk_progress(chunk_progress, current, total)
            return
        
        # Try simpler tqdm pattern: "XX%|" or just "XX%" followed by bar
        percentage_bar_match = re.search(r'(\d+)%\|', cleaned_text)
        if percentage_bar_match:
            chunk_progress = int(percentage_bar_match.group(1))
            self._update_chunk_progress(chunk_progress, 0, 0)
            return
        
        # Try to detect standalone "X/Y" pattern (like 225/500)
        fraction_match = re.search(r'\b(\d+)/(\d+)\b', cleaned_text)
        if fraction_match:
            current = int(fraction_match.group(1))
            total = int(fraction_match.group(2))
            if total > 0 and total >= current:  # Sanity check
                chunk_progress = int((current / total) * 100)
                self._update_chunk_progress(chunk_progress, current, total)
                return
        
        # Try to detect simple percentage: "XX%"
        percentage_match = re.search(r'\b(\d+)%', cleaned_text)
        if percentage_match:
            chunk_progress = int(percentage_match.group(1))
            if chunk_progress <= 100:  # Sanity check
                self._update_chunk_progress(chunk_progress, 0, 0)
    
    def _update_chunk_progress(self, chunk_progress, current_items, total_items):
        """Update progress based on chunk completion."""
        # Detect if we've moved to a new chunk (progress went back to low value or items reset)
        if chunk_progress < 10 and self.current_chunk_progress > 90:
            self.completed_chunks += 1
        elif total_items > 0 and current_items < 50 and self.last_chunk_items[0] > total_items - 50:
            # Items reset to low value - new chunk started
            self.completed_chunks += 1
        
        self.current_chunk_progress = chunk_progress
        
        # Store item counts if provided
        if total_items > 0:
            self.last_chunk_items = (current_items, total_items)
            # Estimate total chunks from chunk size
            # For 100x100 parameter sweep with chunk_size=500: 10000/500 = 20 chunks
            if self.total_chunks == 0 and total_items > 0:
                # Assume standard chunk size of 500 for 100x100 grid = 20 chunks
                estimated_chunks = 20
                self.total_chunks = estimated_chunks
        
        # Calculate total progress
        if self.total_chunks > 0:
            # Overall progress = completed chunks + current chunk progress
            total_progress = ((self.completed_chunks + (chunk_progress / 100.0)) / self.total_chunks) * 100
            total_progress = min(int(total_progress), 99)  # Never show 100% until truly done
        else:
            # If we don't know total chunks, show chunk progress
            total_progress = chunk_progress
        
        self.progress_bar.setValue(total_progress)
        
        # Update info label with chunk info and ETA
        info_parts = []
        
        # Show chunk progress
        if self.total_chunks > 0:
            current_chunk = min(self.completed_chunks + 1, self.total_chunks)
            info_parts.append(f"Chunk {current_chunk}/{self.total_chunks}")
        elif self.completed_chunks > 0:
            info_parts.append(f"Chunk {self.completed_chunks + 1}")
        
        # Show items in current chunk
        if self.last_chunk_items[1] > 0:
            info_parts.append(f"({self.last_chunk_items[0]}/{self.last_chunk_items[1]} items)")
        
        # Calculate ETA
        if total_progress > 0 and self.start_time:
            elapsed_seconds = self.start_time.secsTo(QTime.currentTime())
            if elapsed_seconds > 0:
                total_time_estimate = elapsed_seconds / (total_progress / 100.0)
                remaining_seconds = int(total_time_estimate - elapsed_seconds)
                if remaining_seconds > 0:
                    eta = self._format_time(remaining_seconds)
                    info_parts.append(f"ETA: {eta}")
        
        self.info_label.setText(" | ".join(info_parts))
    
    def _format_time(self, seconds):
        """Format seconds into readable time string."""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}m {secs}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    def _update_elapsed_time(self):
        """Update the elapsed time display."""
        if self.start_time:
            elapsed = self.start_time.secsTo(QTime.currentTime())
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            seconds = elapsed % 60
            self.elapsed_label.setText(f"Elapsed: {hours:02d}:{minutes:02d}:{seconds:02d}")

