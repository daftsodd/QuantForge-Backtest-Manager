# Changelog

All notable changes to QuantForge Backtest Manager will be documented in this file.

## [1.0.0] - 2025-01-XX

### Added
- Initial release
- 4-panel layout with file browser, code viewer, execution console, and results viewer
- Syntax-highlighted Python code display
- Live script execution with console output streaming
- Total progress tracking across chunks with ETA estimation
- Real-time progress bar that accumulates across all chunks
- Results parsing and display (Excel files and visualizations)
- Tabbed results viewer (Overview, Statistics, Data Tables, Visualizations)
- File status tracking (Not Run, Running, Completed, Failed)
- Configuration persistence (window size, last folder)
- Right-click context menus for quick actions
- Keyboard shortcuts (Ctrl+O, F5, etc.)
- Modern dark theme UI
- Execution metadata logging

### Fixed
- PyQt6 import error handling
- Missing QTreeWidgetItemIterator import
- Progress bar detection for tqdm output
- Chunk progress tracking and accumulation
- Time estimation calculations

### Documentation
- Comprehensive README with installation instructions
- Git setup guide with workflow examples
- Contributing guidelines
- MIT License

---

## Future Releases

### Planned Features
- Distributed execution across multiple computers
- Result comparison tools
- Interactive visualizations with plotly
- Custom metric dashboards
- Database integration for result storage
- Real-time collaboration features
- Advanced filtering and search
- Export capabilities
- Performance profiling

