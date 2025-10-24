"""
Backtest Builder Window
Interactive strategy builder with live code preview.
"""
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QSplitter,
                              QWidget, QLabel, QSpinBox, QDoubleSpinBox,
                              QLineEdit, QPushButton, QComboBox, QCheckBox,
                              QGroupBox, QScrollArea, QTextEdit, QFileDialog,
                              QMessageBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPen, QIcon
import os


def create_checkmark_icon():
    """Create a checkmark icon for checkboxes."""
    pixmap = QPixmap(16, 16)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    pen = QPen(Qt.GlobalColor.white)
    pen.setWidth(2)
    painter.setPen(pen)
    
    # Draw checkmark
    painter.drawLine(3, 8, 6, 11)
    painter.drawLine(6, 11, 13, 4)
    
    painter.end()
    return QIcon(pixmap)


class BacktestBuilder(QMainWindow):
    """Interactive backtest strategy builder window."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Backtest Builder")
        self.setMinimumSize(1400, 900)
        
        # Default values
        self.config = self._default_config()
        self.exported_file_path = None  # Store last exported file
        
        # Initialize attributes to prevent errors during UI creation
        self.sweep_widgets = {}
        self.indicator_checkboxes = {}
        self.buy_combo = None
        self.sell_combo = None
        
        # Create checkmark icon for checkboxes
        self._setup_checkmark_icon()
        
        self._init_ui()
        self._apply_stylesheet()
        
        # Initialize dynamic elements after UI is created
        self._update_sweep_visibility()
        self._update_trading_logic_options()
        self._update_code_preview()
    
    def _setup_checkmark_icon(self):
        """Create and save checkmark icon for checkbox styling."""
        icon = create_checkmark_icon()
        pixmap = icon.pixmap(QSize(16, 16))
        
        # Save to temp location
        import tempfile
        self.checkmark_path = os.path.join(tempfile.gettempdir(), "qf_checkmark.png")
        pixmap.save(self.checkmark_path, "PNG")
    
    def _default_config(self):
        """Return default configuration values."""
        return {
            # Data Configuration
            'data_path': r'E:\adamp\Documents\Visual Studio Code\Strategy development code\BitcoinData.csv',
            'data_separator': ';',
            'data_engine': 'python',
            'date_column': 'timeOpen',
            'date_format': '%Y-%m-%dT%H:%M:%S.%fZ',
            'price_columns': ['open', 'high', 'low', 'close', 'volume', 'marketCap'],
            
            # Strategy Configuration
            'strategy_name': 'GMA_KAMA_Crossover',
            'selected_indicators': [],  # List of selected indicators
            
            # Hidden parameters (used in code generation)
            'gma_period': 50,
            'kama_period': 50,
            'kama_fast_period': 2,
            'kama_slow_period': 30,
            'sma_period': 50,
            
            # Trading Logic
            'buy_condition': 'GMA crosses KAMA from above',
            'sell_condition': 'GMA crosses KAMA from below',
            'initial_capital': 10000,
            'enable_short_selling': False,  # Toggle for long/short vs long-only
            'tie_rule': 'strict',  # 'strict' or 'hold_prior'
            'start_in_sync': False,
            'fee_rate': 0.0,  # Trading fee as fraction (0.001 = 0.1%)
            'periods_per_year': 365,  # For annualization (365=daily, 252=trading days, etc.)
            
            # Parameter Sweep (always enabled)
            'gma_start': 1,
            'gma_end': 100,
            'gma_step': 1,
            'kama_start': 1,
            'kama_end': 100,
            'kama_step': 1,
            'sma_start': 1,
            'sma_end': 100,
            'sma_step': 1,
            
            # Performance
            'n_cores_percent': 52,
            'chunk_size': 500,
            'pause_interval': 5,
            
            # Output
            'output_filename': 'backtest_results.xlsx',
            'generate_heatmap': True,
            'heatmap_metric': 'Total_Profit_%',
            'heatmap_filename': 'strategy_heatmap.png',
            'colormap': 'viridis',
            
            # Metrics
            'calculate_sharpe': True,
            'calculate_sortino': True,
            'calculate_omega': True,
            'calculate_drawdown': True,
        }
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel: Configuration options
        left_panel = self._create_config_panel()
        splitter.addWidget(left_panel)
        
        # Right panel: Code preview
        right_panel = self._create_code_panel()
        splitter.addWidget(right_panel)
        
        # Set initial sizes (40% config, 60% code)
        splitter.setSizes([560, 840])
        
        main_layout.addWidget(splitter)
    
    def _create_config_panel(self):
        """Create the configuration panel with all options."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QLabel("Strategy Configuration")
        header.setStyleSheet("""
            QLabel {
                background-color: #2D2D30;
                color: #CCCCCC;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
                border-bottom: 1px solid #3E3E42;
            }
        """)
        layout.addWidget(header)
        
        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #252526;
                border: none;
            }
            QWidget {
                background-color: #252526;
            }
        """)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add configuration groups
        content_layout.addWidget(self._create_data_group())
        content_layout.addWidget(self._create_indicators_group())
        content_layout.addWidget(self._create_trading_group())
        content_layout.addWidget(self._create_sweep_group())
        content_layout.addWidget(self._create_performance_group())
        content_layout.addWidget(self._create_output_group())
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Bottom buttons
        button_panel = self._create_button_panel()
        layout.addWidget(button_panel)
        
        return panel
    
    def _create_data_group(self):
        """Create data configuration group."""
        group = self._create_group("Data Configuration")
        layout = group.layout()
        
        # Data path
        path_layout = QHBoxLayout()
        path_label = QLabel("Data Path:")
        self.data_path_input = QLineEdit(self.config['data_path'])
        self.data_path_input.textChanged.connect(self._on_config_changed)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_data_file)
        browse_btn.setMaximumWidth(80)
        path_layout.addWidget(path_label, 1)
        path_layout.addWidget(self.data_path_input, 3)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)
        
        # Separator
        layout.addLayout(self._create_field("Separator:", 
            QLineEdit(self.config['data_separator']), 'data_separator'))
        
        # Date column
        layout.addLayout(self._create_field("Date Column:", 
            QLineEdit(self.config['date_column']), 'date_column'))
        
        # Date format
        layout.addLayout(self._create_field("Date Format:", 
            QLineEdit(self.config['date_format']), 'date_format'))
        
        return group
    
    def _create_indicators_group(self):
        """Create indicators selection group."""
        group = self._create_group("Indicators")
        layout = group.layout()
        
        # Strategy name
        layout.addLayout(self._create_field("Strategy Name:", 
            QLineEdit(self.config['strategy_name']), 'strategy_name'))
        
        # Info label
        info_label = QLabel("Select indicators to use (more coming soon):")
        info_label.setStyleSheet("color: #CCCCCC; font-style: italic; margin-top: 5px; margin-bottom: 10px;")
        layout.addWidget(info_label)
        
        # Create checkboxes for each indicator
        self.indicator_checkboxes = {}
        
        indicators = [
            ("gma", "GMA (Geometric Moving Average)"),
            ("kama", "KAMA (Kaufman Adaptive Moving Average)"),
            ("sma", "SMA (Simple Moving Average)"),
        ]
        
        for indicator_id, indicator_name in indicators:
            checkbox = QCheckBox(indicator_name)
            checkbox.setStyleSheet("color: #CCCCCC; padding: 5px;")
            checkbox.stateChanged.connect(self._on_indicator_selection_changed)
            layout.addWidget(checkbox)
            self.indicator_checkboxes[indicator_id] = checkbox
        
        # Default selections (GMA and KAMA)
        self.indicator_checkboxes['gma'].setChecked(True)
        self.indicator_checkboxes['kama'].setChecked(True)
        
        note_label = QLabel("Note: Select at least one indicator for the strategy")
        note_label.setStyleSheet("color: #CCCCCC; font-size: 10px; font-style: italic; margin-top: 10px;")
        layout.addWidget(note_label)
        
        return group
    
    def _create_trading_group(self):
        """Create trading logic configuration group."""
        group = self._create_group("Trading Logic")
        layout = group.layout()
        
        # Buy condition
        self.buy_combo = QComboBox()
        self.buy_combo.setStyleSheet("""
            QComboBox {
                background-color: #3C3C3C;
                color: #CCCCCC;
                border: 1px solid #3E3E42;
                padding: 5px;
                border-radius: 3px;
            }
            QComboBox:focus {
                border: 1px solid #007ACC;
            }
        """)
        buy_label = QLabel("Buy Condition:")
        buy_label.setStyleSheet("color: #CCCCCC;")
        buy_label.setMinimumWidth(150)
        buy_layout = QHBoxLayout()
        buy_layout.addWidget(buy_label)
        buy_layout.addWidget(self.buy_combo, 1)
        layout.addLayout(buy_layout)
        
        # Sell condition
        self.sell_combo = QComboBox()
        self.sell_combo.setStyleSheet("""
            QComboBox {
                background-color: #3C3C3C;
                color: #CCCCCC;
                border: 1px solid #3E3E42;
                padding: 5px;
                border-radius: 3px;
            }
            QComboBox:focus {
                border: 1px solid #007ACC;
            }
        """)
        sell_label = QLabel("Sell Condition:")
        sell_label.setStyleSheet("color: #CCCCCC;")
        sell_label.setMinimumWidth(150)
        sell_layout = QHBoxLayout()
        sell_layout.addWidget(sell_label)
        sell_layout.addWidget(self.sell_combo, 1)
        layout.addLayout(sell_layout)
        
        # Initial capital
        capital_spin = QDoubleSpinBox()
        capital_spin.setRange(100, 1000000)
        capital_spin.setValue(self.config['initial_capital'])
        capital_spin.setDecimals(2)
        capital_spin.setSuffix(" $")
        layout.addLayout(self._create_field("Initial Capital:", capital_spin, 'initial_capital'))
        
        # Periods per year (for annualization)
        periods_spin = QSpinBox()
        periods_spin.setRange(1, 365)
        periods_spin.setValue(self.config['periods_per_year'])
        layout.addLayout(self._create_field("Periods/Year:", periods_spin, 'periods_per_year'))
        
        # Fee rate
        fee_spin = QDoubleSpinBox()
        fee_spin.setRange(0, 0.1)
        fee_spin.setValue(self.config['fee_rate'])
        fee_spin.setDecimals(4)
        fee_spin.setSuffix(" (fraction)")
        layout.addLayout(self._create_field("Fee Rate:", fee_spin, 'fee_rate'))
        
        # Enable short selling checkbox
        self.short_selling_cb = QCheckBox("Enable Short Selling (Long/Short)")
        self.short_selling_cb.setChecked(self.config['enable_short_selling'])
        self.short_selling_cb.setToolTip(
            "When enabled, strategy holds long when condition favors it and short when it doesn't (no flat exposure).\n"
            "When disabled, strategy is long-only (long or flat)."
        )
        self.short_selling_cb.stateChanged.connect(self._on_config_changed)
        self.short_selling_cb.setStyleSheet("color: #CCCCCC; padding: 5px; margin-top: 10px;")
        layout.addWidget(self.short_selling_cb)
        
        return group
    
    def _create_sweep_group(self):
        """Create parameter sweep configuration group."""
        group = self._create_group("Parameter Sweep")
        self.sweep_layout = group.layout()
        
        # Store references to sweep widgets for each indicator
        self.sweep_widgets = {}
        
        # Create sweep parameters for each indicator
        indicators = [
            ('gma', 'GMA', 'gma_start', 'gma_end', 'gma_step'),
            ('kama', 'KAMA', 'kama_start', 'kama_end', 'kama_step'),
            ('sma', 'SMA', 'sma_start', 'sma_end', 'sma_step'),
        ]
        
        for ind_id, ind_name, start_key, end_key, step_key in indicators:
            # Create container widget for this indicator's sweep params
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 10)
            
            # Start
            start_spin = QSpinBox()
            start_spin.setRange(1, 1000)
            start_spin.setValue(self.config[start_key])
            start_layout = self._create_field(f"{ind_name} Start:", start_spin, start_key)
            container_layout.addLayout(start_layout)
            
            # End
            end_spin = QSpinBox()
            end_spin.setRange(1, 1000)
            end_spin.setValue(self.config[end_key])
            end_layout = self._create_field(f"{ind_name} End:", end_spin, end_key)
            container_layout.addLayout(end_layout)
            
            # Step
            step_spin = QSpinBox()
            step_spin.setRange(1, 100)
            step_spin.setValue(self.config[step_key])
            step_layout = self._create_field(f"{ind_name} Step:", step_spin, step_key)
            container_layout.addLayout(step_layout)
            
            self.sweep_layout.addWidget(container)
            self.sweep_widgets[ind_id] = container
        
        return group
    
    def _create_performance_group(self):
        """Create performance configuration group."""
        group = self._create_group("Performance Settings")
        layout = group.layout()
        
        # CPU cores percentage
        cores_spin = QSpinBox()
        cores_spin.setRange(1, 100)
        cores_spin.setValue(self.config['n_cores_percent'])
        cores_spin.setSuffix(" %")
        layout.addLayout(self._create_field("CPU Usage:", cores_spin, 'n_cores_percent'))
        
        # Chunk size
        chunk_spin = QSpinBox()
        chunk_spin.setRange(10, 10000)
        chunk_spin.setValue(self.config['chunk_size'])
        layout.addLayout(self._create_field("Chunk Size:", chunk_spin, 'chunk_size'))
        
        # Pause interval
        pause_spin = QSpinBox()
        pause_spin.setRange(0, 60)
        pause_spin.setValue(self.config['pause_interval'])
        pause_spin.setSuffix(" min")
        layout.addLayout(self._create_field("Pause Interval:", pause_spin, 'pause_interval'))
        
        return group
    
    def _create_output_group(self):
        """Create output configuration group."""
        group = self._create_group("Output Settings")
        layout = group.layout()
        
        # Output filename
        layout.addLayout(self._create_field("Excel Filename:", 
            QLineEdit(self.config['output_filename']), 'output_filename'))
        
        # Generate heatmap
        self.heatmap_checkbox = QCheckBox("Generate Heatmap")
        self.heatmap_checkbox.setChecked(self.config['generate_heatmap'])
        self.heatmap_checkbox.stateChanged.connect(self._on_config_changed)
        layout.addWidget(self.heatmap_checkbox)
        
        # Heatmap metric
        metric_combo = QComboBox()
        metric_combo.addItems([
            'Total_Profit_%',
            'Sharpe_Ratio',
            'Sortino_Ratio',
            'Max_Drawdown_%',
            'Omega_Ratio'
        ])
        metric_combo.setCurrentText(self.config['heatmap_metric'])
        layout.addLayout(self._create_field("Heatmap Metric:", metric_combo, 'heatmap_metric'))
        
        # Heatmap filename
        layout.addLayout(self._create_field("Heatmap Filename:", 
            QLineEdit(self.config['heatmap_filename']), 'heatmap_filename'))
        
        # Colormap
        colormap_combo = QComboBox()
        colormap_combo.addItems(['viridis', 'plasma', 'inferno', 'magma', 'cividis', 
                                  'hot', 'cool', 'RdYlGn', 'seismic'])
        colormap_combo.setCurrentText(self.config['colormap'])
        layout.addLayout(self._create_field("Colormap:", colormap_combo, 'colormap'))
        
        # Metrics to calculate
        metrics_label = QLabel("Calculate Metrics:")
        metrics_label.setStyleSheet("color: #CCCCCC; margin-top: 10px;")
        layout.addWidget(metrics_label)
        
        self.sharpe_cb = QCheckBox("Sharpe Ratio")
        self.sharpe_cb.setChecked(self.config['calculate_sharpe'])
        self.sharpe_cb.stateChanged.connect(self._on_config_changed)
        layout.addWidget(self.sharpe_cb)
        
        self.sortino_cb = QCheckBox("Sortino Ratio")
        self.sortino_cb.setChecked(self.config['calculate_sortino'])
        self.sortino_cb.stateChanged.connect(self._on_config_changed)
        layout.addWidget(self.sortino_cb)
        
        self.omega_cb = QCheckBox("Omega Ratio")
        self.omega_cb.setChecked(self.config['calculate_omega'])
        self.omega_cb.stateChanged.connect(self._on_config_changed)
        layout.addWidget(self.omega_cb)
        
        self.drawdown_cb = QCheckBox("Max Drawdown")
        self.drawdown_cb.setChecked(self.config['calculate_drawdown'])
        self.drawdown_cb.stateChanged.connect(self._on_config_changed)
        layout.addWidget(self.drawdown_cb)
        
        return group
    
    def _create_code_panel(self):
        """Create the code preview panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QLabel("Code Preview (Live)")
        header.setStyleSheet("""
            QLabel {
                background-color: #2D2D30;
                color: #CCCCCC;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
                border-bottom: 1px solid #3E3E42;
            }
        """)
        layout.addWidget(header)
        
        # Code editor
        self.code_preview = QTextEdit()
        self.code_preview.setReadOnly(True)
        self.code_preview.setFont(QFont("Consolas", 10))
        self.code_preview.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: none;
                padding: 15px;
            }
        """)
        layout.addWidget(self.code_preview)
        
        return panel
    
    def _create_button_panel(self):
        """Create the bottom button panel."""
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: #2D2D30;
                border-top: 1px solid #3E3E42;
            }
        """)
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Reset button
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self._reset_to_defaults)
        layout.addWidget(reset_btn)
        
        layout.addStretch()
        
        # Export button
        export_btn = QPushButton("Export Code...")
        export_btn.clicked.connect(self._export_code)
        layout.addWidget(export_btn)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        return panel
    
    def _create_group(self, title):
        """Create a styled group box."""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                color: #CCCCCC;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #4EC9B0;
            }
        """)
        layout = QVBoxLayout()
        layout.setSpacing(8)
        group.setLayout(layout)
        return group
    
    def _create_field(self, label_text, widget, config_key):
        """Create a labeled field and connect it to config."""
        layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setStyleSheet("color: #CCCCCC;")
        label.setMinimumWidth(150)
        
        widget.setStyleSheet("""
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #3C3C3C;
                color: #CCCCCC;
                border: 1px solid #3E3E42;
                padding: 5px;
                border-radius: 3px;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border: 1px solid #007ACC;
            }
            QSpinBox::up-button, QDoubleSpinBox::up-button {
                background-color: #3C3C3C;
                border: none;
            }
            QSpinBox::down-button, QDoubleSpinBox::down-button {
                background-color: #3C3C3C;
                border: none;
            }
        """)
        
        # Connect signals based on widget type
        if isinstance(widget, QLineEdit):
            widget.textChanged.connect(lambda: self._update_config(config_key, widget.text()))
        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            widget.valueChanged.connect(lambda: self._update_config(config_key, widget.value()))
        elif isinstance(widget, QComboBox):
            widget.currentTextChanged.connect(lambda: self._update_config(config_key, widget.currentText()))
        
        layout.addWidget(label)
        layout.addWidget(widget, 1)
        
        return layout
    
    def _apply_stylesheet(self):
        """Apply the window stylesheet."""
        # Convert path to use forward slashes for stylesheet
        checkmark_path = self.checkmark_path.replace('\\', '/')
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #1E1E1E;
            }}
            QWidget {{
                background-color: #1E1E1E;
            }}
            QPushButton {{
                background-color: #0E639C;
                color: #FFFFFF;
                border: none;
                padding: 8px 16px;
                border-radius: 3px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #1177BB;
            }}
            QPushButton:pressed {{
                background-color: #0D5A8E;
            }}
            QCheckBox {{
                color: #CCCCCC;
                spacing: 5px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 1px solid #3E3E42;
                border-radius: 3px;
                background-color: #3C3C3C;
            }}
            QCheckBox::indicator:checked {{
                background-color: #007ACC;
                border: 1px solid #007ACC;
                image: url({checkmark_path});
            }}
            QScrollBar:vertical {{
                background-color: #1E1E1E;
                width: 12px;
            }}
            QScrollBar::handle:vertical {{
                background-color: #424242;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: #4E4E4E;
            }}
        """)
    
    def _update_config(self, key, value):
        """Update configuration and refresh code preview."""
        self.config[key] = value
        self._update_code_preview()
    
    def _on_config_changed(self):
        """Handle any configuration change."""
        # Update special widgets
        self.config['data_path'] = self.data_path_input.text()
        self.config['generate_heatmap'] = self.heatmap_checkbox.isChecked()
        self.config['enable_short_selling'] = self.short_selling_cb.isChecked()
        # Note: sweep is always enabled, no checkbox needed
        self.config['calculate_sharpe'] = self.sharpe_cb.isChecked()
        self.config['calculate_sortino'] = self.sortino_cb.isChecked()
        self.config['calculate_omega'] = self.omega_cb.isChecked()
        self.config['calculate_drawdown'] = self.drawdown_cb.isChecked()
        
        self._update_code_preview()
    
    def _on_indicator_selection_changed(self):
        """Handle indicator selection changes."""
        # Update sweep visibility
        self._update_sweep_visibility()
        
        # Update trading logic options
        self._update_trading_logic_options()
        
        # Update code preview
        self._update_code_preview()
    
    def _update_sweep_visibility(self):
        """Show/hide sweep parameters based on selected indicators."""
        for ind_id, checkbox in self.indicator_checkboxes.items():
            if ind_id in self.sweep_widgets:
                self.sweep_widgets[ind_id].setVisible(checkbox.isChecked())
    
    def _update_trading_logic_options(self):
        """Update buy/sell condition dropdowns based on selected indicators."""
        # Safety check - ensure combo boxes exist
        if self.buy_combo is None or self.sell_combo is None:
            return
        
        selected_indicators = self._get_selected_indicators()
        
        if len(selected_indicators) == 0:
            self.buy_combo.clear()
            self.sell_combo.clear()
            return
        
        # Generate all possible crossover combinations
        conditions = []
        
        if len(selected_indicators) >= 2:
            # Generate crossover conditions for all pairs
            for i in range(len(selected_indicators)):
                for j in range(len(selected_indicators)):
                    if i != j:
                        ind1 = selected_indicators[i].upper()
                        ind2 = selected_indicators[j].upper()
                        conditions.append(f"{ind1} crosses {ind2} from above")
                        conditions.append(f"{ind1} crosses {ind2} from below")
                        conditions.append(f"{ind1} > {ind2}")
                        conditions.append(f"{ind1} < {ind2}")
        elif len(selected_indicators) == 1:
            # For single indicator, use price comparisons
            ind = selected_indicators[0].upper()
            conditions = [
                f"Price crosses {ind} from above",
                f"Price crosses {ind} from below",
                f"Price > {ind}",
                f"Price < {ind}"
            ]
        
        # Update combo boxes
        current_buy = self.buy_combo.currentText()
        current_sell = self.sell_combo.currentText()
        
        self.buy_combo.clear()
        self.sell_combo.clear()
        
        self.buy_combo.addItems(conditions)
        self.sell_combo.addItems(conditions)
        
        # Try to restore previous selections if still valid
        if current_buy in conditions:
            self.buy_combo.setCurrentText(current_buy)
        if current_sell in conditions:
            self.sell_combo.setCurrentText(current_sell)
    
    def _get_selected_indicators(self):
        """Get list of selected indicator IDs."""
        return [ind_id for ind_id, checkbox in self.indicator_checkboxes.items() 
                if checkbox.isChecked()]
    
    def _generate_indicator_functions(self, selected):
        """Generate indicator function code for selected indicators."""
        functions = []
        
        if 'gma' in selected:
            functions.append("""def compute_gma(series: pd.Series, window: int) -> pd.Series:
    N = int(window)
    if N < 1:
        return series.copy()
    return np.exp(
        np.log(series)
          .rolling(window=N, min_periods=N)
          .mean()
    )""")
        
        if 'kama' in selected:
            functions.append(f"""def compute_kama(series: pd.Series, window: int,
                 fast_period: int = {self.config['kama_fast_period']},
                 slow_period: int = {self.config['kama_slow_period']}) -> pd.Series:
    N = int(window)
    if N < 1:
        return series.copy()

    change     = series.diff(N).abs()
    volatility = series.diff().abs().rolling(window=N, min_periods=N).sum()
    er         = (change / volatility.replace(0, np.nan)).fillna(0)
    fast_sc    = 2 / (fast_period + 1)
    slow_sc    = 2 / (slow_period + 1)
    sc         = (er * (fast_sc - slow_sc) + slow_sc) ** 2

    kama = series.copy().astype(float)
    kama.iloc[:N] = series.iloc[:N]
    for t in range(N, len(series)):
        kama.iloc[t] = kama.iloc[t-1] + sc.iloc[t] * (series.iloc[t] - kama.iloc[t-1])
    return kama""")
        
        if 'sma' in selected:
            functions.append("""def compute_sma(series: pd.Series, window: int) -> pd.Series:
    \"\"\"Simple Moving Average\"\"\"
    N = int(window)
    if N < 1:
        return series.copy()
    return series.rolling(window=N, min_periods=N).mean()""")
        
        return '\n\n'.join(functions)
    
    def _generate_compute_indicators(self, selected):
        """Generate compute_indicators function for selected indicators."""
        params = [f"{ind}_period" for ind in selected]
        params_str = ', '.join(params)
        
        calculations = []
        for ind in selected:
            ind_upper = ind.upper()
            calculations.append(f"    df2['{ind_upper}']  = compute_{ind}(df2['close'], window={ind}_period)")
        
        calculations_str = '\n'.join(calculations)
        
        # Also generate previous value columns for selected indicators
        prev_cols = []
        for ind in selected:
            ind_upper = ind.upper()
            prev_cols.append(f"    d['prev_{ind_upper}']  = d['{ind_upper}'].shift(1)")
        prev_cols_str = '\n'.join(prev_cols)
        
        return f"""def compute_indicators(df, {params_str}):
    df2 = df.copy()
{calculations_str}
    return df2"""
    
    def _generate_prev_columns(self, selected):
        """Generate previous value columns for selected indicators."""
        prev_cols = []
        for ind in selected:
            ind_upper = ind.upper()
            prev_cols.append(f"    d['prev_{ind_upper}']  = d['{ind_upper}'].shift(1)")
        return '\n'.join(prev_cols)
    
    def _generate_parameter_sweep(self, selected):
        """Generate parameter_sweep function for selected indicators."""
        c = self.config
        
        # Generate parameter names and combo generation
        range_params = ', '.join([f"{ind}_range" for ind in selected])
        combo_vars = ', '.join(selected)
        combo_list = ' for '.join([f"{ind} in {ind}_range" for ind in selected])
        
        # Generate task function parameters and indicator computation
        task_params = ', '.join(selected)
        indicator_call = ', '.join(selected)
        
        # Generate period updates for results
        period_updates = []
        for ind in selected:
            ind_upper = ind.upper()
            period_updates.append(f"'{ind_upper}_Period': {ind}")
        period_updates_str = ', '.join(period_updates)
        
        return f"""def parameter_sweep(df, {range_params},
                    initial_capital={c['initial_capital']}, chunk_size={c['chunk_size']}):
    combos = [({combo_vars}) for {combo_list}]
    results, start = [], time.time()

    for i in range(0, len(combos), chunk_size):
        chunk = combos[i:i+chunk_size]
        def task({task_params}):
            ind   = compute_indicators(df, {indicator_call})
            strat = strategy_logic(ind)
            stats = run_backtest(strat, initial_capital)
            stats.update({{{period_updates_str}}})
            return stats

        with tqdm_joblib(tqdm(total=len(chunk), desc="Processing")):
            out = Parallel(n_jobs=n_jobs)(
                delayed(task)({task_params}) for {task_params} in chunk
            )
        results.extend(out)

        if time.time() - start >= {c['pause_interval']}*60:
            print(f"Pausing for {c['pause_interval']} minutes...")
            time.sleep({c['pause_interval']}*60)
            start = time.time()

    return pd.DataFrame(results)"""
    
    def _browse_data_file(self):
        """Browse for data file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Data File",
            "",
            "CSV Files (*.csv);;All Files (*.*)"
        )
        if file_path:
            self.data_path_input.setText(file_path)
            self._on_config_changed()
    
    def _reset_to_defaults(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset to Defaults",
            "Are you sure you want to reset all settings to default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config = self._default_config()
            self.close()
            # Reopen with defaults
            new_builder = BacktestBuilder(self.parent())
            new_builder.show()
    
    def _get_generated_strategies_folder(self):
        """Get or create the Generated_Strategies folder."""
        # Get the directory where the app is running
        app_dir = os.path.dirname(os.path.abspath(__file__))
        strategies_folder = os.path.join(app_dir, "Generated_Strategies")
        
        # Create folder if it doesn't exist
        if not os.path.exists(strategies_folder):
            os.makedirs(strategies_folder)
            
            # Create a README file to explain the folder
            readme_path = os.path.join(strategies_folder, "README.txt")
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write("Generated Strategies Folder\n")
                f.write("=" * 50 + "\n\n")
                f.write("This folder contains all strategy backtest scripts\n")
                f.write("generated by the QuantForge Backtest Builder.\n\n")
                f.write("Files are automatically saved here with timestamps\n")
                f.write("to prevent overwriting previous strategies.\n\n")
                f.write("You can:\n")
                f.write("- Run these scripts directly\n")
                f.write("- Import them into the main app\n")
                f.write("- Modify them as needed\n")
                f.write("- Copy them to other locations\n\n")
                f.write("Each file is a complete, standalone backtest script.\n")
        
        return strategies_folder
    
    def _export_code(self):
        """Export the generated code to a file automatically."""
        try:
            # Get the strategies folder
            strategies_folder = self._get_generated_strategies_folder()
            
            # Generate filename with timestamp to avoid overwriting
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            strategy_name = self.config['strategy_name'].replace(' ', '_')
            filename = f"{strategy_name}_{timestamp}.py"
            file_path = os.path.join(strategies_folder, filename)
            
            # Write the code with explicit UTF-8 encoding
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self._generate_code())
            
            self.exported_file_path = file_path
            
            # Ask if user wants to add to file browser
            reply = QMessageBox.question(
                self,
                "Export Successful",
                f"Code exported successfully to:\n{file_path}\n\n"
                "Would you like to add this file to your strategy browser?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes and self.parent():
                # Add to parent's file browser if available
                if hasattr(self.parent(), 'file_browser'):
                    self.parent().file_browser.add_file(file_path)
                    self.parent().status_bar.showMessage(f"Added {filename} to browser")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export code:\n{str(e)}"
            )
    
    def _update_code_preview(self):
        """Update the code preview with generated code."""
        # Safety check - ensure code_preview exists
        if not hasattr(self, 'code_preview'):
            return
        code = self._generate_code()
        self.code_preview.setPlainText(code)
    
    def _generate_code(self):
        """Generate Python code based on current configuration."""
        c = self.config
        selected = self._get_selected_indicators()
        
        if not selected:
            return "# Please select at least one indicator"
        
        # Get buy/sell logic from comboboxes
        buy_condition = self.buy_combo.currentText() if self.buy_combo else ""
        sell_condition = self.sell_combo.currentText() if self.sell_combo else ""
        
        # Optimized path for GMA + KAMA only
        if set(selected) == {'gma', 'kama'}:
            return self._generate_code_optimized_gma_kama(buy_condition, sell_condition)

        # Calculate buy/sell logic
        buy_logic = self._get_signal_logic(buy_condition, 'buy')
        sell_logic = self._get_signal_logic(sell_condition, 'sell')
        
        # Use centralized metrics calculation (no more hard-coded annualization)
        metrics_import = "from backtest_core import compute_metrics_from_portfolio"
        
        # Build parameter sweep ranges for selected indicators
        range_definitions = []
        range_params = []
        period_updates = []
        
        for ind in selected:
            ind_upper = ind.upper()
            range_definitions.append(f"    {ind}_range  = range({c[f'{ind}_start']}, {c[f'{ind}_end']} + 1, {c[f'{ind}_step']})")
            range_params.append(f"{ind}_range")
            period_updates.append(f"'{ind_upper}_Period': {ind}")
        
        ranges_code = '\n'.join(range_definitions)
        ranges_str = ', '.join(range_params)
        periods_str = ', '.join(period_updates)
        
        main_exec = f"""{ranges_code}

    results_df = parameter_sweep(df_data, {ranges_str},
                                 initial_capital={c['initial_capital']},
                                 chunk_size={c['chunk_size']})

    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_df.to_excel(
        os.path.join(script_dir, "{c['output_filename']}"),
        index=False
    )"""
        
        # Generate heatmap if requested and we have 2 indicators
        if c['generate_heatmap'] and len(selected) >= 2:
            # Use first two selected indicators for heatmap axes
            ind1 = selected[0].upper()
            ind2 = selected[1].upper()
            main_exec += f"""

    # Heatmap of {c['heatmap_metric']}
    # Generate unique heatmap filename based on script name
    script_basename = os.path.splitext(os.path.basename(__file__))[0]
    heatmap_filename = f"{{script_basename}}_heatmap.png"
    
    pivot = results_df.pivot(
        index='{ind1}_Period',
        columns='{ind2}_Period',
        values='{c['heatmap_metric']}'
    )
    plt.figure(figsize=(10,8))
    plt.imshow(pivot, cmap='{c['colormap']}', origin='lower', aspect='auto')
    plt.colorbar(label='{c['heatmap_metric']}')
    plt.title('Strategy Performance Heatmap: {c['strategy_name']}')
    plt.xlabel('{ind2}_Period')
    plt.ylabel('{ind1}_Period')
    plt.tight_layout()
    plt.savefig(os.path.join(script_dir, heatmap_filename))
    plt.close()
    print(f"Heatmap saved: {{heatmap_filename}}")"""
        
        code = f'''"""
{c['strategy_name']} Strategy Backtest
Generated by QuantForge Backtest Builder

