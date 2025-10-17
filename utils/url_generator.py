import string
import random

BASE62_CHARS = string.digits + string.ascii_lowercase + string.ascii_uppercase

def generate_short_code(length=6):
    return ''.join(random.choice(BASE62_CHARS) for _ in range(length))

def encode_base62(num):
    if num == 0:
        return BASE62_CHARS[0]
    
    result = []
    while num > 0:
        result.append(BASE62_CHARS[num % 62])
        num //= 62
    return ''.join(reversed(result))