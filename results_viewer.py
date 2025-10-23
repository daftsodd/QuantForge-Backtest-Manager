"""
Results Viewer for displaying backtest results.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QLabel, 
                              QTableWidget, QTableWidgetItem, QScrollArea,
                              QGridLayout, QFrame, QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont
import pandas as pd


class ResultsViewer(QWidget):
    """Widget for displaying backtest results in tabbed interface."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_results = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        self.header_label = QLabel("Results")
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
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #1E1E1E;
            }
            QTabBar::tab {
                background-color: #2D2D30;
                color: #CCCCCC;
                padding: 8px 20px;
                margin-right: 2px;
                border: none;
            }
            QTabBar::tab:selected {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            QTabBar::tab:hover {
                background-color: #3E3E42;
            }
        """)
        
        # Create tabs
        self.overview_tab = self._create_overview_tab()
        self.statistics_tab = self._create_statistics_tab()
        self.tables_tab = self._create_tables_tab()
        self.visualizations_tab = self._create_visualizations_tab()
        
        self.tabs.addTab(self.overview_tab, "Overview")
        self.tabs.addTab(self.statistics_tab, "Statistics")
        self.tabs.addTab(self.tables_tab, "Data Tables")
        self.tabs.addTab(self.visualizations_tab, "Visualizations")
        
        layout.addWidget(self.tabs)
    
    def _create_overview_tab(self):
        """Create the overview tab with summary cards."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #1E1E1E; }")
        
        scroll_content = QWidget()
        self.overview_layout = QGridLayout(scroll_content)
        self.overview_layout.setSpacing(15)
        
        # Placeholder label
        self.overview_placeholder = QLabel("No results to display")
        self.overview_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.overview_placeholder.setStyleSheet("QLabel { color: #858585; font-size: 14px; }")
        self.overview_layout.addWidget(self.overview_placeholder, 0, 0)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        return widget
    
    def _create_statistics_tab(self):
        """Create the statistics tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(2)
        self.stats_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.stats_table.horizontalHeader().setStretchLastSection(True)
        self.stats_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.stats_table.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E1E;
                color: #CCCCCC;
                gridline-color: #3E3E42;
                border: none;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #094771;
            }
            QHeaderView::section {
                background-color: #2D2D30;
                color: #CCCCCC;
                padding: 8px;
                border: none;
                border-right: 1px solid #3E3E42;
                border-bottom: 1px solid #3E3E42;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.stats_table)
        return widget
    
    def _create_tables_tab(self):
        """Create the data tables tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.data_table = QTableWidget()
        self.data_table.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E1E;
                color: #CCCCCC;
                gridline-color: #3E3E42;
                border: none;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #094771;
            }
            QHeaderView::section {
                background-color: #2D2D30;
                color: #CCCCCC;
                padding: 8px;
                border: none;
                border-right: 1px solid #3E3E42;
                border-bottom: 1px solid #3E3E42;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.data_table)
        return widget
    
    def _create_visualizations_tab(self):
        """Create the visualizations tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #1E1E1E; }")
        
        scroll_content = QWidget()
        self.viz_layout = QVBoxLayout(scroll_content)
        self.viz_layout.setSpacing(20)
        self.viz_layout.setContentsMargins(15, 15, 15, 15)
        
        # Placeholder
        self.viz_placeholder = QLabel("No visualizations available")
        self.viz_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.viz_placeholder.setStyleSheet("QLabel { color: #858585; font-size: 14px; }")
        self.viz_layout.addWidget(self.viz_placeholder)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        return widget
    
    def display_results(self, results):
        """Display parsed results in the viewer."""
        self.current_results = results
        self.header_label.setText("Results - Available")
        
        # Update overview
        self._update_overview(results)
        
        # Update statistics
        self._update_statistics(results.get('statistics', {}))
        
        # Update data tables
        self._update_tables(results.get('tables', []))
        
        # Update visualizations
        self._update_visualizations(results.get('images', []))
    
    def _update_overview(self, results):
        """Update the overview tab with summary cards."""
        # Clear existing widgets
        while self.overview_layout.count():
            item = self.overview_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        stats = results.get('statistics', {})
        if not stats:
            self.overview_placeholder = QLabel("No statistics available")
            self.overview_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.overview_placeholder.setStyleSheet("QLabel { color: #858585; font-size: 14px; }")
            self.overview_layout.addWidget(self.overview_placeholder, 0, 0)
            return
        
        # Get best config if available
        best_config = stats.get('best_config', {})
        
        # Create summary cards
        cards = []
        if 'Total_Profit_%' in best_config:
            cards.append(("Total Profit", f"{best_config['Total_Profit_%']:.2f}%", "#4EC9B0"))
        if 'Sharpe_Ratio' in best_config:
            cards.append(("Sharpe Ratio", f"{best_config['Sharpe_Ratio']:.3f}", "#569CD6"))
        if 'Max_Drawdown_%' in best_config:
            cards.append(("Max Drawdown", f"{best_config['Max_Drawdown_%']:.2f}%", "#F48771"))
        if 'Number_of_Trades' in best_config:
            cards.append(("Trades", f"{int(best_config['Number_of_Trades'])}", "#DCDCAA"))
        
        # Add cards to grid
        for idx, (title, value, color) in enumerate(cards):
            card = self._create_summary_card(title, value, color)
            row = idx // 2
            col = idx % 2
            self.overview_layout.addWidget(card, row, col)
        
        # Add best config info if available
        if best_config:
            config_label = QLabel("<b>Best Configuration:</b>")
            config_label.setStyleSheet("QLabel { color: #CCCCCC; font-size: 13px; }")
            self.overview_layout.addWidget(config_label, (len(cards) + 1) // 2, 0, 1, 2)
            
            config_text = "<br>".join([f"{k}: {v}" for k, v in best_config.items() 
                                       if k not in ['Total_Profit_%', 'Sharpe_Ratio', 
                                                   'Max_Drawdown_%', 'Number_of_Trades']])
            config_detail = QLabel(config_text)
            config_detail.setStyleSheet("QLabel { color: #858585; font-size: 12px; }")
            self.overview_layout.addWidget(config_detail, (len(cards) + 3) // 2, 0, 1, 2)
        
        self.overview_layout.addItem(self.overview_layout.itemAt(0))  # Add stretch
    
    def _create_summary_card(self, title, value, color):
        """Create a summary card widget."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #252526;
                border-left: 4px solid {color};
                border-radius: 4px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("QLabel { color: #858585; font-size: 12px; }")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"QLabel {{ color: {color}; font-size: 24px; font-weight: bold; }}")
        layout.addWidget(value_label)
        
        return card
    
    def _update_statistics(self, statistics):
        """Update the statistics table."""
        self.stats_table.setRowCount(0)
        
        for metric, value in statistics.items():
            if metric == 'best_config':
                continue
            
            row = self.stats_table.rowCount()
            self.stats_table.insertRow(row)
            
            metric_item = QTableWidgetItem(metric.replace('_', ' ').title())
            self.stats_table.setItem(row, 0, metric_item)
            
            if isinstance(value, float):
                value_item = QTableWidgetItem(f"{value:.4f}")
            else:
                value_item = QTableWidgetItem(str(value))
            self.stats_table.setItem(row, 1, value_item)
    
    def _update_tables(self, tables):
        """Update the data tables tab."""
        if not tables:
            return
        
        # Display the first table (or you could add a selector)
        name, df = tables[0]
        
        self.data_table.setRowCount(len(df))
        self.data_table.setColumnCount(len(df.columns))
        self.data_table.setHorizontalHeaderLabels(df.columns.tolist())
        
        for i in range(len(df)):
            for j in range(len(df.columns)):
                value = df.iloc[i, j]
                if pd.isna(value):
                    item = QTableWidgetItem("")
                elif isinstance(value, float):
                    item = QTableWidgetItem(f"{value:.4f}")
                else:
                    item = QTableWidgetItem(str(value))
                self.data_table.setItem(i, j, item)
    
    def _update_visualizations(self, images):
        """Update the visualizations tab."""
        # Clear existing widgets
        while self.viz_layout.count():
            item = self.viz_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not images:
            self.viz_placeholder = QLabel("No visualizations available")
            self.viz_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.viz_placeholder.setStyleSheet("QLabel { color: #858585; font-size: 14px; }")
            self.viz_layout.addWidget(self.viz_placeholder)
            return
        
        # Display each image
        for name, image_path in images:
            # Title
            title = QLabel(name.replace('_', ' ').title())
            title.setStyleSheet("QLabel { color: #CCCCCC; font-size: 14px; font-weight: bold; }")
            self.viz_layout.addWidget(title)
            
            # Image
            image_label = QLabel()
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # Scale image to fit width (max 800px)
                scaled_pixmap = pixmap.scaledToWidth(800, Qt.TransformationMode.SmoothTransformation)
                image_label.setPixmap(scaled_pixmap)
            else:
                image_label.setText(f"Could not load image: {image_path}")
                image_label.setStyleSheet("QLabel { color: #F48771; }")
            
            self.viz_layout.addWidget(image_label)
        
        self.viz_layout.addStretch()
    
    def clear(self):
        """Clear all results."""
        self.current_results = None
        self.header_label.setText("Results")
        
        # Clear overview
        while self.overview_layout.count():
            item = self.overview_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.overview_placeholder = QLabel("No results to display")
        self.overview_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.overview_placeholder.setStyleSheet("QLabel { color: #858585; font-size: 14px; }")
        self.overview_layout.addWidget(self.overview_placeholder, 0, 0)
        
        # Clear statistics
        self.stats_table.setRowCount(0)
        
        # Clear tables
        self.data_table.setRowCount(0)
        self.data_table.setColumnCount(0)
        
        # Clear visualizations
        while self.viz_layout.count():
            item = self.viz_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.viz_placeholder = QLabel("No visualizations available")
        self.viz_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.viz_placeholder.setStyleSheet("QLabel { color: #858585; font-size: 14px; }")
        self.viz_layout.addWidget(self.viz_placeholder)

