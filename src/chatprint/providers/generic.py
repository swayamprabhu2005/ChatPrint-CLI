"""Generic fallback conversation provider for unknown AI chat pages."""

import copy
from typing import Any

from bs4 import BeautifulSoup, Tag

from chatprint.extraction.cleaner import clean_dom
from chatprint.extraction.heuristics import score_conversation_container
from chatprint.extraction.normalizer import (
    element_to_content_blocks,
)
from chatprint.models import (
    Conversation,
    Message,
    Role,
)
from chatprint.providers.base import ConversationProvider


class GenericProvider(ConversationProvider):
    """Generic heuristic provider for unknown AI conversation webpages."""

    name = "generic"
    display_name = "Generic AI Conversation"

    def detect_confidence(
        self,
        soup: BeautifulSoup,
        raw_html: str,
        metadata: dict[str, Any],
    ) -> float:
        # Default low baseline confidence so it acts as fallback
        return 0.2

    def extract(
        self,
        soup: BeautifulSoup,
        resources: dict[str, bytes],
        original_filename: str,
    ) -> Conversation:
        working_soup = copy.copy(soup)

        title = ""
        if working_soup.title and working_soup.title.string:
            title = working_soup.title.string.strip()

        clean_dom(working_soup)

        # Find best candidate container
        candidates: list[tuple[float, Tag]] = []
        for tag in working_soup.find_all(["main", "article", "div", "section"]):
            score = score_conversation_container(tag)
            if score > 0:
                candidates.append((score, tag))

        candidates.sort(key=lambda x: x[0], reverse=True)

        messages: list[Message] = []
        turn_order = 1

        if candidates:
            best_container = candidates[0][1]
            # Try to see if direct children look like alternating turns
            direct_divs = [c for c in best_container.children if isinstance(c, Tag)]
            if len(direct_divs) >= 2:
                for div in direct_divs:
                    blocks = element_to_content_blocks(div)
                    if blocks:
                        role = Role.USER if turn_order % 2 == 1 else Role.ASSISTANT
                        messages.append(Message(role=role, blocks=blocks, order=turn_order))
                        turn_order += 1
            else:
                blocks = element_to_content_blocks(best_container)
                if blocks:
                    messages.append(Message(role=Role.ASSISTANT, blocks=blocks, order=1))

        if not messages:
            body = working_soup.body or working_soup
            blocks = element_to_content_blocks(body)
            if blocks:
                messages.append(Message(role=Role.ASSISTANT, blocks=blocks, order=1))

        return Conversation(
            title=title or "AI Conversation",
            source="Generic AI Webpage",
            original_filename=original_filename,
            messages=messages,
            metadata={"extracted_turns": len(messages)},
        )