Strategy Summary:
  Buy:  {buy_condition}
  Sell: {sell_condition}
  Periods/year: {c['periods_per_year']}
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os, time, sys
from tqdm import tqdm
from joblib import Parallel, delayed
from tqdm_joblib import tqdm_joblib

# Import shared backtest core for metrics
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(os.path.join(APP_DIR, 'backtest_core.py')):
    sys.path.insert(0, APP_DIR)
    from backtest_core import compute_metrics_from_portfolio
else:
    # Fallback: define metrics locally if backtest_core not found
    def compute_metrics_from_portfolio(port, initial_capital, periods_per_year=365):
        ret = np.diff(port) / port[:-1]
        ret = np.concatenate(([0.0], ret))
        total_prof = (port[-1] / initial_capital - 1.0) * 100.0
        std = np.std(ret, ddof=1)
        sharpe = (np.mean(ret) / std * np.sqrt(float(periods_per_year))) if std != 0.0 else 0.0
        neg = ret[ret < 0.0]
        neg_std = np.std(neg, ddof=1) if neg.size > 0 else 0.0
        sortino = (np.mean(ret) * periods_per_year) / (neg_std * np.sqrt(float(periods_per_year))) if neg.size > 0 and neg_std != 0.0 else 0.0
        pos_sum = ret[ret > 0.0].sum()
        neg_sum = ret[ret < 0.0].sum()
        omega = pos_sum / abs(neg_sum) if neg_sum != 0.0 else float("inf")
        cummax = np.maximum.accumulate(port)
        dd = (port - cummax) / cummax
        drawdown = abs(dd.min() * 100.0)
        return {{
            'Sharpe_Ratio': sharpe,
            'Sortino_Ratio': sortino,
            'Omega_Ratio': omega,
            'Max_Drawdown_%': drawdown,
            'Total_Profit_%': total_prof,
            'Final_Portfolio_Value': port[-1],
        }}

