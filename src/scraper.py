import pandas as pd
from jobspy import scrape_jobs


class JobScraper:
    def __init__(self, proxies):
        self.proxies = proxies
        self.new_jobs = pd.DataFrame()

    def scrape_job_board_jobs(
            self,
            search_term,
            location,
            results_wanted=20,
            hours_old=72,
            distance=200,
            country_indeed="USA"
    ):
        try:
            jobs = scrape_jobs(
                site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor"],
                search_term=search_term,
                location=location,
                results_wanted=results_wanted,
                hours_old=hours_old,
                distance=distance,
                country_indeed=country_indeed,
                proxies=self.proxies
            )
            print(f"[JOB BOARDS] Scraped {len(jobs)} jobs for '{search_term}' in '{location}'.")
        except Exception as e:
            print(f"Error scraping job boards for '{search_term}' in '{location}': {e}")
            return

        if "job_url" not in jobs.columns:
            print("Error: 'job_url' column is missing from the scraped jobs DataFrame.")
            return

        if not jobs.empty:
            self.new_jobs = pd.concat([self.new_jobs, jobs], ignore_index=True)

    def scrape_google_jobs(self, search_term, results_wanted=20):
        try:
            jobs = scrape_jobs(
                site_name="google",
                google_search_term=search_term,
                results_wanted=results_wanted,
                proxies=self.proxies
            )
            print(f"[GOOGLE] Scraped {len(jobs)} jobs for '{search_term}'.")
        except Exception as e:
            print(f"Error scraping Google jobs for '{search_term}': {e}")
            return

        if "job_url" not in jobs.columns:
            print("Error: 'job_url' column is missing from the scraped jobs DataFrame.")
            return

        if not jobs.empty:
            self.new_jobs = pd.concat([self.new_jobs, jobs], ignore_index=True)

    def drop_duplicates(self):
        if not self.new_jobs.empty:
            self.new_jobs = self.new_jobs.drop_duplicates(subset="job_url")
            self.new_jobs = self.new_jobs.drop_duplicates(subset=["title", "company", "location"])
