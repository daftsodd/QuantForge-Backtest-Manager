"""
Code Viewer with Syntax Highlighting
Displays Python code in read-only mode with line numbers.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import Qt, QRegularExpression
import os
from pathlib import Path


class PythonHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Python code."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Define formatting styles
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        
        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor("#4EC9B0"))
        
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        comment_format.setFontItalic(True)
        
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#DCDCAA"))
        
        # Define highlighting rules
        self.highlighting_rules = []
        
        # Keywords
        keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def',
            'del', 'elif', 'else', 'except', 'False', 'finally', 'for',
            'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
            'None', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return',
            'True', 'try', 'while', 'with', 'yield', 'async', 'await'
        ]
        for keyword in keywords:
            pattern = QRegularExpression(f'\\b{keyword}\\b')
            self.highlighting_rules.append((pattern, keyword_format))
        
        # Built-in functions
        builtins = [
            'abs', 'all', 'any', 'bin', 'bool', 'bytes', 'callable', 'chr',
            'dict', 'dir', 'enumerate', 'filter', 'float', 'format', 'frozenset',
            'int', 'isinstance', 'len', 'list', 'map', 'max', 'min', 'open',
            'print', 'range', 'set', 'slice', 'sorted', 'str', 'sum', 'tuple',
            'type', 'zip'
        ]
        for builtin in builtins:
            pattern = QRegularExpression(f'\\b{builtin}\\b')
            self.highlighting_rules.append((pattern, builtin_format))
        
        # Numbers
        self.highlighting_rules.append((
            QRegularExpression('\\b[0-9]+\\.?[0-9]*\\b'),
            number_format
        ))
        
        # Functions
        self.highlighting_rules.append((
            QRegularExpression('\\b[A-Za-z_][A-Za-z0-9_]*(?=\\()'),
            function_format
        ))
        
        # Strings (double quotes)
        self.highlighting_rules.append((
            QRegularExpression('"[^"\\\\]*(\\\\.[^"\\\\]*)*"'),
            string_format
        ))
        
        # Strings (single quotes)
        self.highlighting_rules.append((
            QRegularExpression("'[^'\\\\]*(\\\\.[^'\\\\]*)*'"),
            string_format
        ))
        
        # Triple-quoted strings
        self.highlighting_rules.append((
            QRegularExpression('"""[^"]*"""'),
            string_format
        ))
        
        # Comments
        self.highlighting_rules.append((
            QRegularExpression('#[^\n]*'),
            comment_format
        ))
    
    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text."""
        for pattern, format_style in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format_style)


class CodeViewer(QWidget):
    """Widget for displaying Python code with syntax highlighting."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header label
        self.header_label = QLabel("No file selected")
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
        
        # Code text edit
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Consolas", 10))
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: none;
                padding: 10px;
            }
        """)
        
        # Apply syntax highlighter
        self.highlighter = PythonHighlighter(self.text_edit.document())
        
        layout.addWidget(self.text_edit)
    
    def load_file(self, file_path):
        """Load and display a Python file."""
        self.current_file = file_path
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.text_edit.setPlainText(content)
            
            # Update header with file info
            file_stat = os.stat(file_path)
            file_size = file_stat.st_size
            line_count = content.count('\n') + 1
            
            size_str = self._format_size(file_size)
            header_text = (
                f"{Path(file_path).name} | "
                f"{size_str} | "
                f"{line_count} lines"
            )
            self.header_label.setText(header_text)
            
        except Exception as e:
            self.text_edit.setPlainText(f"Error loading file: {e}")
            self.header_label.setText("Error loading file")
    
    def clear(self):
        """Clear the code viewer."""
        self.text_edit.clear()
        self.header_label.setText("No file selected")
        self.current_file = None
    
    def _format_size(self, size_bytes):
        """Format file size in human-readable form."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

