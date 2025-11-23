# Torrent Tracker Manager

A comprehensive desktop application for managing and validating BitTorrent trackers. Clean duplicates, validate tracker status, and maintain a history of reliable trackers.

![License](https://img.shields.io/badge/License-GPL%202.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.7%2B-green.svg)

## Features

### 🔍 Duplicate Detection
- Extract tracker URLs from text input
- Intelligent duplicate removal with URL normalization
- Support for HTTP, HTTPS, UDP, and magnet links
- Batch processing of large tracker lists

### ✅ Tracker Validation
- Multi-threaded validation for performance
- Support for UDP and HTTP tracker protocols
- Real-time progress tracking
- Configurable timeout and worker settings

### 📊 History & Analytics
- Persistent storage of validation results
- Tracker reliability scoring based on historical data
- Favorite trackers with custom notes
- Success rate statistics and performance metrics

### 🎨 User-Friendly Interface
- Tab-based workflow (Find → Validate → Export → History)
- Light and dark theme support
- Auto-scroll and progress indicators
- Keyboard shortcuts for common actions

### 📤 Export Options
- Multiple format support (TXT, JSON, CSV, YAML)
- Copy working trackers to clipboard
- Export filtered results (working/dead/all)
- Structured data with validation metadata

---

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Steps
1. Clone the repository:
```bash
git clone https://github.com/appaKappaK/tracker-manager.git
cd tracker-manager
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

---

## Usage

### Basic Workflow

1. **Find Duplicates Tab**
   - Paste your tracker list into the input area
   - Click "Find Duplicates" to remove redundant URLs
   - Review the unique trackers found

2. **Validate Trackers Tab** 
   - Click "Validate Trackers" to start validation
   - Monitor progress with real-time updates
   - Working and dead trackers are separated automatically

3. **Export Results Tab**
   - Export working trackers as plain text
   - Save complete results in JSON format
   - Copy working trackers to clipboard

4. **History & Analytics Tab**
   - View validation history and statistics
   - Identify reliable trackers based on success rate
   - Manage favorite trackers

### Keyboard Shortcuts

- `Ctrl+D` - Find duplicates
- `Ctrl+V` - Validate trackers
- `Ctrl+T` - Toggle theme
- `Ctrl+Q` - Quit application
- `Escape` - Stop validation
- `F1` - Show help

---

## Tracker Validation Methods

The application uses different validation techniques depending on the tracker protocol:

### HTTP/HTTPS Trackers
- **HEAD Request**: First attempts a lightweight HEAD request to check availability
- **GET Fallback**: If HEAD fails, performs a full GET request
- **Status Codes**: Considers 2xx status codes as working
- **Redirect Handling**: Automatically follows HTTP redirects
- **Connection Pooling**: Reuses connections for better performance

### UDP Trackers
- **Protocol Handshake**: Implements BitTorrent UDP tracker protocol
- **Connection ID**: Sends proper connection establishment packet
- **Timeout Handling**: Configurable socket timeouts (default: 5 seconds)
- **Port Detection**: Uses default UDP port 6969 if not specified

### Magnet Links
- **Syntax Validation**: Checks for valid magnet link structure
- **Info Hash Extraction**: Validates info hash presence and format
- **Always Working**: Treated as always valid (client-side resolution)

### Validation Features
- **Multi-threaded**: Validates multiple trackers simultaneously
- **Configurable Timeouts**: Adjustable per-protocol timeouts
- **Error Handling**: Comprehensive exception handling with detailed error messages
- **Resource Management**: Proper cleanup of sockets and HTTP sessions
- **Stop Mechanism**: Can safely stop validation mid-process

---

## Configuration

The application automatically creates a configuration file (`tracker_manager_config.json`) with default settings:

```json
{
  "validation": {
    "max_workers": 10,
    "timeout": 10,
    "socket_timeout": 5
  },
  "gui": {
    "window_width": 800,
    "window_height": 600,
    "auto_scroll": true,
    "dark_mode": false
  }
}
```

---

## Project Structure

```
tracker-manager/
├── controllers/
│   └── main_controller.py     # Main application logic
├── models/
│   ├── tracker_models.py      # Data classes
│   └── database_models.py     # Database models
├── views/
│   ├── main_view.py           # Main GUI
│   └── history_view.py        # History tab
├── services/
│   ├── tracker_parser.py      # URL parsing
│   └── tracker_validator.py   # Validation logic
├── config.py                  # Configuration management
├── main.py                    # Application entry point
└── requirements.txt           # Dependencies
```

## Database

The application uses SQLite with the following schema:

- **trackers** - Individual tracker records with validation history
- **validation_sessions** - Session summaries for batch validations  
- **favorites** - User-selected favorite trackers

---

## Development

### Adding New Features

The application follows MVC architecture:

- **Models**: Data structures in `models/`
- **Views**: GUI components in `views/` 
- **Controllers**: Business logic in `controllers/`

### Plugin System

Extend functionality by implementing the `Plugin` base class:

```python
from plugin_base import Plugin

class CustomPlugin(Plugin):
    def before_validation(self, trackers):
        # Pre-process trackers
        return trackers
        
    def after_validation(self, results):
        # Post-process results
        return results
```

---

## License

This project is licensed under the GNU General Public License v2.0 - see the [LICENSE](LICENSE) file for details.

## Support

For bugs and feature requests, please create an issue on GitHub.

## Acknowledgments

- Built with Python and Tkinter
- Uses SQLite for data persistence
- Icons from Unicode emoji set
