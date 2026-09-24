"""ChatGPT conversation provider."""

import copy
import re
from typing import Any

from bs4 import BeautifulSoup

from chatprint.extraction.cleaner import clean_dom
from chatprint.extraction.normalizer import (
    element_to_content_blocks,
)
from chatprint.models import (
    Conversation,
    Message,
    Role,
)
from chatprint.providers.base import ConversationProvider

_CHATGPT_UNWANTED_SELECTORS = [
    # Sidebar & navigation
    "nav",
    "aside",
    "#sidebar",
    "div[aria-label*='Chat history']",
    "div[aria-label*='History']",
    # Account & Profile
    "div[data-testid='profile-button']",
    "button[aria-label*='User menu']",
    "div[class*='user-menu']",
    # Model selector & Header
    "header",
    "div[data-testid='model-switcher']",
    # Action buttons (copy, edit, regenerate, speech, thumbs)
    "button",
    "div[role='button']",
    "div[class*='action-buttons']",
    "div[class*='text-gray-400']",
    # Footer & Upgrade prompts
    "footer",
    "div[class*='text-xs text-center']",
    "a[href*='pricing']",
]


class ChatGPTProvider(ConversationProvider):
    """Provider for ChatGPT saved conversations."""

    name = "chatgpt"
    display_name = "ChatGPT"

    def detect_confidence(
        self,
        soup: BeautifulSoup,
        raw_html: str,
        metadata: dict[str, Any],
    ) -> float:
        score = 0.0
        snapshot_loc = metadata.get("snapshot_location", "").lower()
        title = (soup.title.string.strip() if soup.title and soup.title.string else "").lower()

        # Disqualify if explicitly Google Search / Gemini
        if "google.com" in snapshot_loc or "google search" in title:
            return 0.0

        # URL / Location signals
        if "chatgpt.com" in snapshot_loc or "chat.openai.com" in snapshot_loc:
            score += 0.8

        # Title signals
        if "chatgpt" in title:
            score += 0.5

        # Structural & Textual signals
        raw_lower = raw_html.lower()
        if "data-message-author-role" in raw_lower:
            score += 0.7
        if "conversation-turn-" in raw_lower:
            score += 0.6
        if "openai" in raw_lower:
            score += 0.3
        if "chatgpt" in raw_lower:
            score += 0.3

        return min(1.0, score)

    def extract(
        self,
        soup: BeautifulSoup,
        resources: dict[str, bytes],
        original_filename: str,
    ) -> Conversation:
        working_soup = copy.copy(soup)

        # Extract title
        page_title = ""
        if working_soup.title and working_soup.title.string:
            page_title = working_soup.title.string.strip()
            # Clean " | ChatGPT" or " - ChatGPT"
            page_title = re.sub(r"\s*[-|]\s*ChatGPT$", "", page_title, flags=re.IGNORECASE).strip()

        # Clean DOM of unwanted UI components
        clean_dom(working_soup, _CHATGPT_UNWANTED_SELECTORS)

        messages: list[Message] = []
        turn_order = 1

        # Look for conversation turns
        turns = working_soup.select(
            "[data-testid^='conversation-turn-'], [data-message-author-role], article, .conversation-turn"
        )

        for turn in turns:
            # Determine role
            role_attr = (
                turn.get("data-message-author-role")
                or (turn.find(attrs={"data-message-author-role": True}) or {}).get("data-message-author-role")
                or ""
            ).lower()

            classes = " ".join(turn.get("class") or []).lower()

            if role_attr == "user" or "user" in classes:
                role = Role.USER
            elif role_attr in ("assistant", "model") or "assistant" in classes or "agent" in classes:
                role = Role.ASSISTANT
            else:
                # Fallback role inference based on turn order
                role = Role.USER if turn_order % 2 == 1 else Role.ASSISTANT

            # Find prose/markdown content container if present, else use turn
            content_container = (
                turn.find("div", class_=re.compile(r"(markdown|prose)", re.IGNORECASE))
                or turn
            )

            blocks = element_to_content_blocks(content_container)
            if blocks:
                messages.append(Message(role=role, blocks=blocks, order=turn_order))
                turn_order += 1

        # Fallback if no explicit turn selectors matched
        if not messages:
            main_container = working_soup.find("main") or working_soup.body
            if main_container:
                blocks = element_to_content_blocks(main_container)
                if blocks:
                    messages.append(
                        Message(
                            role=Role.ASSISTANT,
                            blocks=blocks,
                            order=1,
                        )
                    )

        return Conversation(
            title=page_title or "ChatGPT Conversation",
            source="ChatGPT",
            original_filename=original_filename,
            messages=messages,
            metadata={"extracted_turns": len(messages)},
        )
