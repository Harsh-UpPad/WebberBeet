import os
import re
import tkinter as tk
from tkinter import ttk, font

# =====================================================================
# 1. PARSING ENGINE SUBSYSTEM
# =====================================================================

# Globally compile regex patterns for speed and memory optimization
HEADER_PATTERN = re.compile(r"^(>{1,6})\s+(.*)$")
HEX_PATTERN = re.compile(r"^\*hexc\(H\!\s*([0-9A-Fa-f]{6})\)\*\s*(.*)")
SIZE_PATTERN = re.compile(r"^\*size\(I\!\s*([0-9]{2})\)\*\s*(.*)")
TOKEN_PATTERN = re.compile(r"(\|\<:[^|]+:\>\||\|\<[^|]+\>\||\|:[^|]+:\||\|[^|]+\||A\|[^|]+\|A)")

DEFAULT_BASE_SIZE = 12

# Map number of arrows to their respective typographic base sizes
HEADER_SIZE_MAP = {
    1: "hge", 
    2: "bg", 
    3: "med", 
    4: "sma", 
    5: "ser", 
    6: "tet", 
    7: DEFAULT_BASE_SIZE
}

def JIT(path: str) -> list[str]:
    """Reads file and returns raw unparsed line elements."""
    with open(path, "r", encoding="utf-8") as file:
        return file.read().splitlines()

def parse_line_styles(segment: str, base_size: str) -> tuple[str, str]:
    """Parses text segments for explicit typographic wrapper tags or structural size overrides."""
    
    # 1. Catch absolute inline size overrides first using the walrus operator
    if size_match := SIZE_PATTERN.match(segment):
        extracted_size, actual_content = size_match.groups()
        base_size = f"size_{extracted_size}"
        segment = actual_content

    # 2. Map markdown prefixes to their corresponding style suffixes with the proper size context
    tags = { 
        "|<:": f"{base_size}_bi", 
        "|<": f"{base_size}_bold", 
        "|:": f"{base_size}_italic", 
        "|": f"{base_size}_formatted" 
    }

    # 3. Check for matching structural tag bounds
    for prefix, suffix in tags.items():
        if segment.startswith(prefix):
            strip_len = len(prefix)
            return segment[strip_len:-strip_len], suffix
            
    return segment, base_size  # Return as plain text if no styling wrappers match

def engine_parser(path: str) -> list[list[tuple[str, str]]]:
    """Scans headers and tokenizes bold-italic, bold, italic, and generic formatted segments."""
    compiled_document = []

    for line in JIT(path):
        base_size, clean_text = "normal", line

        # Extract structural document headers using regex match groups
        if header_match := HEADER_PATTERN.match(line):
            arrows, clean_text = header_match.groups()
            base_size = HEADER_SIZE_MAP.get(len(arrows), "normal")

        line_tokens = []
        for segment in filter(None, TOKEN_PATTERN.split(clean_text)):
            content, style = parse_line_styles(segment, base_size)

            # Apply inline hexadecimal color overrides if present
            if style != base_size and (color_match := HEX_PATTERN.match(content)):
                hex_color, actual_content = color_match.groups()
                style = f"color_{hex_color}" if style == "color_00FFF0" else f"{style}_color_{hex_color}"
                content = actual_content

            line_tokens.append((content, style))

        compiled_document.append(line_tokens)
        
    return compiled_document
