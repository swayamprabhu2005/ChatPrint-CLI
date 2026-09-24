# Contributing to AI Conversation CLI

Thank you for your interest in contributing to AI Conversation CLI!

## Code of Conduct
Please be respectful and constructive in all discussions, pull requests, and issue reports.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/swayamprabhu2005/AI-Conversation-CLI.git
   cd AI-Conversation-CLI
   ```

2. Create a virtual environment using Python 3.10:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

3. Install editable package with dev dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Verify installation:
   ```bash
   ai-conversation --version
   ai-conversation doctor
   ```

## Running Tests
Run the test suite with pytest:
```bash
pytest
```

Run linter:
```bash
ruff check src tests
```

## Adding a New AI Conversation Provider
To add support for a new provider:
1. Create a new file in `src/ai_conversation/providers/<provider_name>.py`.
2. Inherit from `ConversationProvider` in `src/ai_conversation/providers/base.py`.
3. Implement `detect_confidence` and `extract`.
4. Register the provider in `src/ai_conversation/providers/__init__.py`.
5. Add representative fixtures in `tests/fixtures/<provider_name>/`.
6. Add unit and integration tests.
