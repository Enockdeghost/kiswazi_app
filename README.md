# kiswazi_app

kiswazi_app is a modern, feature-rich desktop dictionary and language learning tool built with Python and PyQt5. It is designed to help users learn new vocabulary, translate text, practice with flashcards, and improve their grammar—all in an intuitive graphical interface.

## Features

- **Comprehensive Dictionary**: Search for words, view definitions, part of speech, pronunciation, etymology, example sentences, synonyms, and antonyms.
- **Word of the Day & Random Word**: Get inspired with a new word every day or discover random vocabulary.
- **Search History & Bookmarks**: Keep track of your previous searches and bookmark important words for quick access.
- **Custom Word Lists**: Create your own vocabulary lists for GRE, TOEFL, business terms, or custom learning.
- **Flashcard Practice**: Practice vocabulary using interactive flashcards with definitions.
- **Translator**: Translate text between several languages (mock implementation; can be integrated with real APIs).
- **Grammar Checker**: Quickly check your grammar and get suggestions (simple mockup, extendable for advanced corrections).
- **Pronunciation Audio**: Listen to word pronunciations powered by Google Text-to-Speech (gTTS).
- **Dark Mode**: Switch between light and dark themes for comfortable viewing.
- **User Settings**: Customize appearance, font size, pronunciation, auto-translation, and manage your data.
- **Data Import/Export**: Safely back up or transfer your personal data (history, bookmarks, custom lists).

## Getting Started

### Prerequisites

- Python 3.7+
- [PyQt5](https://pypi.org/project/PyQt5/)
- [gTTS](https://pypi.org/project/gTTS/)
- [pygame](https://pypi.org/project/pygame/)
- [requests](https://pypi.org/project/requests/)

Install dependencies:

```bash
pip install PyQt5 gTTS pygame requests
```

### Running the App

1. Clone the repository:

    ```bash
    git clone https://github.com/Enockdeghost/kiswazi_app.git
    cd kiswazi_app
    ```

2. Run the main Python script:

    ```bash
    python <your_script_name>.py
    ```

    Replace `<your_script_name>.py` with the actual filename containing the provided code above.

### File Structure

- `dictionary.db`: SQLite database, created automatically on first run
- `README.md`: Project documentation

## Key Classes & Structure

- **DatabaseManager**: Handles all database operations (words, history, bookmarks, lists, settings)
- **WordCard**: UI component displaying detailed info for each word, including audio and bookmark functionality
- **kiswaziDictionary**: The main application window, with tabs for dictionary, translator, vocabulary practice, grammar checking, history, and settings
- **SplashScreen**: Displays an animated splash screen during app startup

## Usage

- **Search Words**: Type a word in the search bar and press Enter or click "Search".
- **Bookmark**: Click the ⭐ icon on a word card to bookmark it.
- **Get Pronunciation**: Click the 🔊 icon to hear the word pronounced.
- **Practice Vocabulary**: Go to the "Vocabulary" tab, create or select a word list, and use flashcards.
- **Translate Text**: Use the "Translator" tab to mock-translate between languages.
- **Check Grammar**: Enter text in the "Grammar" tab and click "Check Grammar" for suggestions.
- **Switch Themes**: Use the "🌙" or "☀️" button in the header or settings to toggle dark mode.
- **Import/Export Data**: Use buttons in the settings to back up or restore your history, bookmarks, and custom lists.

## Customization & Extending

- **Add More Words**: Modify `populate_sample_data` or extend the database.
- **Integrate Real Translation/Grammar APIs**: Replace the mock functions with actual API calls.
- **Enhance Flashcards and Lists**: Import/export from CSV, add spaced repetition, etc.

## Troubleshooting

- If you encounter issues with audio playback:
    - Ensure `pygame` and `gTTS` are installed.
    - Check your system's audio output settings.
- If the GUI does not start, check that all dependencies are correctly installed and use Python 3.7+.

