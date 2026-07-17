import os
import re

def JIT(path) -> list:
    """Reads file and returns raw unparsed line elements."""
    with open(path, "r", encoding="utf-8") as file:
        return file.read().split("\n")

def parser(path) -> list:
    """Scans headers and tokenizes bold-italic, bold, italic, and generic formatted segments."""
    raw_lines = JIT(path)
    compiled_document = []

    for line in raw_lines:
        base_size = "normal"
        clean_text = line

        # Classify header categories from deepest down to shallowest
        if line.startswith(">>>>>> "):   base_size, clean_text = "tet", line[7:]
        elif line.startswith(">>>>> "):  base_size, clean_text = "ser", line[6:]
        elif line.startswith(">>>> "):   base_size, clean_text = "sma", line[5:]
        elif line.startswith(">>> "):    base_size, clean_text = "med", line[4:]
        elif line.startswith(">> "):     base_size, clean_text = "bg", line[3:]
        elif line.startswith("> "):      base_size, clean_text = "hge", line[2:]

        # Unified single-pass regex: matches |<:bi:>| OR |<bold>| OR |:italics:| OR generic |formatted| spans
        # Ordered from longest pattern string rule down to shortest pattern string rule to prevent truncation
        combined_regex = r'(\|\<:[^|]+:\>\||\|\<[^|]+\>\||\|:[^|]+:\||\|[^|]+\|)'
        segments = re.split(combined_regex, clean_text)
        line_tokens = []

        for segment in segments:
            if not segment:
                continue

            style_type = base_size
            clean_text_segment = segment

            # 1. Match Bold-Italic Token Layer: |<:text:>|
            if segment.startswith("|<:") and segment.endswith(":>|"):
                style_type, clean_text_segment = f"{base_size}_bi", segment[3:-3]

            # 2. Match Bold Token Layer: |<text>|
            elif segment.startswith("|<") and segment.endswith(">|"):
                style_type, clean_text_segment = f"{base_size}_bold", segment[2:-2]

            # 3. Match Italic Token Layer: |:text:|
            elif segment.startswith("|:") and segment.endswith(":|"):
                style_type, clean_text_segment = f"{base_size}_italic", segment[2:-2]

            # 4. Match Generic Formatted Container Layer: |text|
            elif segment.startswith("|") and segment.endswith("|"):
                style_type, clean_text_segment = f"{base_size}_formatted", segment[1:-1]

            # UNIFIED COLOR PROCESSOR: Inspects extracted text for your precise hex format rule
            if style_type != base_size:
                color_match = re.match(r'^\*hexc\(H\!\s*([0-9A-Fa-f]{6})\)\*\s*(.*)', clean_text_segment)
                if color_match:
                    hex_color = color_match.group(1)
                    actual_content = color_match.group(2)
                    
                    style_type = f"{style_type}_color_{hex_color}"
                    clean_text_segment = actual_content

            line_tokens.append((clean_text_segment, style_type))

        compiled_document.append(line_tokens)
        
    return compiled_document
