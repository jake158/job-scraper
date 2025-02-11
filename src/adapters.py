import functools
import time
import openai
from pydantic import BaseModel


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


class JobFilterResponse(BaseModel):
    keep_job: bool


def retry(max_retries=2, delay=1):
    """
    A decorator that retries the wrapped function up to max_retries times.
    If all retries fail, it returns True (i.e. keep the job).
    """
    def decorator_retry(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    print(f"Retry {attempts} for {func.__name__} due to error: {e}")
                    time.sleep(delay)
            print("Retries exhausted. Defaulting to keeping the job.")
            return True
        return wrapper
    return decorator_retry


@retry(max_retries=2, delay=1)
def llm_should_keep_job(api_key: str, prompt: str, job_title: str, location: str, description: str) -> bool:
    """
    MODIFY THIS if you are using a different LLM.
    Returns True if the model indicates the job should be kept, False if it should be filtered out.
    """
    client = openai.OpenAI(api_key=api_key)

    job_info = (
        f"Job Title: {job_title}\n"
        f"Location: {location}\n"
        f"Description: {description}\n"
    )
    print("[LLM] filter decision for job:\n" + job_info)

    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[{"role": "system",
                       "content":
                       "You are a job filtering assistant."
                       + prompt +
                       "Return True if the job should be kept, False if it should be filtered out."},
                      {"role": "user", "content": job_info}],
            response_format=JobFilterResponse,)

        response = completion.choices[0].message.parsed
        print("[LLM] final decision: " + ("Keep job" if response.keep_job else "Filter out job"))
        return response.keep_job
    except Exception as e:
        raise e
