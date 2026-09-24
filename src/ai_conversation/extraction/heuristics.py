"""Heuristics for scoring conversation containers and detecting dialogue structure."""

import re

from bs4 import Tag

_POSITIVE_ATTR_PATTERNS = re.compile(
    r"(conversation|chat|turn|message|dialogue|response|bubble|prose|query|prompt)",
    re.IGNORECASE,
)

_NEGATIVE_ATTR_PATTERNS = re.compile(
    r"(nav|header|footer|sidebar|advert|ad-|banner|menu|modal|cookie|searchbox|toolbar)",
    re.IGNORECASE,
)


def score_conversation_container(tag: Tag) -> float:
    """Calculate a relevance score for a DOM container candidate being a conversation.

    Args:
        tag: BeautifulSoup Tag to evaluate.

    Returns:
        Float score (higher is more likely to be a conversation container).
    """
    text = tag.get_text().strip()
    if len(text) < 20:
        return 0.0

    score = 1.0

    # Attribute inspection (class, id, role, data attributes)
    attr_string = " ".join(
        f"{k}={v}" for k, v in tag.attrs.items() if isinstance(v, (str, list))
    )

    if _POSITIVE_ATTR_PATTERNS.search(attr_string):
        score += 3.0

    if _NEGATIVE_ATTR_PATTERNS.search(attr_string):
        score -= 4.0

    # Child element richness: paragraphs, lists, code, headings
    p_count = len(tag.find_all("p"))
    li_count = len(tag.find_all("li"))
    pre_count = len(tag.find_all("pre"))
    heading_count = len(tag.find_all(["h1", "h2", "h3", "h4"]))

    content_element_score = min(p_count * 0.5 + li_count * 0.3 + pre_count * 1.0 + heading_count * 0.5, 10.0)
    score += content_element_score

    # Repeated child items (turns)
    direct_children = [c for c in tag.children if isinstance(c, Tag)]
    if len(direct_children) >= 2:
        score += 2.0

    # Length of content
    text_length = len(text)
    if text_length > 200:
        score += 2.0
    if text_length > 1000:
        score += 2.0

    return max(0.0, score)
