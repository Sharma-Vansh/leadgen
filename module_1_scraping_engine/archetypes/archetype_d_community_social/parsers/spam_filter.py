"""
Archetype D, Tier 1: Spam Gatekeeper Filter
Drops casual chats, memes, crypto spam, and non-hiring messages.
Keeps only messages containing verified hiring/recruitment intent.
"""
import re
from typing import Tuple

HIRING_KEYWORDS = [
    r"\bhiring\b",
    r"\bwe are hiring\b",
    r"\bjob\b",
    r"\bopening\b",
    r"\binternship\b",
    r"\bintern\b",
    r"\bapply\b",
    r"\brecruitment\b",
    r"\boff-campus\b",
    r"\boffcampus\b",
    r"\bdrive\b",
    r"\bvacancy\b",
    r"\brole\b",
    r"\bsde\b",
    r"\bdeveloper\b",
    r"\banalyst\b"
]

SPAM_KEYWORDS = [
    r"\bcrypto\b",
    r"\bbitcoin\b",
    r"\bairdrop\b",
    r"\bforex\b",
    r"\bcasino\b",
    r"\bbetting\b",
    r"\blottery\b",
    r"\bearn ₹\d+ from home daily by liking\b",
    r"\btask scam\b",
    r"\bfree recharge\b"
]


class SpamFilter:
    def __init__(self):
        self.hiring_pattern = re.compile("|".join(HIRING_KEYWORDS), re.IGNORECASE)
        self.spam_pattern = re.compile("|".join(SPAM_KEYWORDS), re.IGNORECASE)

    def is_valid_hiring_post(self, text: str) -> Tuple[bool, str]:
        """
        Evaluates post text.
        Returns: (is_valid, reason)
        """
        if not text or len(text.strip()) < 20:
            return False, "Text too short (<20 chars)"

        # Check for obvious scam/spam keywords
        if self.spam_pattern.search(text):
            return False, "Flagged by scam/spam keyword pattern"

        # Check for positive hiring keywords
        if not self.hiring_pattern.search(text):
            return False, "No hiring/job intent keywords detected"

        return True, "Valid hiring post"
