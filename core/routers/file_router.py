import re


# =========================================================
# Exact Commands
# =========================================================

FILES = {

    "create folder": {
        "action": "create_folder"
    },

    "create file": {
        "action": "create_file"
    },

    "zip folder": {
        "action": "zip"
    },

    "extract zip": {
        "action": "extract"
    },

    "recent files": {
        "action": "recent_files"
    },

    "file information": {
        "action": "file_info"
    },

}


# =========================================================
# File Router
# =========================================================

def file_route(command):

    command = command.lower().strip()

    if not command:
        return None

    # =====================================================
    # Existing Exact Commands
    # =====================================================

    if command in FILES:

        return [
            FILES[command]
        ]

    # =====================================================
    # Open File
    # =====================================================

    match = re.fullmatch(
        r"(?:open|launch)\s+(?:the\s+)?file\s+(.+)",
        command,
        re.IGNORECASE
    )

    if match:

        path = match.group(1).strip()

        if path:

            return [{
                "action": "open_file",
                "path": path
            }]

    # =====================================================
    # Open Folder
    # =====================================================

    match = re.fullmatch(
        r"(?:open|launch)\s+(?:the\s+)?folder\s+(.+)",
        command,
        re.IGNORECASE
    )

    if match:

        path = match.group(1).strip()

        if path:

            return [{
                "action": "open_folder",
                "path": path
            }]

    # =====================================================
    # Create Folder
    # =====================================================

    match = re.fullmatch(
        r"(?:create|make|new)\s+(?:a\s+)?folder(?:\s+called)?\s+(.+)",
        command,
        re.IGNORECASE
    )

    if match:

        path = match.group(1).strip()

        if path:

            return [{
                "action": "create_folder",
                "path": path
            }]

    # =====================================================
    # Create File
    # =====================================================

    match = re.fullmatch(
        r"(?:create|make|new)\s+(?:a\s+)?file(?:\s+called)?\s+(.+)",
        command,
        re.IGNORECASE
    )

    if match:

        path = match.group(1).strip()

        if path:

            return [{
                "action": "create_file",
                "path": path
            }]

    # =====================================================
    # Copy
    # =====================================================

    match = re.fullmatch(
        r"copy\s+(.+?)\s+(?:to|into)\s+(.+)",
        command,
        re.IGNORECASE
    )

    if match:

        source = match.group(1).strip()
        destination = match.group(2).strip()

        if source and destination:

            return [{
                "action": "copy",
                "source": source,
                "destination": destination
            }]

    # =====================================================
    # Move
    # =====================================================

    match = re.fullmatch(
        r"move\s+(.+?)\s+(?:to|into)\s+(.+)",
        command,
        re.IGNORECASE
    )

    if match:

        source = match.group(1).strip()
        destination = match.group(2).strip()

        if source and destination:

            return [{
                "action": "move",
                "source": source,
                "destination": destination
            }]

    # =====================================================
    # Rename
    # =====================================================

    match = re.fullmatch(
        r"rename\s+(.+?)\s+(?:to|as)\s+(.+)",
        command,
        re.IGNORECASE
    )

    if match:

        old = match.group(1).strip()
        new = match.group(2).strip()

        if old and new:

            return [{
                "action": "rename",
                "old": old,
                "new": new
            }]

    # =====================================================
    # Delete / Remove
    # =====================================================

    match = re.fullmatch(
        r"(?:delete|remove|trash)\s+(?:the\s+)?(.+)",
        command,
        re.IGNORECASE
    )

    if match:

        path = match.group(1).strip()

        if path:

            return [{
                "action": "delete",
                "path": path
            }]

    # =====================================================
    # File Information
    # =====================================================

    match = re.fullmatch(
        r"(?:file\s+)?(?:info|information|details)\s+(?:for\s+)?(.+)",
        command,
        re.IGNORECASE
    )

    if match:

        path = match.group(1).strip()

        if path:

            return [{
                "action": "file_info",
                "path": path
            }]

    # =====================================================
    # Recent Files
    # =====================================================

    if command in [
        "recent files",
        "show recent files",
        "show my recent files",
        "list recent files",
        "what are my recent files",
    ]:

        return [{
            "action": "recent_files"
        }]

    # =====================================================
    # Recycle
    # =====================================================

    match = re.fullmatch(
        r"(?:recycle|move to recycle bin|send to recycle bin)\s+(.+)",
        command,
        re.IGNORECASE
    )

    if match:

        path = match.group(1).strip()

        if path:

            return [{
                "action": "recycle",
                "path": path
            }]

    # =====================================================
    # ZIP
    # =====================================================

    match = re.fullmatch(
        r"(?:zip|compress)\s+(?:folder\s+)?(.+?)(?:\s+as\s+(.+))?",
        command,
        re.IGNORECASE
    )

    if match:

        folder = match.group(1).strip()
        output = match.group(2)

        if folder:

            if output:

                output = output.strip()

            else:

                output = folder.rstrip(
                    "\\/"
                )

            return [{
                "action": "zip",
                "folder": folder,
                "output": output
            }]

    # =====================================================
    # Extract ZIP
    # =====================================================

    match = re.fullmatch(
        r"(?:extract|unzip)\s+(.+?)(?:\s+to\s+(.+))?",
        command,
        re.IGNORECASE
    )

    if match:

        archive = match.group(1).strip()
        destination = match.group(2)

        if archive:

            if destination:

                destination = destination.strip()

            else:

                destination = "."

            return [{
                "action": "extract",
                "zip": archive,
                "destination": destination
            }]
            
    # =========================================================
    # Search / Find File
    # =========================================================

    match = re.fullmatch(
        r"(?:find|search\s+for|look\s+for)\s+(?:my\s+)?(.+)",
        command,
        re.IGNORECASE
    )

    if match:

        query = match.group(1).strip()

        if query:

            return [{
                "action": "search_file",
                "query": query
            }]        

    return None