# -----------------------------
# Configuration
# -----------------------------
n_cores = os.cpu_count() or 1
n_jobs  = max(1, int(n_cores * {c['n_cores_percent'] / 100}))

# -----------------------------
# 1. Load & Clean Data
# -----------------------------
def load_and_clean_data():
    path = r"{c['data_path']}"
    df   = pd.read_csv(path, sep="{c['data_separator']}", engine="{c['data_engine']}", quoting=3)
    df   = df.applymap(lambda x: x.strip('"') if isinstance(x, str) else x)
    df['Date'] = pd.to_datetime(
        df['{c['date_column']}'],
        format="{c['date_format']}",
        errors='coerce'
    )
    for col in {c['price_columns']}:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return (
        df.drop_duplicates()
          .dropna(subset=['Date'])
          .sort_values('Date')
          .reset_index(drop=True)
    )

# -----------------------------
# 2. Indicator Functions
# -----------------------------
{self._generate_indicator_functions(selected)}

# -----------------------------
# 3. Combine Indicators
# -----------------------------
{self._generate_compute_indicators(selected)}

# -----------------------------
# 4. Trading Logic
# -----------------------------
def strategy_logic(df):
    """Trading signals for {c['strategy_name']}"""
    d = df.copy()
{self._generate_prev_columns(selected)}
{buy_logic}
{sell_logic}
    return d

