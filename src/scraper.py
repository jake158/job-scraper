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
            indeed_search_term=None,
            results_wanted=20,
            hours_old=72,
            distance=200,
            country_indeed="USA"
    ):
        all_jobs = pd.DataFrame()
        indeed_search_term = indeed_search_term or search_term

        # --- Scrape non-Indeed job boards ---
        non_indeed_sites = ["linkedin", "zip_recruiter", "glassdoor"]
        try:
            jobs = scrape_jobs(
                site_name=non_indeed_sites,
                search_term=search_term,
                location=location,
                results_wanted=results_wanted,
                hours_old=hours_old,
                distance=distance,
                country_indeed=country_indeed,
                proxies=self.proxies
            )
            print(f"[JOB BOARDS] Scraped {len(jobs)} jobs for '{search_term}' in '{location}' (non-Indeed sites).")
        except Exception as e:
            print(f"Error scraping job boards for '{search_term}' in '{location}': {e}")
            jobs = pd.DataFrame()

        all_jobs = pd.concat([all_jobs, jobs], ignore_index=True)

        # --- Scrape Indeed separately ---
        try:
            indeed_jobs = scrape_jobs(
                site_name="indeed",
                search_term=indeed_search_term,
                location=location,
                results_wanted=results_wanted,
                hours_old=hours_old,
                distance=distance,
                country_indeed=country_indeed,
                proxies=self.proxies
            )
            print(f"[INDEED] Scraped {len(indeed_jobs)} jobs for '{indeed_search_term}' in '{location}'.")
        except Exception as e:
            print(f"Error scraping Indeed for '{indeed_search_term}' in '{location}': {e}")
            indeed_jobs = pd.DataFrame()

        all_jobs = pd.concat([all_jobs, indeed_jobs], ignore_index=True)

        # --- Validate and update new_jobs ---
        if all_jobs.empty:
            print("No jobs scraped.")
            return
        if "job_url" not in all_jobs.columns:
            print("Error: 'job_url' column is missing from the scraped jobs DataFrame.")
            return

        self.new_jobs = pd.concat([self.new_jobs, all_jobs], ignore_index=True)

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
