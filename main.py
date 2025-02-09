import pandas as pd
from jobspy import scrape_jobs
from src.utils import (
    load_config,
    load_seen_links,
    load_proxies,
    update_seen_links,
    save_new_jobs,
    save_seen_links,
)

SEEN_FILE = "seen.csv"
NEW_JOBS_FILE = "new_jobs.csv"
CONFIG_FILE = "config.json"
PROXIES_FILE = "proxies.txt"


class JobScraper:
    def __init__(self, seen_links, proxies):
        self.seen_links = seen_links
        self.proxies = proxies
        self.new_jobs = pd.DataFrame()

    def _update_results(self, new_jobs):
        if not new_jobs.empty:
            self.new_jobs = pd.concat([self.new_jobs, new_jobs], ignore_index=True)
        self.seen_links = update_seen_links(self.seen_links, new_jobs)

    def scrape_job_board_jobs(self, search_term, location, country_indeed):
        try:
            jobs = scrape_jobs(
                site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor"],
                search_term=search_term,
                location=location,
                results_wanted=20,
                hours_old=72,
                distance=200,
                country_indeed=country_indeed,
                proxies=self.proxies
            )
            print(f"[JOB BOARDS] Scraped {len(jobs)} jobs.")
        except Exception as e:
            print(f"Error scraping job boards for '{search_term}' in '{location}': {e}")
            return pd.DataFrame()

        if "job_url" not in jobs.columns:
            print("Error: 'job_url' column is missing from the scraped jobs DataFrame.")
            return pd.DataFrame()

        new_jobs = jobs[~jobs["job_url"].isin(self.seen_links)]
        print(f"Filtered {len(new_jobs)} new jobs after checking seen links.")

        self._update_results(new_jobs)

    def scrape_google_jobs(self, search_term):
        try:
            jobs = scrape_jobs(
                site_name="google",
                google_search_term=search_term,
                results_wanted=20,
                proxies=self.proxies
            )
            print(f"[GOOGLE] Scraped {len(jobs)} jobs.")
        except Exception as e:
            print(f"Error scraping Google jobs for '{search_term}': {e}")
            return pd.DataFrame()

        if "job_url" not in jobs.columns:
            print("Error: 'job_url' column is missing from the scraped jobs DataFrame.")
            return pd.DataFrame()

        new_jobs = jobs[~jobs["job_url"].isin(self.seen_links)]
        print(f"Filtered {len(new_jobs)} new jobs after checking seen links.")

        self._update_results(new_jobs)

    def drop_duplicates(self):
        if not self.new_jobs.empty:
            self.new_jobs = self.new_jobs.drop_duplicates(subset="job_url")
            self.new_jobs = self.new_jobs.drop_duplicates(subset=["title", "company", "location"])


def main():
    config = load_config(CONFIG_FILE)
    seen_links = load_seen_links(SEEN_FILE)
    proxies = load_proxies(PROXIES_FILE)
    scraper = JobScraper(seen_links, proxies)

    if config["search_job_boards"]:
        for search_term, location, country_indeed in config["board_search_terms"]:
            scraper.scrape_job_board_jobs(search_term, location, country_indeed)

    if config["search_google_jobs"]:
        for search_term in config["google_search_terms"]:
            scraper.scrape_google_jobs(search_term)

    scraper.drop_duplicates()

    save_new_jobs(NEW_JOBS_FILE, scraper.new_jobs)
    save_seen_links(SEEN_FILE, scraper.seen_links)


if __name__ == "__main__":
    main()
