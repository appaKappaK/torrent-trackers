# Torrent Tracker Manager

A comprehensive desktop application for managing and validating BitTorrent trackers. Built with Python and Tkinter, featuring duplicate detection, multi-protocol validation, and persistent history tracking.

![License](https://img.shields.io/badge/License-GPL%202.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.7%2B-green.svg)
![Architecture](https://img.shields.io/badge/Architecture-MVC-orange.svg)

## Features

### 🔍 Advanced Duplicate Detection
- **Smart URL Extraction**: Parse tracker URLs from any text input
- **URL Normalization**: Intelligent duplicate removal with protocol-aware normalization
- **Multi-Protocol Support**: HTTP, HTTPS, UDP, and magnet links
- **Batch Processing**: Handle large tracker lists efficiently

### ✅ Multi-Protocol Validation
- **Concurrent Validation**: Multi-threaded validation with configurable workers
- **Protocol-Specific Methods**: 
  - HTTP/HTTPS: HEAD/GET requests with proper redirect handling
  - UDP: Native BitTorrent protocol implementation
  - Magnet: Syntax validation and info hash extraction
- **Real-time Progress**: Live updates with progress bars and status indicators
- **Configurable Timeouts**: Adjustable validation thresholds per protocol

### 📊 Comprehensive Analytics & History
- **Persistent Storage**: SQLite database with optimized schema
- **Reliability Scoring**: Success rate tracking with minimum check thresholds
- **Favorite System**: Custom notes and quick access to preferred trackers
- **Performance Metrics**: Response time tracking and statistical analysis
- **Validation Sessions**: Complete history of batch operations

### 🎨 Modern User Interface
- **Tab-Based Workflow**: Logical workflow (Find → Validate → Export → History)
- **Theme Support**: Light and dark mode with persistent preferences
- **Auto-Save**: Batched configuration saves for optimal performance
- **Responsive Design**: Real-time UI updates during validation
- **Keyboard Shortcuts**: Efficient workflow navigation

### 📤 Flexible Export System
- **Multiple Formats**: TXT, JSON, CSV, YAML export options
- **Clipboard Integration**: One-click copy of working trackers
- **Filtered Exports**: Working/dead/all trackers with metadata
- **Structured Data**: Complete validation results with timestamps
- **Preset Management**: Built-in tracker list presets

### 🔧 Advanced Features
- **Network Interface Binding**: Linux-specific interface selection
- **Resource Monitoring**: System health checks and performance optimization
- **Auto-Save Management**: Intelligent batched configuration saves
- **Plugin Architecture**: Extensible design for custom functionality
- **Comprehensive Logging**: Detailed operation logging for debugging

---

## Project Structure
```
torrent-tracker/
├── controllers/
│   ├── __init__.py
│   └── main_controller.py          # Main application logic (MVC)
├── models/
│   ├── database_models.py          # SQLite database management
│   ├── __init__.py
│   └── tracker_models.py           # Data classes and collections
├── views/
│   ├── history_view.py             # History and analytics tab
│   ├── __init__.py
│   └── main_view.py                # Primary GUI implementation
├── services/
│   ├── __init__.py
│   ├── plugin_base.py              # Plugin system foundation
│   ├── tracker_parser.py           # URL parsing and normalization
│   └── tracker_validator.py        # Multi-protocol validation
├── network/
│   └── interface_bind.py           # Network interface management
├── utils/
│   └── helpers.py                  # Utility functions and classes
├── config.py                       # Configuration management
├── main.py                         # Application entry point
├── requirements.txt                # Project dependencies
└── README.md                       # Documentation
```
### Key Files
- **`main.py`** - Application entry point with proper initialization
- **`controllers/main_controller.py`** - Core business logic following MVC pattern
- **`views/main_view.py`** - Primary user interface implementation
- **`models/`** - Data models and database management
- **`services/`** - Parser, validator, and plugin services
- **`network/interface_bind.py`** - Linux network interface binding
- **`utils/helpers.py`** - Utility functions and performance tools

---

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Quick Start
1. Clone the repository:
```bash
git clone https://github.com/appaKappaK/tracker-manager.git
cd torrent-tracker
```

2. Create and activate virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
# or
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
```

### Dependencies
Core dependencies include:
- `tkinter` - GUI framework (built-in)
- `sqlite3` - Database (built-in)
- `psutil` - System resource monitoring
- `PyYAML` - YAML export support

---

## Usage

### Basic Workflow

1. **Find Duplicates Tab**
   - Paste tracker lists into the input area
   - Click "Find Duplicates" for intelligent URL normalization
   - Review statistics: total, unique, and duplicate counts

2. **Validate Trackers Tab** 
   - Configure validation settings (workers, timeouts)
   - Select network interface (Linux systems)
   - Start validation with real-time progress monitoring
   - Stop validation at any time with Escape key

3. **Export Results Tab**
   - Export working trackers as plain text for immediate use
   - Save complete results in structured formats (JSON, CSV, YAML)
   - Copy working trackers directly to clipboard
   - Use preset tracker lists for quick setup

4. **History & Analytics Tab**
   - View comprehensive validation history
   - Identify reliable trackers based on success rates
   - Manage favorites with custom notes
   - Analyze performance trends and statistics

### Keyboard Shortcuts

- `Ctrl+D` - Find duplicates
- `Ctrl+V` - Validate trackers  
- `Ctrl+E` - Export results
- `Ctrl+T` - Toggle theme
- `Ctrl+Q` - Quit application
- `Escape` - Stop validation
- `F1` - Show help

---

## Configuration

The application automatically creates a configuration file (`tracker_manager_config.json`) with default settings:

```json
{
  "validation": {
    "max_workers": 10,
    "timeout": 10,
    "socket_timeout": 5,
    "network_interface": null
  },
  "gui": {
    "window_width": 800,
    "window_height": 600,
    "auto_scroll": true,
    "dark_mode": false
  },
  "trackers": {
    "default_ports": {
      "http": 80,
      "https": 443,
      "udp": 6969
    }
  }
}
```

### File Locations
- **Config File**: `tracker_manager_config.json`
- **Database**: `tracker_history.db`
- **Log File**: `tracker_manager.log`
- **Exports**: `working-trackers/` directory

---

## Development

### Code Organization
The project follows strict organizational patterns with clear section headers:

```python
# Example from MainController:
# ===== VIEW AND INITIALIZATION METHODS =====
# ===== NETWORK INTERFACE METHODS =====  
# ===== TRACKER PROCESSING METHODS =====
# ===== VALIDATION CONTROL METHODS =====
# ===== EXPORT AND COPY METHODS =====
# ===== DATABASE AND HISTORY METHODS =====
# ===== STATISTICS AND ANALYSIS METHODS =====
```

### Development Tools
The `tools/` directory contains utilities for development and debugging:
- `check_duplicates.py` - Standalone duplicate checking
- `debug_app.py` - Application debugging utilities
- `test_database.py` - Database functionality testing
- `test_fixes.py` - Patch testing and validation
___
### Extending Functionality

#### Adding New Protocols
```python
class NewProtocolValidator:
    def validate(self, tracker: Tracker) -> ValidationResult:
        # Implement protocol-specific validation
        pass
```

#### Creating New Export Formats
```python
def export_custom_format(self) -> str:
    # Implement custom export logic
    return formatted_data
```

#### Plugin Development
```python
from services.plugin_base import Plugin

class CustomPlugin(Plugin):
    def before_validation(self, trackers):
        # Pre-process trackers
        return processed_trackers
        
    def after_validation(self, results):
        # Post-process results
        return enhanced_results
```

---

## Database Schema

### Core Tables
- **trackers** - Individual tracker records with validation history
- **validation_sessions** - Session summaries for batch validations  
- **favorites** - User-selected favorite trackers with notes

### Optimizations
- **Indexed Queries**: Performance-optimized database access
- **Data Integrity**: SQL constraints and validation rules
- **Efficient Storage**: Normalized URL storage with deduplication

---

## Network Features

### Interface Binding (Linux)
The application supports network interface selection on Linux systems via `network/interface_bind.py`:

```python
# Automatic interface detection
interfaces = validator.interface_binder.detect_interfaces()

# Manual interface selection
validator.set_network_interface('eth0')
```

### Protocol Support
- **HTTP/HTTPS**: Full protocol implementation with connection pooling
- **UDP**: Native BitTorrent tracker protocol
- **Magnet**: URI validation and info hash extraction

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow existing code organization patterns with clear section headers
- Maintain the MVC architecture separation
- Add comprehensive docstrings and comments
- Update documentation for new features
- Use the tools directory for testing and debugging

## License

This project is licensed under the GNU General Public License v2.0 - see the [LICENSE](LICENSE) file for details.