import re


def sanitize_postgresql_identifier(input_string: str):
    # Remove leading and trailing whitespace
    sanitized = input_string.strip()

    # Replace spaces and other disallowed characters with underscores
    sanitized = re.sub(r"\W", "_", sanitized)

    # Ensure the name starts with a letter or underscore
    if not re.match(r"^[a-zA-Z_]", sanitized):
        sanitized = "_" + sanitized

    # Truncate to 63 characters to meet Postgres limitations
    sanitized = sanitized[:63]

    return sanitized
