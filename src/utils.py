import os
import csv
import json
import pandas as pd


def load_config(file_path):
    """
    Load the configuration from a JSON file.
    """
    if not os.path.exists(file_path):
        raise Exception(f"{file_path} not found. You are probably calling main.py from outside of the project folder.")

    with open(file_path, "r") as f:
        config = json.load(f)

    config["search_job_boards"] = config.get("search_job_boards", False)
    config["search_google_jobs"] = config.get("search_google_jobs", False)

    config["board_search_terms"] = config.get("board_search_terms", [])
    config["google_search_terms"] = config.get("google_search_terms", [])

    # Filter options.
    config["filter_locations"] = config.get("filter_locations", False)
    config["locations_to_filter"] = config.get("locations_to_filter", [])
    config["filter_job_titles"] = config.get("filter_job_titles", False)
    config["job_titles_to_filter"] = config.get("job_titles_to_filter", [])
    config["filter_companies"] = config.get("filter_companies", False)
    config["companies_to_filter"] = config.get("companies_to_filter", [])

    return config


def load_seen_jobs(file_path):
    """
    Load seen jobs from a CSV file. Expected columns: title, company, location, job_url.
    If the file doesn't exist, return an empty DataFrame with those columns.
    """
    columns = ["title", "company", "location", "job_url"]

    if os.path.exists(file_path):
        try:
            seen_jobs = pd.read_csv(file_path)
            print(f"Loaded {len(seen_jobs)} seen jobs from {file_path}.")
            return seen_jobs
        except Exception as e:
            print(f"Error loading seen jobs: {e}")
            return pd.DataFrame(columns=columns)

    print(f"{file_path} not found. Starting with an empty seen jobs DataFrame.")
    return pd.DataFrame(columns=columns)


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


def save_jobs(file_path, jobs):
    """
    Save the jobs to a CSV file.
    """
    if jobs.empty:
        print("No jobs to save.")
        return
    jobs.to_csv(file_path, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
    print(f"Saved {len(jobs)} new jobs to {file_path}.")
