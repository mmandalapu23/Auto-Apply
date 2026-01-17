"""Text utilities."""
import re


def extract_emails(text: str) -> list:
    """Extract email addresses from text."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)


def extract_urls(text: str) -> list:
    """Extract URLs from text."""
    url_pattern = r'https?://[^\s]+'
    return re.findall(url_pattern, text)


def clean_text(text: str) -> str:
    """Clean text: strip whitespace, normalize newlines."""
    return '\n'.join(line.strip() for line in text.split('\n') if line.strip())


def highlight_keywords(text: str, keywords: list) -> str:
    """Highlight keywords in text."""
    result = text
    for keyword in keywords:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        result = pattern.sub(f"**{keyword}**", result)
    return result
