"""URL code generation utilities using Base62 encoding."""
import string
import random

BASE62_CHARS = string.digits + string.ascii_lowercase + string.ascii_uppercase

def generate_short_code(length=6):
    """Generate a random short code using Base62 characters.
    
    Args:
        length: Length of the generated code (default: 6)
        
    Returns:
        Random string of specified length using Base62 characters
    """
    return ''.join(random.choice(BASE62_CHARS) for _ in range(length))

def encode_base62(num):
    """Encode a number to Base62 string.
    
    Args:
        num: Integer to encode
        
    Returns:
        Base62 encoded string representation of the number
    """
    if num == 0:
        return BASE62_CHARS[0]
    
    result = []
    while num > 0:
        result.append(BASE62_CHARS[num % 62])
        num //= 62
    return ''.join(reversed(result))