# -----------------------------
# 5. Backtest Engine
# -----------------------------
def run_backtest(df, initial_capital={c['initial_capital']}):
    pos, cash, shares = 0, initial_capital, 0
    portfolio, trades = [], 0

    for _, r in df.iterrows():
        price = r['close']
        if pos == 0 and r.get('buy_signal', False):
            shares, cash, pos, trades = cash/price, 0, 1, trades+1
        elif pos == 1 and r.get('sell_signal', False):
            cash, shares, pos = shares*price, 0, 0
        portfolio.append(shares*price if pos else cash)

    port_array = np.array(portfolio, dtype=float)
    metrics = compute_metrics_from_portfolio(port_array, float(initial_capital), periods_per_year={c['periods_per_year']})
    metrics['Number_of_Trades'] = trades
    return metrics

# -----------------------------
# 6. Parameter Sweep
# -----------------------------
{self._generate_parameter_sweep(selected)}

# -----------------------------
# 7. Main Execution
# -----------------------------
if __name__ == "__main__":
    df_data = load_and_clean_data()
{main_exec}
'''
        return code
    
    def _get_signal_logic(self, condition, signal_type):
        """Generate buy/sell signal logic code dynamically based on condition."""
        if not condition:
            return f"""    d['{signal_type}_signal'] = False"""
        
        # Parse the condition to extract indicators
        parts = condition.split()
        
        if len(parts) < 3:
            return f"""    d['{signal_type}_signal'] = False  # Invalid condition"""
        
        ind1 = parts[0]  # First indicator or "Price"
        ind2 = None
        
        # Find the second indicator (different from ind1)
        for part in parts:
            u = part.upper()
            if u in ['GMA', 'KAMA', 'SMA'] and u != ind1.upper():
                ind2 = u
                break
        
        # Handle single indicator comparisons with Price
        if ind1 == "Price":
            ind1 = "close"
            if ind2:
                ind2 = ind2.upper()
        else:
            ind1 = ind1.upper()
            if ind2:
                ind2 = ind2.upper()
        
        # Generate logic based on condition type
        if 'crosses' in condition and 'from above' in condition:
            if ind1 == "close":
                return f"""    d['{signal_type}_signal'] = (
        (d['prev_{ind2}'] < d['{ind2}']) &
        (d['{ind1}'] > d['{ind2}'])
    )"""
            else:
                return f"""    d['{signal_type}_signal'] = (
        (d['prev_{ind1}'] > d['prev_{ind2}']) &
        (d['{ind1}'] < d['{ind2}'])
    )"""
        elif 'crosses' in condition and 'from below' in condition:
            if ind1 == "close":
                return f"""    d['{signal_type}_signal'] = (
        (d['prev_{ind2}'] > d['{ind2}']) &
        (d['{ind1}'] < d['{ind2}'])
    )"""
            else:
                return f"""    d['{signal_type}_signal'] = (
        (d['prev_{ind1}'] < d['prev_{ind2}']) &
        (d['{ind1}'] > d['{ind2}'])
    )"""
        elif ' > ' in condition:
            return f"""    d['{signal_type}_signal'] = (d['{ind1}'] > d['{ind2}'])"""
        elif ' < ' in condition:
            return f"""    d['{signal_type}_signal'] = (d['{ind1}'] < d['{ind2}'])"""
        else:
            return f"""    d['{signal_type}_signal'] = False  # Unrecognized condition"""

    def _generate_code_optimized_gma_kama(self, buy_condition: str, sell_condition: str) -> str:
        """Generate an optimized strategy script specifically for GMA+KAMA.

        - Precomputes GMA and KAMA grids once
        - Properly parses indicator order (left vs right)
        - Uses edge-driven backtest with correct crossover semantics
        - Parallelizes across one dimension
        - Writes multi-sheet Excel with Top-5 by key metrics
        """
        c = self.config
        # Ranges
        gma_range = f"range({c['gma_start']}, {c['gma_end']} + 1, {c['gma_step']})"
        kama_range = f"range({c['kama_start']}, {c['kama_end']} + 1, {c['kama_step']})"

        # Parse indicator order from conditions
        # Format: "{LEFT} crosses {RIGHT} from {above|below}"
        def parse_crossover_condition(cond: str):
            """Parse condition to extract left indicator, right indicator, and direction.
            
            Returns: (left_ind_var, right_ind_var, cross_up: bool) or None if not a crossover
            """
            if not cond or 'crosses' not in cond:
                return None
            
            parts = cond.split()
            if len(parts) < 4:
                return None
            
            left = parts[0].upper()  # e.g., "GMA"
            # Find "crosses" position
            try:
                cross_idx = [p.lower() for p in parts].index('crosses')
                if cross_idx + 1 < len(parts):
                    right = parts[cross_idx + 1].upper()  # e.g., "KAMA"
                else:
                    right = None
            except:
                right = None
            
            if left is None or right is None:
                return None
            
            # Map indicator names to variable names
            ind_map = {'GMA': 'g', 'KAMA': 'k'}
            left_var = ind_map.get(left, 'g')
            right_var = ind_map.get(right, 'k')
            
            # Determine direction
            cross_up = 'from below' in cond.lower()
            
            return (left_var, right_var, cross_up)
        
        # Parse buy and sell conditions
        buy_parsed = parse_crossover_condition(buy_condition)
        sell_parsed = parse_crossover_condition(sell_condition)
        
        # Detect strategy logic type (crossover vs regime)
        is_crossover = buy_parsed is not None or sell_parsed is not None
        strategy_logic = "crossover" if is_crossover else "regime"
        exposure_mode = "long_short" if c['enable_short_selling'] else "long_only"
        
        # Build strategy summary for diagnostics
        buy_desc = buy_condition if buy_condition else "None"
        sell_desc = sell_condition if sell_condition else "None"
        strategy_summary = f"""
# Strategy Summary:
#   Type: {strategy_logic.capitalize()}
#   Exposure: {exposure_mode.replace('_', '-').capitalize()}
#   Buy:  {buy_desc}
#   Sell: {sell_desc}
#   Tie rule: {c['tie_rule']}
#   Start in sync: {c['start_in_sync']}
#   Fee rate: {c['fee_rate']}
#   Periods/year: {c['periods_per_year']}
"""
        
        # Route to appropriate code generation based on strategy_logic and exposure_mode
        if strategy_logic == "crossover":
            if exposure_mode == "long_only":
                # Crossover long-only (existing logic)
                if buy_parsed:
                    left_var, right_var, cross_up = buy_parsed
                    buy_expr = f"compute_crossover_edges({left_var}, {right_var}, cross_up={cross_up}, tie_rule='{c['tie_rule']}')"
                else:
                    buy_expr = f"np.zeros(len(g), dtype=np.bool_)"
                
                if sell_parsed:
                    left_var, right_var, cross_up = sell_parsed
                    sell_expr = f"compute_crossover_edges({left_var}, {right_var}, cross_up={cross_up}, tie_rule='{c['tie_rule']}')"
                else:
                    sell_expr = f"np.zeros(len(g), dtype=np.bool_)"
                
                engine_name = "run_backtest_edges_nb"
                engine_type = "edge_long_only"
            else:
                # Crossover long/short
                if buy_parsed:
                    left_var, right_var, cross_up = buy_parsed
                    long_edge_expr = f"compute_crossover_edges({left_var}, {right_var}, cross_up={cross_up}, tie_rule='{c['tie_rule']}')"
                else:
                    long_edge_expr = f"np.zeros(len(g), dtype=np.bool_)"
                
                if sell_parsed:
                    left_var, right_var, cross_up = sell_parsed
                    short_edge_expr = f"compute_crossover_edges({left_var}, {right_var}, cross_up={cross_up}, tie_rule='{c['tie_rule']}')"
                else:
                    short_edge_expr = f"np.zeros(len(g), dtype=np.bool_)"
                
                buy_expr = long_edge_expr
                sell_expr = short_edge_expr
                engine_name = "run_backtest_edges_long_short_nb"
                engine_type = "edge_long_short"
        else:
            # Regime strategy
            # For regime, we need to compute regime array and route to appropriate engine
            # Simplified: use first condition to infer regime (e.g., "GMA > KAMA")
            engine_name = "run_backtest_regime_long_short_nb" if exposure_mode == "long_short" else "run_backtest_regime_long_only_nb"
            engine_type = f"regime_{exposure_mode.split('_')[1]}"
            buy_expr = f"np.zeros(len(g), dtype=np.bool_)"
            sell_expr = f"np.zeros(len(g), dtype=np.bool_)"

        # Heatmap code if requested
        heatmap_block = ""
        if c['generate_heatmap']:
            heatmap_block = f"""
    # Heatmap of {c['heatmap_metric']}
    # Generate unique heatmap filename based on script name
    script_basename = os.path.splitext(os.path.basename(__file__))[0]
    heatmap_filename = f"{{script_basename}}_heatmap.png"
    
    pivot = all_df.pivot(index='GMA_Period', columns='KAMA_Period', values='{c['heatmap_metric']}')
    plt.figure(figsize=(10,8))
    plt.imshow(pivot, cmap='{c['colormap']}', origin='lower', aspect='auto')
    plt.colorbar(label='{c['heatmap_metric']}')
    plt.title('Strategy Performance Heatmap: {c['strategy_name']}')
    plt.xlabel('KAMA_Period')
    plt.ylabel('GMA_Period')
    plt.tight_layout()
    plt.savefig(os.path.join(script_dir, heatmap_filename))
    plt.close()
    print(f"Heatmap saved: {{heatmap_filename}}")
"""

        code = f'''"""
{c['strategy_name']} Strategy Backtest (Optimized GMA+KAMA)
Generated by QuantForge Backtest Builder
"""
import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from joblib import Parallel, delayed

