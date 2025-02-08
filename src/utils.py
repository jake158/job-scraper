import os
import csv
import json
import pandas as pd


def load_search_terms(file_path):
    """
    Load search terms from a JSON file.
    Expected JSON structure:
    {
      "board_search_terms": [
         {"search_term": "software engineer intern", "location": "San Francisco", "country_indeed": "USA"}
      ],
      "google_search_terms": [
         "software engineer intern jobs near San Francisco since yesterday"
      ]
    }
    """
    if not os.path.exists(file_path):
        print(f"{file_path} not found. Using empty search terms.")
        return [], []
    with open(file_path, "r") as f:
        config = json.load(f)
    board_terms = config.get("board_search_terms", [])
    google_terms = config.get("google_search_terms", [])
    return board_terms, google_terms


def load_seen_links(file_path):
    """
    Load seen links from the given CSV file.
    If the file doesn't exist, return an empty list.
    """
    if os.path.exists(file_path):
        seen_links = pd.read_csv(file_path)["job_url"].tolist()
        print(f"Loaded {len(seen_links)} seen links from {file_path}.")
        return seen_links
    print(f"{file_path} not found. Starting with an empty seen list.")
    return []


def load_proxies(file_path):
    """
    Load proxies from a text file, one per line.
    If the file doesn't exist or contains no proxies, return ["localhost"].
    """
    if not os.path.exists(file_path):
        print(f"{file_path} not found. Using 'localhost' as proxy.")
        return ["localhost"]
    with open(file_path, "r") as f:
        proxies = [line.strip() for line in f if line.strip()]
    if not proxies:
        print(f"No proxies found in {file_path}. Using 'localhost' as proxy.")
        return ["localhost"]
    print(f"Loaded {len(proxies)} proxies from {file_path}.")
    return proxies


def update_seen_links(seen_links, new_jobs):
    """
    Update the list of seen links with links from new jobs.
    """
    if not new_jobs.empty:
        new_links = new_jobs["job_url"].tolist()
        seen_links.extend(new_links)
    return list(set(seen_links))


def save_new_jobs(file_path, new_jobs):
    """
    Save the new jobs to a CSV file.
    """
    if new_jobs.empty:
        print("No new jobs to save.")
        return
    new_jobs.to_csv(file_path, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
    print(f"Saved {len(new_jobs)} new jobs to {file_path}.")


def save_seen_links(file_path, seen_links):
    """
    Save the seen links to the given CSV file.
    """
    seen_df = pd.DataFrame({"job_url": seen_links})
    seen_df.to_csv(file_path, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
    print(f"Saved {len(seen_links)} seen links to {file_path}.")
