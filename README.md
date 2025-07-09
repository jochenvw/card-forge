# 🎴 CardForge

**CardForge** is a toolkit for generating beautiful, Ray Dalio–style *baseball cards* for people profiles—complete with AI-generated headshots, skills, interests, and aspirations.

Use it to create professional talent snapshots, dynamic team rosters, or personal growth cards in seconds.

---

## 🚀 Quick Start (MVP)

### Prerequisites

- Python 3.10+
- Package manager: `uv` (recommended) or `pip`

> **Why uv?** uv is a fast, modern Python package installer that's 10-100x faster than pip. It provides better dependency resolution, automatic virtual environment management, and works seamlessly with both requirements.txt and pyproject.toml files.

### Installation

#### Option 1: Using uv (Recommended - Fast & Modern)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or on Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# Or with pip: pip install uv

# Clone the repository
git clone https://github.com/jochenvw/card-forge.git
cd card-forge

# Install dependencies with uv (creates virtual environment automatically)
uv sync

# Activate the uv-managed virtual environment (if needed)
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run commands in the uv environment without activating
uv run python generate_card.py --help
```

#### Option 2: Using pip (Traditional)

```bash
# Clone the repository
git clone https://github.com/jochenvw/card-forge.git
cd card-forge

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Option 3: Install as Package with uv

```bash
# Install directly from git
uv pip install git+https://github.com/jochenvw/card-forge.git

# Or install in development mode after cloning
git clone https://github.com/jochenvw/card-forge.git
cd card-forge
uv pip install -e .
```

### Basic Usage

Generate a profile card with the simple command:

**With uv:**
```bash
uv run python generate_card.py --image input_photo.png --markdown profile.md --output output_card.png
```

**With pip/traditional Python:**
```bash
python generate_card.py --image input_photo.png --markdown profile.md --output output_card.png
```

### Example

Try the included example:

**With uv:**
```bash
uv run python generate_card.py --image examples/input_photo.png --markdown examples/profile.md --output my_card.png
```

**With pip/traditional Python:**
```bash
python generate_card.py --image examples/input_photo.png --markdown examples/profile.md --output my_card.png
```

This will generate a profile card combining:
- The profile photo (left side)
- AI-processed summary of skills and aspirations (right side)
- Professional styling with title bar

---

## 📋 Command Line Options

**With uv:**
```bash
uv run python generate_card.py [OPTIONS]
```

**With pip/traditional Python:**
```bash
python generate_card.py [OPTIONS]
```

**Options:**
```
Required:
  --image, -i PATH      Input image file (PNG recommended)
  --markdown, -m PATH   Markdown profile file
  --output, -o PATH     Output PNG file path

Optional:
  --model MODEL         LLM model for text processing (default: microsoft/DialoGPT-medium)
  --width WIDTH         Card width in pixels (default: 800)
  --height HEIGHT       Card height in pixels (default: 600)
  --verbose, -v         Enable detailed output
```

---

## 📝 Profile Format

Create a markdown file with your profile information:

```markdown
# Your Name - Title

## About
Brief description of who you are and what you do.

## Key Competencies
- **Skill 1**: Description of expertise
- **Skill 2**: Another key skill
- **Skill 3**: Additional competency

## Current Aspirations
- Goal or aspiration 1
- Goal or aspiration 2
- Goal or aspiration 3

## Recent Achievements
- Achievement 1
- Achievement 2
```

---

## 🧠 AI Processing

CardForge uses local AI models to:
- Summarize your profile into key bullet points
- Extract the most important skills and aspirations
- Generate professional card content

**GPU Support**: The system automatically detects and uses GPU acceleration when available for faster AI processing.

**Offline Mode**: All processing happens locally on your machine - no cloud dependencies required.

---

## ✨ Features

- 🧠 **Generative AI Summaries**
  - Automatically generate concise descriptions of skills, interests, and aspirations from structured or free-form input.
- 🎨 **Customizable Card Templates**
  - Ready-to-use layouts and styles for different use cases (e.g., professional, casual, team-oriented).
- 🤖 **AI Headshot Integration**
  - Plug in avatar generation services (Midjourney, D-ID, Stability AI) or upload real photos.
- 🖼️ **High-Quality Exports**
  - Render cards to PNG or PDF for printing and sharing.
- 🌐 **API & CLI**
  - Generate cards programmatically or via a command-line tool.

---

## 🧪 Testing

Run the test suite to verify everything works:

**With uv:**
```bash
uv run python test_pipeline.py
```

**With pip/traditional Python:**
```bash
python test_pipeline.py
```

---

## 🔧 Development

### Project Structure

```
card-forge/
├── generate_card.py          # Main CLI application
├── src/
│   ├── markdown_parser.py    # Markdown content parsing
│   ├── llm_processor.py      # AI text processing
│   └── image_composer.py     # Card image generation
├── examples/                 # Sample input files
├── output/                   # Generated cards
├── pyproject.toml            # Modern Python project configuration (uv compatible)
├── requirements.txt          # Legacy pip requirements
├── .python-version           # Python version specification for uv
└── test_pipeline.py          # Test suite
```

### Development Setup

**With uv (Recommended):**
```bash
# Clone and setup development environment
git clone https://github.com/jochenvw/card-forge.git
cd card-forge

# Install with development dependencies
uv sync --extra dev

# Run tests
uv run python test_pipeline.py

# Format code (if dev dependencies installed)
uv run black .
uv run flake8 .
```

**With pip (Traditional):**
```bash
git clone https://github.com/jochenvw/card-forge.git
cd card-forge
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### Adding New Features

1. **New Card Layouts**: Modify `src/image_composer.py`
2. **Better AI Models**: Update `src/llm_processor.py`
3. **Input Formats**: Extend `src/markdown_parser.py`

---

## 📄 License

MIT License - see LICENSE file for details.
