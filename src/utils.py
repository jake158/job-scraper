import os
import csv
import json
import pandas as pd


def load_config(file_path):
    """
    Load the configuration from a JSON file and process the search terms.
    """
    if not os.path.exists(file_path):
        raise Exception(f"{file_path} not found. You are probably calling main.py from outside of the project folder.")

    with open(file_path, "r") as f:
        config = json.load(f)

    config["search_job_boards"] = config.get("search_job_boards", False)
    config["search_google_jobs"] = config.get("search_google_jobs", False)

    board_entries = config.get("board_search_terms", [])
    config["board_search_terms"] = [
        (
            entry.get("search_term", ""),
            entry.get("location", ""),
            entry.get("country_indeed", "")
        )
        for entry in board_entries
    ]
    config["google_search_terms"] = config.get("google_search_terms", [])

    config["filter_locations"] = config.get("filter_locations", False)
    config["locations_to_filter"] = config.get("locations_to_filter", [])

    config["filter_job_titles"] = config.get("filter_job_titles", False)
    config["job_titles_to_filter"] = config.get("job_titles_to_filter", [])

    config["filter_companies"] = config.get("filter_companies", False)
    config["companies_to_filter"] = config.get("companies_to_filter", [])

    return config


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
    Proxy format: user:pass@host:port
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
