import tkinter as tk
from tkinter import ttk
import csv
from datetime import datetime

def load_jobs():
    try:
        with open('jobs.csv', mode='r') as file:
            csv_reader = csv.DictReader(file)
            return list(csv_reader)
    except FileNotFoundError:
        return []

def save_jobs(jobs):
    with open('jobs.csv', mode='w', newline='') as file:
        fieldnames = jobs[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(jobs)

def mark_job():
    selected_item = job_treeview.selection()[0]
    selected_index = treeview_item_to_job[selected_item]
    job = jobs[selected_index]
    job['Status'] = "Done" if job['Status'] == "Not Done" else "Not Done"
    save_jobs(jobs)
    update_job_treeview(jobs)

def search_job():
    job_number = search_job_entry.get()
    for job in jobs:
        if job['Job Number'] == job_number:
            show_job_details(job)
            return
    show_job_details(None)

def show_job_details(job):
    job_details_window = tk.Toplevel(root)
    job_details_window.title("Job Details")
    if job is not None:
        for key, value in job.items():
            ttk.Label(job_details_window, text=f"{key}: {value}").pack()
    else:
        ttk.Label(job_details_window, text="Job not found").pack()

def apply_filter():
    location_filter_value = location_filter.get()
    client_filter_value = client_filter.get()
    status_filter_value = status_filter.get()

    filtered_jobs = []
    for job in jobs:
        if (not location_filter_value or job['Location'] == location_filter_value) and \
           (not client_filter_value or job['Name'] == client_filter_value) and \
           (not status_filter_value or job['Status'] == status_filter_value):
            filtered_jobs.append(job)

    update_job_treeview(filtered_jobs)

def reset_filters():
    location_filter.set('')
    client_filter.set('')
    status_filter.set('')
    update_job_treeview(jobs)

def update_job_treeview(jobs_to_display):
    job_treeview.delete(*job_treeview.get_children())
    today = datetime.today()
    not_done_jobs = []
    done_jobs = []

    for i, job in enumerate(jobs_to_display):
        job_date = datetime.strptime(job['Production Date'], '%Y-%m-%d')
        days_in_shop = (today - job_date).days
        item = job_treeview.insert('', 'end', values=(job['Sign off Date'], job['Name'], job['Phone Number'],
                                                      job['Location'], job['Production Date'], job['Price'],
                                                      job['Notes'], job['Job Number'],
                                                      days_in_shop if job['Status'] == "Not Done" else "",  # Show Days in Shop for Not Done jobs
                                                      job['Status']))
        treeview_item_to_job[item] = i

        if job['Status'] == "Not Done":
            not_done_jobs.append((item, days_in_shop))
        else:
            done_jobs.append((item, days_in_shop))

    not_done_jobs.sort(key=lambda x: x[1], reverse=True)
    done_jobs.sort(key=lambda x: x[1], reverse=True)

    for item, _ in not_done_jobs:
        job_treeview.move(item, '', 'end')
    for item, _ in done_jobs:
        job_treeview.move(item, '', 'end')

def update_client_filter():
    client_names = set()
    for job in jobs:
        client_names.add(job['Name'])
    client_names_list = sorted(list(client_names))  # Sort alphabetically
    client_filter['values'] = ('',) + tuple(client_names_list)  # Add an empty option

def update_location_filter():
    location_names = set()
    for job in jobs:
        location_names.add(job['Location'])
    location_names_list = sorted(list(location_names))  # Sort alphabetically
    location_filter['values'] = ('',) + tuple(location_names_list)  # Add an empty option

root = tk.Tk()
root.title("Job Management App")

main_frame = ttk.Frame(root)
main_frame.pack(padx=20, pady=20, fill='both', expand=True)

jobs = load_jobs()
treeview_item_to_job = {}

# Create a treeview for displaying job information
job_treeview = ttk.Treeview(main_frame, columns=("Sign off Date", "Name", "Phone Number", "Location", "Production Date", "Price", "Notes", "Job Number", "Days In Shop", "Status"), show="headings")
job_treeview.heading("Sign off Date", text="Sign off Date")
job_treeview.heading("Name", text="Name")
job_treeview.heading("Phone Number", text="Phone Number")
job_treeview.heading("Location", text="Location")
job_treeview.heading("Production Date", text="Production Date")
job_treeview.heading("Price", text="Price")
job_treeview.heading("Notes", text="Notes")
job_treeview.heading("Job Number", text="Job Number")
job_treeview.heading("Days In Shop", text="Days In Shop")
job_treeview.heading("Status", text="Status")

# Create a vertical scrollbar for the job treeview
job_treeview_scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=job_treeview.yview)
job_treeview.configure(yscrollcommand=job_treeview_scrollbar.set)

job_treeview.pack(side='left', fill='both', expand=True)
job_treeview_scrollbar.pack(side='right', fill='y')

# Update the filtered job list
update_job_treeview(jobs)

mark_done_button = ttk.Button(main_frame, text="Mark Job as Done/Not Done", command=mark_job)
mark_done_button.pack()

search_job_label = ttk.Label(main_frame, text="Search Job by Job Number:")
search_job_label.pack()
search_job_entry = ttk.Entry(main_frame)
search_job_entry.pack()

search_button = ttk.Button(main_frame, text="Search", command=search_job)
search_button.pack()

filter_label = ttk.Label(main_frame, text="Filter by:")
filter_label.pack()

location_filter_label = ttk.Label(main_frame, text="Location:")
location_filter_label.pack()
location_filter = ttk.Combobox(main_frame)
location_filter.pack()

client_filter_label = ttk.Label(main_frame, text="Client:")
client_filter_label.pack()
client_filter = ttk.Combobox(main_frame, values=["", "Client 1", "Client 2", "Client 3"])
client_filter.pack()

status_filter_label = ttk.Label(main_frame, text="Status:")
status_filter_label.pack()
status_filter = ttk.Combobox(main_frame, values=["", "Not Done", "Done"])
status_filter.pack()

filter_button = ttk.Button(main_frame, text="Apply Filter", command=apply_filter)
filter_button.pack()

reset_button = ttk.Button(main_frame, text="Reset Filters", command=reset_filters)
reset_button.pack()

# Update the client filter with unique client names
update_client_filter()

# Update the location filter with unique location names
update_location_filter()

root.mainloop()


# Sign off date, Name, Phone, location, production, price, notes, Job Number, day in shop, status