# Allow importing shared cores from parent directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(SCRIPT_DIR)
if APP_DIR not in sys.path:
    sys.path.append(APP_DIR)

from indicators_core import precompute_gma_grid, precompute_kama_grid
from backtest_core import (
    run_backtest_edges_nb,
    run_backtest_edges_long_short_nb,
    run_backtest_regime_long_only_nb,
    run_backtest_regime_long_short_nb,
    compute_metrics_from_portfolio,
    create_valid_mask,
    compute_crossover_edges,
    compute_regime,
){strategy_summary}

# -----------------------------
# Configuration
# -----------------------------
n_cores = os.cpu_count() or 1
n_jobs  = max(1, int(n_cores * {c['n_cores_percent'] / 100}))

# -----------------------------
# 1. Load & Clean Data
# -----------------------------
def load_and_clean_data():
    path = r"{c['data_path']}"
    df   = pd.read_csv(path, sep="{c['data_separator']}", engine="{c['data_engine']}", quoting=3)
    df   = df.applymap(lambda x: x.strip('"') if isinstance(x, str) else x)
    df['Date'] = pd.to_datetime(
        df['{c['date_column']}'],
        format="{c['date_format']}",
        errors='coerce'
    )
    for col in {c['price_columns']}:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return (
        df.drop_duplicates()
          .dropna(subset=['Date'])
          .sort_values('Date')
          .reset_index(drop=True)
    )

