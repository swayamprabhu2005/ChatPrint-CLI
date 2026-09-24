# Supported Providers & Heuristic Rules

This document details the provider implementations for **Google Gemini AI Mode** and **ChatGPT**.

---

## 1. GeminiProvider (`src/chatprint/providers/gemini.py`)

### Detection Signals
- Snapshot location containing `gemini.google.com` or `google.com/search`.
- Page title containing `Google Search`, `Gemini`, or `Google AI`.
- HTML attributes: `data-attrid="wa:/description"`, `div[aria-label*="AI Overview"]`, `data-message-author-role="model"`, `user-query`, `model-response`.

### Unwanted UI Purged
- `#searchform`, `#tsf`, `#header`, `#top_nav`, `#hdtb`, `#appbar` (Google Search header and tabs)
- `div[aria-label*='Google Account']`, `div.gb_` (Account avatar and profile menus)
- `#rhs`, `#rhs_block`, `.rhsvw`, `div[class*='commercial-unit']` (Right sidebar knowledge panel and ads)
- `div[data-attrid*='wa:/paa']` (People Also Ask widget)
- `#footcnt`, `#fbar`, `footer` (Footers)
- Action buttons: Copy, Share, Export to Docs, feedback icons.

### Conversation Turn Extraction
- **Pattern 1 (Multi-Turn Chat)**: Matches turns via `[data-message-author-role]`, `user-query`, and `model-response`.
- **Pattern 2 (AI Overview / Search AI Mode)**: Extracts the user question from the search query `<textarea name="q">` or page title, and matches with the main AI Overview response container.
- **Pattern 3 (Fallback Main Container)**: Captures `#center_col` or `<main>` content blocks.

---

## 2. ChatGPTProvider (`src/chatprint/providers/chatgpt.py`)

### Detection Signals
- Snapshot location containing `chatgpt.com` or `chat.openai.com`.
- Title containing `ChatGPT`.
- DOM attributes: `[data-message-author-role]`, `[data-testid^="conversation-turn-"]`.

### Unwanted UI Purged
- `nav`, `aside`, `#sidebar`, `div[aria-label*='Chat history']` (Left history sidebar)
- `div[data-testid='profile-button']`, `button[aria-label*='User menu']` (Profile menu)
- `header`, `div[data-testid='model-switcher']` (Model selector)
- Action buttons: Copy, edit prompt, thumbs up/down, regenerate.
- Footer disclaimers and upgrade-to-plus banners.

### Conversation Turn Extraction
- Loops through all `[data-testid^="conversation-turn-"]` elements.
- Inspects `data-message-author-role` (`user` vs `assistant`).
- Extracts inner markdown containers (`div.markdown.prose`).

---

## 3. GenericProvider (`src/chatprint/providers/generic.py`)

Acts as an automated fallback when confidence for Gemini or ChatGPT is low or unknown.
- Uses `score_conversation_container(tag)` to identify the highest density conversational area.
- Detects alternating child speaker elements.
- Formats content blocks safely into the `Conversation` model.
