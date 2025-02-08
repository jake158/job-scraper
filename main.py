import os
import csv
import json
import pandas as pd
from jobspy import scrape_jobs

SEEN_FILE = "seen.csv"
NEW_JOBS_FILE = "new_jobs.csv"
SEARCH_TERMS_FILE = "search_terms.json"


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


def scrape_job_board_jobs(search_term, location, country_indeed, seen_links):
    try:
        jobs = scrape_jobs(
            site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor"],
            search_term=search_term,
            location=location,
            results_wanted=20,
            hours_old=72,
            distance=200,
            country_indeed=country_indeed,
        )
        print(f"[JOB BOARDS] Scraped {len(jobs)} jobs.")
    except Exception as e:
        print(f"Error scraping job boards for '{search_term}' in '{location}': {e}")
        return pd.DataFrame()

    if "job_url" not in jobs.columns:
        print("Error: 'job_url' column is missing from the scraped jobs DataFrame.")
        return pd.DataFrame()

    new_jobs = jobs[~jobs["job_url"].isin(seen_links)]
    print(f"Filtered {len(new_jobs)} new jobs after checking seen links.")
    return new_jobs


def scrape_google_jobs(search_term, seen_links):
    try:
        jobs = scrape_jobs(
            site_name="google",
            google_search_term=search_term,
            results_wanted=2,
        )
        print(f"[GOOGLE] Scraped {len(jobs)} jobs.")
    except Exception as e:
        print(f"Error scraping Google jobs for '{search_term}': {e}")
        return pd.DataFrame()

    if "job_url" not in jobs.columns:
        print("Error: 'job_url' column is missing from the scraped jobs DataFrame.")
        return pd.DataFrame()

    new_jobs = jobs[~jobs["job_url"].isin(seen_links)]
    print(f"Filtered {len(new_jobs)} new jobs after checking seen links.")
    return new_jobs


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


if __name__ == "__main__":
    board_terms, google_terms = load_search_terms(SEARCH_TERMS_FILE)

    BOARD_SEARCH_TERMS = [
        (entry.get("search_term", ""), entry.get("location", ""), entry.get("country_indeed", ""))
        for entry in board_terms
    ]
    GOOGLE_SEARCH_TERMS = google_terms

    seen_links = load_seen_links(SEEN_FILE)
    new_jobs = pd.DataFrame()

    for (search_term, location, country_indeed) in BOARD_SEARCH_TERMS:
        new_board_jobs = scrape_job_board_jobs(search_term, location, country_indeed, seen_links)
        if not new_board_jobs.empty:
            new_jobs = pd.concat([new_jobs, new_board_jobs], ignore_index=True)
        seen_links = update_seen_links(seen_links, new_board_jobs)

    for search_term in GOOGLE_SEARCH_TERMS:
        new_google_jobs = scrape_google_jobs(search_term, seen_links)
        if not new_google_jobs.empty:
            new_jobs = pd.concat([new_jobs, new_google_jobs], ignore_index=True)
        seen_links = update_seen_links(seen_links, new_google_jobs)

    new_jobs = new_jobs.drop_duplicates(subset="job_url")
    new_jobs = new_jobs.drop_duplicates(subset=["title", "company", "location"])

    save_new_jobs(NEW_JOBS_FILE, new_jobs)
    save_seen_links(SEEN_FILE, seen_links)
