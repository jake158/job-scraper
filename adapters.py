
def _transform_proxy_line(line: str) -> str:
    """
    MODIFY THIS if your proxies are in a different format.
    Transforms a proxy line from various formats to the format expected by the job scraper: 'user:pass@host:port'.

    Expected input formats:
      - "host:port:user:pass"  (will be transformed to "user:pass@host:port")
      - "user:pass@host:port"  (assumed to be already in the correct format)

    If the line does not match known formats, this function returns None.
    """
    line = line.strip()
    if not line:
        return None

    if "@" in line:
        return line

    parts = line.split(":")
    if len(parts) == 4:
        host, port, user, password = parts
        return f"{user}:{password}@{host}:{port}"

    print(f"Invalid proxy format: {line}")
    return None


def load_proxies(file_path: str) -> list:
    """
    Load proxies from a text file, one per line, transforming each line to the format:
      'user:pass@host:port'

    If the file does not exist or no valid proxies are found, return ["localhost"].
    """
    import os
    if not os.path.exists(file_path):
        print(f"{file_path} not found. Using 'localhost' as proxy.")
        return ["localhost"]

    proxies = []
    with open(file_path, "r") as f:
        for line in f:
            transformed = _transform_proxy_line(line)
            if transformed:
                proxies.append(transformed)
    if not proxies:
        print(f"No valid proxies found in {file_path}. Using 'localhost' as proxy.")
        return ["localhost"]

    print(f"Loaded {len(proxies)} proxies from {file_path}.")
    return proxies


def llm_should_keep_job(job_title: str, location: str, description: str) -> bool:
    """
    Fixed-signature function to filter with an LLM.
    """
    # TODO: Implement
    return None
