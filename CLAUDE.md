# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an enhanced fork of labelImg - a graphical image annotation tool written in Python with PyQt5. The project has been significantly extended with AI-powered features, batch operations, project management, and advanced UI improvements.

**Key Technologies:**
- Python 3.6+ with PyQt5 for GUI
- YOLO (ultralytics) for AI-powered object detection
- PyTorch for deep learning functionality
- XML/JSON for annotation file formats (Pascal VOC, YOLO, CreateML)

## Development Commands

### Running the Application
```bash
# Main application
python labelImg.py
python labelImg.py [IMAGE_PATH] [PRE-DEFINED_CLASS_FILE]

# Alternative using pip installation
pip install -e .
labelImg
```

### Development Setup
```bash
# Install dependencies
pip install -r requirements_ai.txt

# Generate Qt resources (required after UI changes)
pyrcc5 -o libs/resources.py resources.qrc

# Run tests
python -m unittest discover tests
```

### Building/Packaging
```bash
# Using PyInstaller (Windows)
pyinstaller labelImg.spec
# OR
python 打包labelImg.bat

# Using Makefile (Linux/Mac)
make qt5py3    # Generate resources
make test      # Run tests
make clean     # Clean build files
```

## Architecture Overview

### Main Application Entry
- `labelImg.py` - Main application file containing the `MainWindow` class
- Entry point for the GUI application with extensive feature integration

### Core Libraries Structure (`libs/`)

**Core Components:**
- `canvas.py` - Drawing canvas for image display and annotation editing
- `shape.py` - Geometric shape classes for bounding boxes and annotations
- `labelFile.py` - Annotation file I/O operations (XML, YOLO, JSON formats)
- `settings.py` - Application settings and configuration management

**AI Assistant Module (`libs/ai_assistant/`):**
- `yolo_predictor.py` - YOLO model integration for object detection
- `model_manager.py` - AI model loading and management
- `batch_processor.py` - Batch prediction operations
- `confidence_filter.py` - Prediction confidence filtering

**Project Management:**
- `project_manager.py` - Multi-project workspace management
- `project_config_adapter.py` - Configuration adaptation layer
- `project_management_dialog.py` - Project management UI
- `project_selector.py` - Project switching component

**UI Enhancement:**
- `ai_assistant_panel.py` - AI assistant docked widget
- `batch_operations.py` - Batch operation utilities
- `ui_styles.py` - Unified UI styling
- `shortcut_manager.py` - Keyboard shortcut management

**File Format Support:**
- `pascal_voc_io.py` - Pascal VOC XML format
- `yolo_io.py` - YOLO format support
- `create_ml_io.py` - Apple CreateML format

### Configuration System

The application uses a hierarchical configuration system:

1. **Global configs/** - Legacy system configuration
2. **Per-project configs/** - Project-specific settings stored in `projects/[project_name]/configs/`
3. **Runtime settings** - Managed through `Settings` class

### Key Patterns

**Event-Driven Architecture:**
- Heavy use of PyQt signals/slots for component communication
- Custom signals for AI prediction results, project switching, batch operations

**Modular Design:**
- Each major feature is encapsulated in its own module
- Dependency injection through manager classes
- Plugin-like architecture for AI models

**Configuration Management:**
- YAML for structured configs (classes, training parameters)
- JSON for simple key-value settings
- Automatic migration from legacy configurations

## Testing Strategy

Run comprehensive tests using the numerous test files:
```bash
# Run specific feature tests
python test_ai_assistant.py
python test_project_management.py
python test_batch_operations.py

# Run integration tests
python test_final_integration.py
```

## Common Development Tasks

### Adding New AI Models
1. Extend `ModelManager` class in `libs/ai_assistant/model_manager.py`
2. Implement predictor interface in AI assistant module
3. Update UI components in `ai_assistant_panel.py`

### Extending File Format Support
1. Create new I/O module following pattern of `pascal_voc_io.py`
2. Register format in `labelFile.py`
3. Update UI format selection components

### Adding New Project Configuration
1. Extend project metadata schema in `project_manager.py`
2. Update configuration adapter in `project_config_adapter.py`
3. Modify project management dialogs as needed

### UI Modifications
1. Update Qt resource file: `resources.qrc`
2. Regenerate resources: `pyrcc5 -o libs/resources.py resources.qrc`
3. Apply consistent styling through `ui_styles.py`

## Development Notes

- **Chinese Language Support**: The codebase includes extensive Chinese language support and documentation
- **Performance Optimization**: Image processing operations are optimized with caching and background processing
- **Error Handling**: Comprehensive error handling throughout with user-friendly messages
- **Memory Management**: Careful attention to memory usage for large dataset processing

## File Locations

- **User Settings**: `~/.labelImgSettings.pkl` (legacy) or `projects/[project]/configs/`
- **Predefined Classes**: `data/predefined_classes.txt`
- **Project Data**: `projects/[project_name]/` directory structure
- **AI Models**: `projects/shared/models/` for shared models or `projects/[project]/models/` for project-specific

## Important Implementation Details

- The application maintains backward compatibility with original labelImg workflows
- AI features are optional and gracefully degrade if dependencies are missing
- Project management system automatically migrates legacy configurations
- Batch operations include progress tracking and cancellation support
- Multi-format annotation support with automatic conversion capabilities