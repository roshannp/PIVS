import re

DANGEROUS_PATTERNS = [
    r"ignore\s+.*instructions",
    r"pretend\s+.*you(\'|’)?re",
    r"system\s+prompt",
    r"/etc/passwd",
    r"you are DAN",
    r"simulate.*(linux|terminal|bash|cmd)",
    r"respond to .*as if.*(shell|command|terminal)",
    r"whoami",
    r"cat\s+/etc/passwd"
]


def is_prompt_safe(prompt):
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, prompt, re.IGNORECASE):
            return False, pattern
    return True, None