# -----------------------------
# 2. Optimized Sweep
# -----------------------------
def parameter_sweep_optimized(df, initial_capital={c['initial_capital']}):
    close = df['close'].to_numpy(dtype=float)
    g_periods = list({gma_range})
    k_periods = list({kama_range})

    # Precompute indicator grids once
    g_grid = precompute_gma_grid(close, np.array(g_periods, dtype=np.int64))
    k_grid = precompute_kama_grid(close, np.array(k_periods, dtype=np.int64), fast_period={c['kama_fast_period']}, slow_period={c['kama_slow_period']})

    def eval_for_k(kp: int):
        out = []
        k = k_grid[int(kp)]
        for gp in g_periods:
            g = g_grid[int(gp)]
            
            # Create validity mask (both indicators non-NaN)
            valid_mask = create_valid_mask(g, k)
            
            # Route to appropriate engine based on strategy_logic and exposure_mode
            if "{engine_type}" == "edge_long_only":
                # Crossover long-only
                buy_edges = {buy_expr}
                sell_edges = {sell_expr}
                port, final_val, trades, buy_count, sell_count = {engine_name}(
                    close, buy_edges, sell_edges, float(initial_capital),
                    start_in_sync={c['start_in_sync']},
                    valid_mask=valid_mask,
                    fee_rate={c['fee_rate']}
                )
                metrics = compute_metrics_from_portfolio(
                    port, float(initial_capital), periods_per_year={c['periods_per_year']}
                )
                row = {{
                    'GMA_Period': int(gp),
                    'KAMA_Period': int(kp),
                    'Final_Portfolio_Value': float(final_val),
                    'Number_of_Trades': int(trades),
                    'Buy_Count': int(buy_count),
                    'Sell_Count': int(sell_count),
                }}
                row.update(metrics)
                
            elif "{engine_type}" == "edge_long_short":
                # Crossover long/short
                long_edges = {buy_expr}
                short_edges = {sell_expr}
                port, final_val, transitions, long_bars, short_bars = {engine_name}(
                    close, long_edges, short_edges, float(initial_capital),
                    start_flat=True,
                    valid_mask=valid_mask,
                    fee_rate={c['fee_rate']}
                )
                metrics = compute_metrics_from_portfolio(
                    port, float(initial_capital), periods_per_year={c['periods_per_year']}
                )
                row = {{
                    'GMA_Period': int(gp),
                    'KAMA_Period': int(kp),
                    'Final_Portfolio_Value': float(final_val),
                    'Transitions': int(transitions),
                    'Long_Bars': int(long_bars),
                    'Short_Bars': int(short_bars),
                }}
                row.update(metrics)
                
            elif "{engine_type}" == "regime_only":
                # Regime long-only
                regime = compute_regime(g, k, greater_than=True, tie_rule='{c['tie_rule']}')
                port, final_val, trades, long_bars, flat_bars = run_backtest_regime_long_only_nb(
                    close, regime, float(initial_capital),
                    valid_mask=valid_mask,
                    fee_rate={c['fee_rate']}
                )
                metrics = compute_metrics_from_portfolio(
                    port, float(initial_capital), periods_per_year={c['periods_per_year']}
                )
                row = {{
                    'GMA_Period': int(gp),
                    'KAMA_Period': int(kp),
                    'Final_Portfolio_Value': float(final_val),
                    'Number_of_Trades': int(trades),
                    'Long_Bars': int(long_bars),
                    'Flat_Bars': int(flat_bars),
                }}
                row.update(metrics)
                
            else:  # regime_short
                # Regime long/short
                regime = compute_regime(g, k, greater_than=True, tie_rule='{c['tie_rule']}')
                port, final_val, transitions, long_bars, short_bars = run_backtest_regime_long_short_nb(
                    close, regime, float(initial_capital),
                    valid_mask=valid_mask,
                    fee_rate={c['fee_rate']}
                )
                metrics = compute_metrics_from_portfolio(
                    port, float(initial_capital), periods_per_year={c['periods_per_year']}
                )
                row = {{
                    'GMA_Period': int(gp),
                    'KAMA_Period': int(kp),
                    'Final_Portfolio_Value': float(final_val),
                    'Transitions': int(transitions),
                    'Long_Bars': int(long_bars),
                    'Short_Bars': int(short_bars),
                }}
                row.update(metrics)
            
            out.append(row)
        return out

    # Parallel across KAMA only (threads to avoid numba recompilation per process)
    results_nested = Parallel(n_jobs=n_jobs, prefer='threads')(
        delayed(eval_for_k)(kp) for kp in k_periods
    )
    results = [r for sub in results_nested for r in sub]
    return pd.DataFrame(results)


