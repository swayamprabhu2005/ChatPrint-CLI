"""Google Gemini and Google Search AI Mode conversation provider."""

import copy
import re
from typing import Any

from bs4 import BeautifulSoup

from ai_conversation.extraction.cleaner import clean_dom
from ai_conversation.extraction.normalizer import (
    element_to_content_blocks,
    normalize_text,
)
from ai_conversation.models import (
    Conversation,
    Message,
    ParagraphBlock,
    Role,
)
from ai_conversation.providers.base import ConversationProvider

_GEMINI_UNWANTED_SELECTORS = [
    # Google Search UI
    "#searchform",
    "#tsf",
    "#header",
    "#top_nav",
    "#hdtb",
    "#appbar",
    "header",
    "nav",
    # Accounts & Profiles
    "div[aria-label*='Google Account']",
    "a[aria-label*='Google Account']",
    "div[aria-label*='Account Information']",
    "div[class*='gb_']",
    # Right-hand side & Sidebars & Ads
    "#rhs",
    "#rhs_block",
    ".rhsvw",
    "div[class*='commercial-unit']",
    "div[aria-label*='Ads']",
    "div[data-attrid*='Shopping']",
    # People Also Ask / Search widgets unrelated to conversation
    "div[data-attrid*='wa:/paa']",
    "div[data-initq]",
    "#extrares",
    "#bottomads",
    # Footers
    "#footcnt",
    "#fbar",
    "footer",
    # Buttons & Controls
    "button",
    "div[role='button']",
    "div[aria-label*='Feedback']",
    "div[aria-label*='Share']",
    "div[aria-label*='Copy']",
]


class GeminiProvider(ConversationProvider):
    """Provider for Google Gemini and Google Search AI Mode pages."""

    name = "gemini"
    display_name = "Google Gemini AI Mode"

    def detect_confidence(
        self,
        soup: BeautifulSoup,
        raw_html: str,
        metadata: dict[str, Any],
    ) -> float:
        score = 0.0
        snapshot_loc = metadata.get("snapshot_location", "").lower()
        title = (soup.title.string.strip() if soup.title and soup.title.string else "").lower()

        # URL / Location signals
        if "gemini.google.com" in snapshot_loc:
            score += 0.7
        elif "google.com/search" in snapshot_loc or "google.com" in snapshot_loc:
            score += 0.3

        # Title signals
        if "gemini" in title:
            score += 0.5
        elif "google search" in title:
            score += 0.2

        # Structural & Textual signals
        raw_lower = raw_html.lower()
        if "ai overview" in raw_lower:
            score += 0.4
        if "gemini" in raw_lower:
            score += 0.3
        if "data-attrid" in raw_lower:
            score += 0.2
        if "data-message-author-role=\"model\"" in raw_lower or "model-response" in raw_lower:
            score += 0.6
        if soup.find("div", attrs={"data-attrid": re.compile(r"(wa:/description|Overview)", re.IGNORECASE)}):
            score += 0.5
        if soup.find(attrs={"aria-label": re.compile(r"AI Overview", re.IGNORECASE)}):
            score += 0.5

        return min(1.0, score)

    def extract(
        self,
        soup: BeautifulSoup,
        resources: dict[str, bytes],
        original_filename: str,
    ) -> Conversation:
        # Create a deep copy of soup so original is unmodified
        working_soup = copy.copy(soup)

        # Extract title or initial query from search input or title tag
        page_title = ""
        if working_soup.title and working_soup.title.string:
            page_title = working_soup.title.string.strip()
            # Clean " - Google Search" suffix if present
            page_title = re.sub(r"\s*-\s*Google Search$", "", page_title, flags=re.IGNORECASE).strip()

        # Try to find user search input
        search_query = ""
        search_input = working_soup.find("textarea", attrs={"name": "q"}) or working_soup.find("input", attrs={"name": "q"})
        if search_input:
            search_query = search_input.get("value") or search_input.get_text() or ""
            search_query = search_query.strip()

        if not page_title and search_query:
            page_title = search_query

        # Clean DOM of unwanted UI components
        clean_dom(working_soup, _GEMINI_UNWANTED_SELECTORS)

        messages: list[Message] = []
        turn_order = 1

        # PATTERN 1: Multi-turn chat (gemini.google.com or Google AI Mode multi-turn)
        # Look for explicit turn elements
        turn_elements = working_soup.select(
            "[data-message-author-role], .conversation-turn, .chat-turn, user-query, model-response, [data-turn-id]"
        )

        if turn_elements:
            for turn in turn_elements:
                role_attr = (turn.get("data-message-author-role") or "").lower()
                tag_name = turn.name.lower()
                classes = " ".join(turn.get("class") or []).lower()

                if "user" in role_attr or "user" in classes or tag_name == "user-query":
                    role = Role.USER
                elif "model" in role_attr or "assistant" in role_attr or "model" in classes or tag_name == "model-response":
                    role = Role.ASSISTANT
                else:
                    role = Role.ASSISTANT

                blocks = element_to_content_blocks(turn)
                if blocks:
                    messages.append(Message(role=role, blocks=blocks, order=turn_order))
                    turn_order += 1

        # PATTERN 2: Google Search AI Overview / AI Mode container
        if not messages:
            # Look for AI Overview response container
            ai_overview = (
                working_soup.find("div", attrs={"data-attrid": re.compile(r"(wa:/description|Overview)", re.IGNORECASE)})
                or working_soup.find(attrs={"aria-label": re.compile(r"AI Overview", re.IGNORECASE)})
                or working_soup.find("div", attrs={"data-snc": True})
                or working_soup.find("div", class_=re.compile(r"(ai-overview|gemini-response)", re.IGNORECASE))
            )

            # If user query is known, create User message first
            user_text = search_query or page_title
            if user_text:
                messages.append(
                    Message(
                        role=Role.USER,
                        blocks=[ParagraphBlock(text=normalize_text(user_text))],
                        order=1,
                    )
                )
                turn_order = 2

            if ai_overview:
                # Remove nested feedback/action links from AI overview
                for unwanted in ai_overview.select("button, div[role='button'], [data-attribution]"):
                    unwanted.decompose()
                blocks = element_to_content_blocks(ai_overview)
                if blocks:
                    messages.append(
                        Message(
                            role=Role.ASSISTANT,
                            blocks=blocks,
                            order=turn_order,
                        )
                    )

        # PATTERN 3: Heuristic fallback for any remaining main text container
        if not messages:
            main_container = working_soup.find("main") or working_soup.find("div", id="center_col") or working_soup.body
            if main_container:
                blocks = element_to_content_blocks(main_container)
                if blocks:
                    # If we had a title, user prompt was title
                    if page_title:
                        messages.append(
                            Message(
                                role=Role.USER,
                                blocks=[ParagraphBlock(text=normalize_text(page_title))],
                                order=1,
                            )
                        )
                        messages.append(
                            Message(
                                role=Role.ASSISTANT,
                                blocks=blocks,
                                order=2,
                            )
                        )
                    else:
                        messages.append(
                            Message(
                                role=Role.ASSISTANT,
                                blocks=blocks,
                                order=1,
                            )
                        )

        return Conversation(
            title=page_title or "Gemini Conversation",
            source="Google Gemini AI Mode",
            original_filename=original_filename,
            messages=messages,
            metadata={"extracted_turns": len(messages)},
        )
