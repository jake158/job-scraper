import pandas as pd
from scraper import JobScraper
from src.utils import (
    load_config,
    load_seen_jobs,
    load_proxies,
    save_jobs,
)

SEEN_FILE = "seen.csv"
NEW_JOBS_FILE = "new_jobs.csv"
CONFIG_FILE = "config.json"
PROXIES_FILE = "proxies.txt"


def get_job_identity(job):
    """
    Given a job record (a Series), return a tuple that represents its identity:
    (title, company, location)
    """
    title = str(job.get("title", "")).strip().lower()
    company = str(job.get("company", "")).strip().lower()
    location = str(job.get("location", "")).strip().lower()
    return (title, company, location)


def filter_seen(scraped_jobs, seen_jobs):
    """
    Given the scraped jobs DataFrame and the seen jobs DataFrame,
    return a tuple (filtered_jobs_df, updated_seen_jobs) where:
      - filtered_jobs_df contains only jobs that are new (i.e., whose job_url and identity are not already seen)
      - updated_seen_jobs is the merge of the original seen_jobs and the newly filtered jobs,
        deduplicated on the job_url.
    """
    seen_job_urls = set(seen_jobs["job_url"].dropna().tolist())

    seen_identity = set(
        seen_jobs[["title", "company", "location"]]
        .dropna()
        .apply(lambda row: tuple(x.lower() for x in row), axis=1)
        .tolist()
    )

    filtered_jobs = []
    for _, job in scraped_jobs.iterrows():
        job_url = str(job.get("job_url", "")).strip()
        identity = get_job_identity(job)

        if job_url in seen_job_urls or identity in seen_identity:
            continue
        filtered_jobs.append(job)

    filtered_jobs_df = pd.DataFrame(filtered_jobs)
    updated_seen_jobs = pd.concat([seen_jobs, filtered_jobs_df], ignore_index=True)
    updated_seen_jobs = updated_seen_jobs.drop_duplicates(subset="job_url")

    return filtered_jobs_df, updated_seen_jobs


def filter_jobs_by_field(jobs_df, field, filter_list):
    """
    Given a jobs DataFrame, filter out any row whose value in 'field'
    (converted to lowercase and stripped) is in the filter_list (also lowercased).
    If filter_list is empty, return jobs_df unchanged.
    """
    if not filter_list:
        return jobs_df
    filter_values = {x.strip().lower() for x in filter_list}

    filtered_df = jobs_df[jobs_df[field].fillna("").apply(lambda x: x.strip().lower() not in filter_values)]
    return filtered_df


def main():
    config = load_config(CONFIG_FILE)
    proxies = load_proxies(PROXIES_FILE)
    scraper = JobScraper(proxies)

    if config["search_job_boards"]:
        for search_term, location, country_indeed in config["board_search_terms"]:
            scraper.scrape_job_board_jobs(search_term, location, country_indeed=country_indeed)

    if config["search_google_jobs"]:
        for search_term in config["google_search_terms"]:
            scraper.scrape_google_jobs(search_term)

    scraper.drop_duplicates()

    # Filter pipeline:
    seen_jobs = load_seen_jobs(SEEN_FILE)
    filtered_jobs_df, updated_seen_jobs = filter_seen(scraper.new_jobs, seen_jobs)

    print(f"After filtering seen jobs, {len(filtered_jobs_df)} jobs remain.")

    text_filter_criteria = [
        ("location", "filter_locations", "locations_to_filter"),
        ("title", "filter_job_titles", "job_titles_to_filter"),
        ("company", "filter_companies", "companies_to_filter")
    ]

    for field, flag_key, values_key in text_filter_criteria:
        if config[flag_key]:
            filtered_jobs_df = filter_jobs_by_field(
                filtered_jobs_df,
                field,
                config[values_key]
            )
            print(f"After applying {field} filters, {len(filtered_jobs_df)} jobs remain.")
    #

    save_jobs(NEW_JOBS_FILE, filtered_jobs_df)
    save_jobs(SEEN_FILE, updated_seen_jobs)


if __name__ == "__main__":
    main()
