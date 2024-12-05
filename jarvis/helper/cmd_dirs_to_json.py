from datetime import datetime

import re


def parse_dir_output(dir_output):
    files = []
    directories = []

    for line in dir_output.split("\n"):
        file_match = re.match(
            r"(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2})\s+(?:<DIR>|\s*(\d+(?:\.\d+)?)\s+)(.*?)$",
            line.strip(),
        )
        if file_match:
            date_str, size_str, name = file_match.groups()
            if size_str:  # File
                # Convert size to bytes (removing comma and converting to integer)
                size = int(
                    float(size_str.replace(",", "")) * 1000
                    if "." in size_str
                    else size_str
                )
                files.append(
                    {
                        "name": name.strip(),
                        "size": size,
                        "modified": datetime.strptime(
                            date_str, "%d/%m/%Y %H:%M"
                        ).isoformat(),
                    }
                )
            elif name not in [".", ".."]:  # Directory
                directories.append(name.strip())

    return {
        "files": files,
        "directories": directories,
        "totals": {
            "files": len(files),
            "directories": len(directories),
            "size": sum(f["size"] for f in files),
        },
    }