if __name__ == "__main__":
    df_data = load_and_clean_data()
    all_df = parameter_sweep_optimized(df_data, initial_capital={c['initial_capital']})

    # Write Excel with multi-sheets including Top-5 tables
    script_dir = os.path.dirname(os.path.abspath(__file__))
    xlsx_path = os.path.join(script_dir, "{c['output_filename']}")
    with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
        all_df.to_excel(writer, index=False, sheet_name='All_Results')
        # Top 5 tables
        def top5(df, col, ascending=False):
            d = df.copy()
            d = d[pd.to_numeric(d[col], errors='coerce').notna()]
            return d.sort_values(col, ascending=ascending).head(5)

        top5(all_df, 'Sharpe_Ratio', ascending=False).to_excel(writer, index=False, sheet_name='Top5_Sharpe')
        top5(all_df, 'Sortino_Ratio', ascending=False).to_excel(writer, index=False, sheet_name='Top5_Sortino')
        top5(all_df, 'Omega_Ratio', ascending=False).to_excel(writer, index=False, sheet_name='Top5_Omega')
        top5(all_df, 'Max_Drawdown_%', ascending=True).to_excel(writer, index=False, sheet_name='Top5_MaxDD')
        top5(all_df, 'Total_Profit_%', ascending=False).to_excel(writer, index=False, sheet_name='Top5_Profit')

    # Optional heatmap
{heatmap_block}'''
        return code

