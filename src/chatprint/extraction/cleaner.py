"""DOM cleaning engine for stripping unwanted webpage UI and non-content elements."""

from bs4 import BeautifulSoup

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
    # Remove standard non-content tags
    for tag_name in _TAGS_TO_REMOVE:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    # Remove extra unwanted selectors if provided
    if extra_unwanted_selectors:
        for selector in extra_unwanted_selectors:
            try:
                for match in soup.select(selector):
                    match.decompose()
            except Exception:
                # Ignore invalid CSS selector syntax gracefully
                continue

    # Remove elements explicitly styled with display: none or hidden attribute
    for hidden in soup.find_all(attrs={"hidden": True}):
        hidden.decompose()

    for el in soup.find_all(True):
        style = el.get("style", "")
        if "display: none" in style or "display:none" in style:
            el.decompose()

    return soup
