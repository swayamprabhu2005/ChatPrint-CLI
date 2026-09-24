"""DOM cleaning engine for stripping unwanted webpage UI and non-content elements."""

from bs4 import BeautifulSoup, Comment

_TAGS_TO_REMOVE = [
    "script",
    "noscript",
    "style",
    "iframe",
    "object",
    "embed",
    "applet",
    "form",
    "svg",
    "button",
]


def clean_dom(soup: BeautifulSoup, extra_unwanted_selectors: list[str] | None = None) -> BeautifulSoup:
    """Strip scripts, stylesheets, tracking elements, buttons, and unwanted UI.

    Args:
        soup: BeautifulSoup parsed DOM.
        extra_unwanted_selectors: Optional provider-specific CSS selectors to decompose.

    Returns:
        Cleaned BeautifulSoup instance.
    """
    # Remove all HTML comments (which often store hydration JSON payloads and internal tokens)
    for comment in list(soup.find_all(string=lambda text: isinstance(text, Comment))):
        comment.extract()

    # Remove standard non-content tags
    for tag_name in _TAGS_TO_REMOVE:
        for tag in list(soup.find_all(tag_name)):
            if not getattr(tag, "decomposed", False):
                tag.decompose()

    # Remove extra unwanted selectors if provided
    if extra_unwanted_selectors:
        for selector in extra_unwanted_selectors:
            try:
                for match in list(soup.select(selector)):
                    if not getattr(match, "decomposed", False):
                        match.decompose()
            except Exception:
                # Ignore invalid CSS selector syntax gracefully
                continue

    # Remove elements explicitly styled with display: none or hidden attribute
    for hidden in list(soup.find_all(attrs={"hidden": True})):
        if not getattr(hidden, "decomposed", False):
            hidden.decompose()

    for el in list(soup.find_all(True)):
        if getattr(el, "decomposed", False):
            continue
        attrs = getattr(el, "attrs", None)
        if not attrs or not isinstance(attrs, dict):
            continue
        style = attrs.get("style", "")
        if isinstance(style, str) and (
            "display: none" in style.lower()
            or "display:none" in style.lower()
            or "visibility: hidden" in style.lower()
            or "visibility:hidden" in style.lower()
        ):
            el.decompose()

    return soup
