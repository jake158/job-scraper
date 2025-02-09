import os
import webbrowser
import pandas as pd
import customtkinter as ctk
from src.utils import save_jobs

# -------------------------------
# Job Viewer GUI using customtkinter
# -------------------------------


class JobViewer(ctk.CTk):
    def __init__(self, jobs):
        super().__init__()
        self.title("Job Viewer")
        self.geometry("850x755")
        self.jobs = jobs
        self.current_index = 0

        # Job title
        self.title_label = ctk.CTkLabel(self, text="", font=("Roboto", 20, "bold"))
        self.title_label.pack(pady=10)

        # Job description
        self.description_textbox = ctk.CTkTextbox(self, width=800, height=500)
        self.description_textbox.pack(pady=10)

        # Company name
        self.company_label = ctk.CTkLabel(self, text="", font=("Roboto", 16))
        self.company_label.pack(pady=2)

        # Job location
        self.location_label = ctk.CTkLabel(self, text="", font=("Roboto", 14))
        self.location_label.pack(pady=2)

        # Current job index
        self.index_label = ctk.CTkLabel(self, text=f"{self.current_index}/{len(self.jobs) - 1}", font=("Roboto", 14))
        self.index_label.pack(pady=2)

        # Navigation buttons frame
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=10)

        self.prev_button = ctk.CTkButton(
            self.button_frame, text="Previous", state="disabled", command=self.show_previous
        )
        self.prev_button.grid(row=0, column=0, padx=10)

        self.open_link_button = ctk.CTkButton(
            self.button_frame, text="Open Apply Link", command=self.open_link
        )
        self.open_link_button.grid(row=0, column=1, padx=10)

        self.next_button = ctk.CTkButton(
            self.button_frame, text="Next", command=self.show_next
        )
        self.next_button.grid(row=0, column=2, padx=10)

        # Delete button
        self.delete_button = ctk.CTkButton(self, text="Delete", width=80, command=self.delete)
        self.delete_button.pack(pady=2)

        if not self.jobs.empty:
            self.show_job(self.current_index)
        else:
            self.title_label.configure(text="No jobs found!")
            self.description_textbox.insert("0.0", "Please scrape jobs first.")
            self.open_link_button.configure(state="disabled")
            self.delete_button.configure(state="disabled")
            self.next_button.configure(state="disabled")
            self.index_label.configure(text="0/0")

    def show_job(self, index):
        """Display the job at the given index."""
        if index < 0 or index >= len(self.jobs):
            return

        job = self.jobs.iloc[index]

        title = job["title"] if "title" in job and pd.notna(job["title"]) else "No Title"
        description = (
            job["description"]
            if "description" in job and pd.notna(job["description"])
            else "No Description"
        )
        company = job["company"] if "company" in job and pd.notna(job["company"]) else "N/A"
        location = job["location"] if "location" in job and pd.notna(job["location"]) else "N/A"

        self.title_label.configure(text=title)
        self.description_textbox.delete("0.0", "end")
        self.description_textbox.insert("0.0", description)
        self.company_label.configure(text=f"Company: {company}")
        self.location_label.configure(text=f"Location: {location}")
        self.index_label.configure(text=f"{self.current_index}/{len(self.jobs) - 1}")

        if "job_url" in job and pd.notna(job["job_url"]) and job["job_url"].strip():
            self.open_link_button.configure(state="normal")
        else:
            self.open_link_button.configure(state="disabled")

    def show_next(self):
        """Show the next job if available."""
        if self.current_index < len(self.jobs) - 1:
            self.current_index += 1
            self.prev_button.configure(state="normal")
            self.next_button.configure(state="normal")
            self.show_job(self.current_index)
        if self.current_index == len(self.jobs) - 1:
            self.next_button.configure(state="disabled")

    def show_previous(self):
        """Show the previous job if available."""
        if self.current_index > 0:
            self.current_index -= 1
            self.prev_button.configure(state="normal")
            self.next_button.configure(state="normal")
            self.show_job(self.current_index)
        if self.current_index == 0:
            self.prev_button.configure(state="disabled")

    def open_link(self):
        """Open the job's apply link in the default browser."""
        job = self.jobs.iloc[self.current_index]
        job_url = job["job_url"] if "job_url" in job and pd.notna(job["job_url"]) else None
        if job_url and job_url.strip():
            webbrowser.open(job_url)
        else:
            self.open_link_button.configure(state="disabled")

    def delete(self):
        """Delete the current job from the view and update the CSV file."""
        if self.jobs.empty:
            self.delete_button.configure(state="disabled")
            return

        self.jobs = self.jobs.drop(self.jobs.index[self.current_index]).reset_index(drop=True)
        save_jobs("new_jobs.csv", self.jobs)
        print(f"Deleted job at index {self.current_index}. Updated CSV saved.")

        if self.current_index >= len(self.jobs) and self.current_index > 0:
            self.current_index -= 1

        if not self.jobs.empty:
            self.show_job(self.current_index)
        else:
            self.title_label.configure(text="No jobs found!")
            self.description_textbox.delete("0.0", "end")
            self.description_textbox.insert("0.0", "All jobs deleted.")
            self.company_label.configure(text="")
            self.location_label.configure(text="")
            self.index_label.configure(text="0/0")
            self.open_link_button.configure(state="disabled")
            self.delete_button.configure(state="disabled")
            self.prev_button.configure(state="disabled")
            self.next_button.configure(state="disabled")


def load_jobs(file_path):
    """Load jobs from a CSV file into a DataFrame."""
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            print(f"Error loading jobs: {e}")
            return pd.DataFrame()
    else:
        print(f"{file_path} not found.")
        return pd.DataFrame()


def main():
    ctk.set_appearance_mode("dark")
    jobs = load_jobs("new_jobs.csv")
    app = JobViewer(jobs)
    app.mainloop()


if __name__ == "__main__":
    main()
