import sys
import csv
import pandas as pd
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton, QLineEdit, QDialog, QLabel, QHBoxLayout
from PyQt5.QtGui import QColor, QFont
from fpdf import FPDF


class JobManagementApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Job Management App")
        self.setGeometry(100, 100, 800, 600)

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.layout = QVBoxLayout(self.centralWidget)

        # Create a table widget to display data
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setColumnCount(11)  # Adjust column count according to your data
        self.tableWidget.setHorizontalHeaderLabels(["Sign off Date", "Name", "Phone Number", "Location", "Production Date", "Price", "Notes", "Job Number", "Status", "Days In Shop", "Edit"])

        # Hide the vertical header (row index)
        self.tableWidget.verticalHeader().setVisible(False)

        self.layout.addWidget(self.tableWidget)

        # Create a button to add a new job
        self.add_job_button = QPushButton("Add New Job", self)
        self.add_job_button.clicked.connect(self.add_new_job)
        self.layout.addWidget(self.add_job_button)

        # Create input field for searching by Job Number
        self.job_number_label = QLabel("Search by Job Number:")
        self.layout.addWidget(self.job_number_label)

        self.job_number_input = QLineEdit(self)
        self.layout.addWidget(self.job_number_input)

        self.search_button = QPushButton("Search", self)
        self.search_button.clicked.connect(self.search_by_job_number)
        self.layout.addWidget(self.search_button)

        self.print_pdf_button = QPushButton("Print PDF", self)
        self.print_pdf_button.clicked.connect(self.print_pdf)
        self.layout.addWidget(self.print_pdf_button)

        # Load and display data from the CSV file
        self.load_and_display_data()

        # Adjust column sizes to fit contents
        self.tableWidget.resizeColumnsToContents()

        # Set font size for labels and buttons
        font = QFont()
        font.setPointSize(14)  # Adjust the font size as needed
        self.job_number_label.setFont(font)
        self.add_job_button.setFont(font)
        self.search_button.setFont(font)

        self.showMaximized()

    def print_pdf(self):
        # Load data from the CSV file
        data = self.load_data_from_csv("jobs.csv")

        # Filter jobs that are not done
        not_done_jobs = [job for job in data if job["Status"] == "Not Done"]

        # Create a Pandas DataFrame from the filtered data
        df = pd.DataFrame(not_done_jobs)

        # Remove the time portion from the "Production Date"
        df['Production Date'] = pd.to_datetime(df['Production Date']).dt.strftime('%Y-%m-%d')

        # Calculate "Days In Shop" and add it to the DataFrame
        df['Days In Shop'] = (pd.Timestamp.now() - pd.to_datetime(df['Production Date'])).dt.days

        # Create a PDF document with landscape orientation
        pdf = FPDF(orientation='L')  # Landscape orientation
        pdf.add_page()
        pdf.set_font("Arial", size=10)

        # Initialize a list to store maximum column widths
        max_col_widths = [pdf.get_string_width(col) + 6 for col in df.columns]  # 6 is for padding

        # Iterate over the DataFrame to find the maximum width for each column
        for _, row in df.iterrows():
            for col in df.columns:
                col_width = pdf.get_string_width(str(row[col])) + 6  # 6 is for padding
                max_col_widths[df.columns.get_loc(col)] = max(max_col_widths[df.columns.get_loc(col)], col_width)

        # Calculate the total page width
        total_width = sum(max_col_widths)

        # Calculate the column widths based on the maximum widths and total width
        col_widths = [(w / total_width) * pdf.w for w in max_col_widths]

        # Remove the "Status" column from the DataFrame
        df = df.drop(columns=["Status"])

        # Add a table to the PDF with adjusted column widths and text wrapping
        pdf.set_fill_color(255, 255, 255)  # Set fill color to white
        pdf.set_text_color(0, 0, 0)  # Set text color to black

        # Print the header row
        for col in df.columns:
            pdf.cell(col_widths[df.columns.get_loc(col)], 10, txt=col, border=1, fill=1)
        pdf.ln()

        # Define a function to get the background color based on days in shop
        def get_background_color(days_in_shop):
            max_days = 30
            g = int(255 - (255 * days_in_shop / max_days))
            r = int(255 * days_in_shop / max_days)
            b = 0
            return r, g, b

        # Print each job's data side by side with a color gradient for "Days In Shop"
        for _, row in df.iterrows():
            for col in df.columns:
                cell_text = str(row[col])
                # If the column is "Days In Shop," apply the background color gradient
                if col == "Days In Shop":
                    days_in_shop = int(row[col])
                    r, g, b = get_background_color(days_in_shop)
                    pdf.set_fill_color(r, g, b)
                    pdf.cell(col_widths[df.columns.get_loc(col)], 10, txt=cell_text, border=1, fill=1)
                    pdf.set_fill_color(255, 255, 255)  # Reset fill color to white
                else:
                    pdf.cell(col_widths[df.columns.get_loc(col)], 10, txt=cell_text, border=1)
            pdf.ln()

        # Save the PDF to a file
        pdf_file_path = "not_done_jobs.pdf"
        pdf.output(pdf_file_path)

    def load_and_display_data(self):
        # Load data from the CSV file
        data = self.load_data_from_csv("jobs.csv")  # Replace with your CSV file name

        # Calculate "Days In Shop" and display data
        sorted_data = self.sort_and_display_data(data)

    def load_data_from_csv(self, file_path):
        try:
            with open(file_path, mode='r') as file:
                csv_reader = csv.DictReader(file)
                return list(csv_reader)
        except FileNotFoundError:
            return []

    def sort_and_display_data(self, data):
        # Separate data into "Not Done" and "Done" groups
        not_done_jobs = []
        done_jobs = []

        for record in data:
            production_date = datetime.strptime(record["Production Date"], '%Y-%m-%d')
            days_in_shop = (datetime.now() - production_date).days
            record["Days In Shop"] = str(days_in_shop)

            if record["Status"] == "Not Done":
                not_done_jobs.append(record)
            else:
                done_jobs.append(record)

        # Sort both groups by "Days In Shop" in descending order
        not_done_jobs.sort(key=lambda x: int(x["Days In Shop"]), reverse=True)
        done_jobs.sort(key=lambda x: int(x["Days In Shop"]), reverse=True)

        # Display the combined and sorted data
        sorted_data = not_done_jobs + done_jobs
        self.display_data(sorted_data)

    def display_data(self, data):
        self.tableWidget.setRowCount(len(data))

        for row, record in enumerate(data):
            for col, value in enumerate(record.values()):
                item = QTableWidgetItem(value)
                self.tableWidget.setItem(row, col, item)

            # Set "Days In Shop" cell text to blank for done jobs
            if record["Status"] == "Done":
                item = QTableWidgetItem("")  # Blank text for "Days In Shop"
                self.tableWidget.setItem(row, 9, item)

            # Calculate background color for "Days In Shop" based on a gradient scale
            days_in_shop = int(record["Days In Shop"])
            bg_color = self.get_background_color(days_in_shop)
            self.tableWidget.item(row, 9).setBackground(bg_color)

            # Grey out the row for done jobs
            if record["Status"] == "Done":
                for col in range(10):  # Assuming 10 columns
                    self.tableWidget.item(row, col).setBackground(QColor(220, 220, 220))  # Grey background

            # Create an "Edit" button for each row
            edit_button = QPushButton("Edit")
            edit_button.clicked.connect(lambda checked, row=row: self.edit_job(row))
            self.tableWidget.setCellWidget(row, 10, edit_button)

    def get_background_color(self, days_in_shop):
        # Define the maximum days for the gradient scale
        max_days = 30

        # Set to red if days_in_shop exceeds max_days
        if days_in_shop > max_days:
            return QColor(255, 0, 0)  # Red

        # Calculate a gradient color based on the number of days
        min_color = QColor(0, 255, 0)  # Green (for 0 days)
        max_color = QColor(255, 0, 0)  # Red (for max_days)

        # Interpolate between min_color and max_color based on days_in_shop
        r = self.interpolate_color(min_color.red(), max_color.red(), days_in_shop, max_days)
        g = self.interpolate_color(min_color.green(), max_color.green(), days_in_shop, max_days)
        b = self.interpolate_color(min_color.blue(), max_color.blue(), days_in_shop, max_days)

        return QColor(r, g, b)

    def interpolate_color(self, start, end, value, max_value):
        # Interpolate a color component (e.g., red, green, or blue) based on a value and a maximum value
        return int(start + (end - start) * (value / max_value))

    def search_by_job_number(self):
        job_number = self.job_number_input.text()
        job_data = self.find_job_by_number(job_number)

        if job_data:
            self.show_job_details(job_data)
        else:
            self.show_job_not_found_message()

    def find_job_by_number(self, job_number):
        # Load data from the CSV file
        data = self.load_data_from_csv("jobs.csv")  # Replace with your CSV file name

        # Search for the job by Job Number
        for record in data:
            if record["Job Number"] == job_number:
                return record

        return None

    def show_job_details(self, job_data):
        job_details_dialog = QDialog(self)
        job_details_dialog.setWindowTitle("Job Details")

        layout = QVBoxLayout()

        for key, value in job_data.items():
            label = QLabel(f"{key}: {value}")
            layout.addWidget(label)

        job_details_dialog.setLayout(layout)
        job_details_dialog.exec_()

    def show_job_not_found_message(self):
        not_found_dialog = QDialog(self)
        not_found_dialog.setWindowTitle("Job Not Found")

        layout = QVBoxLayout()

        label = QLabel("Job not found.")
        layout.addWidget(label)

        not_found_dialog.setLayout(layout)
        not_found_dialog.exec_()

    def add_new_job(self):
        # Create a dialog for adding a new job
        add_job_dialog = QDialog(self)
        add_job_dialog.setWindowTitle("Add New Job")

        # Create input fields for job details
        form_layout = QVBoxLayout()

        labels = ["Sign off Date (YYYY-MM-DD):", "Name:", "Phone Number:", "Location:", "Production Date (YYYY-MM-DD):", "Price:", "Notes:", "Job Number:", "Status (Done/Not Done):"]
        placeholders = ["e.g., 2023-09-18", "e.g., John Doe", "e.g., 123-456-7890", "e.g., New York, NY", "e.g., 2023-09-18", "e.g., 500", "e.g., Additional details", "e.g., 12345", "e.g., Done"]

        input_fields = []
        for label, placeholder in zip(labels, placeholders):
            label_widget = QLabel(label)
            input_widget = QLineEdit()
            input_widget.setPlaceholderText(placeholder)
            input_fields.append(input_widget)
            form_layout.addWidget(label_widget)
            form_layout.addWidget(input_widget)

        # Create buttons for adding the new job and canceling
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add")
        cancel_button = QPushButton("Cancel")

        add_button.clicked.connect(add_job_dialog.accept)
        cancel_button.clicked.connect(add_job_dialog.reject)

        button_layout.addWidget(add_button)
        button_layout.addWidget(cancel_button)

        # Combine form layout and button layout
        dialog_layout = QVBoxLayout()
        dialog_layout.addLayout(form_layout)
        dialog_layout.addLayout(button_layout)

        add_job_dialog.setLayout(dialog_layout)

        # Execute the dialog and handle user input
        result = add_job_dialog.exec_()

        if result == QDialog.Accepted:
            # Retrieve user-entered data
            new_job_data = {}
            for label, input_field in zip(labels, input_fields):
                field_name = label.split(":")[0].strip()  # Extract field name from label
                field_value = input_field.text()
                new_job_data[field_name] = field_value

            # Validate and add the new job to the CSV
            if self.validate_and_add_job(new_job_data):
                # Reload and display the updated data
                self.load_and_display_data()

    def validate_and_add_job(self, new_job_data):
        # Validate the new job data here (e.g., check if fields are not empty, date formats are correct, etc.)
        # You can implement your own validation logic based on your requirements.

        # For demonstration purposes, let's assume basic validation where fields must not be empty.
        for key, value in new_job_data.items():
            if not value:
                self.show_error_message("Please fill in all fields.")
                return False

        # Assuming all validation passed, add the new job to the CSV file
        file_path = "jobs.csv"  # Replace with your CSV file path
        try:
            with open(file_path, mode='a', newline='') as file:
                fieldnames = new_job_data.keys()
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writerow(new_job_data)
            return True
        except Exception as e:
            self.show_error_message(f"Error adding the job: {str(e)}")
            return False

    def show_error_message(self, message):
        error_dialog = QDialog(self)
        error_dialog.setWindowTitle("Error")
        layout = QVBoxLayout()
        label = QLabel(message)
        layout.addWidget(label)
        error_dialog.setLayout(layout)
        error_dialog.exec_()

    def edit_job(self, row):
        # Get the job data from the selected row
        job_data = {}
        for col in range(10):  # Assuming 10 columns
            header = self.tableWidget.horizontalHeaderItem(col).text()
            item = self.tableWidget.item(row, col)
            if header and item:
                job_data[header] = item.text()

        # Create a dialog for editing the job
        edit_job_dialog = QDialog(self)
        edit_job_dialog.setWindowTitle("Edit Job")

        # Create input fields for job details with pre-filled values
        form_layout = QVBoxLayout()

        labels = ["Sign off Date:", "Name:", "Phone Number:", "Location:", "Production Date:", "Price:", "Notes:", "Job Number:", "Status:"]
        placeholders = ["e.g., 2023-09-18", "e.g., John Doe", "e.g., 123-456-7890", "e.g., New York, NY", "e.g., 2023-09-18", "e.g., 500", "e.g., Additional details", "e.g., 12345", "e.g., Done"]

        input_fields = []
        for label, placeholder in zip(labels, placeholders):
            if label != "Days In Shop:":
                field_name = label.split(":")[0].strip()  # Extract field name from label
                label_widget = QLabel(label)
                input_widget = QLineEdit()
                input_widget.setPlaceholderText(placeholder)
                input_widget.setText(job_data.get(field_name, ""))  # Pre-fill with existing values
                input_fields.append((field_name, input_widget))  # Store field name along with input widget
                form_layout.addWidget(label_widget)
                form_layout.addWidget(input_widget)

        # Create buttons for saving the edited job and canceling
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")

        save_button.clicked.connect(edit_job_dialog.accept)
        cancel_button.clicked.connect(edit_job_dialog.reject)

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        # Combine form layout and button layout
        dialog_layout = QVBoxLayout()
        dialog_layout.addLayout(form_layout)
        dialog_layout.addLayout(button_layout)

        edit_job_dialog.setLayout(dialog_layout)

        # Execute the dialog and handle user input
        result = edit_job_dialog.exec_()

        if result == QDialog.Accepted:
            # Retrieve user-edited data
            edited_job_data = {}
            for field_name, input_field in input_fields:
                field_value = input_field.text()
                edited_job_data[field_name] = field_value

            # Update the edited job data in the CSV (excluding "Days In Shop")
            if self.update_job_data(row, edited_job_data):
                # Reload and display the updated data
                self.load_and_display_data()

    def update_job_data(self, row, edited_job_data):
        # Load data from the CSV file
        file_path = "jobs.csv"  # Replace with your CSV file path
        data = self.load_data_from_csv(file_path)

        # Find the corresponding row in the data
        for record in data:
            if record["Job Number"] == edited_job_data["Job Number"]:
                # Update the record with edited values
                record.update(edited_job_data)

        # Write the updated data back to the CSV file
        try:
            with open(file_path, mode='w', newline='') as file:
                fieldnames = data[0].keys() if data else edited_job_data.keys()
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception as e:
            self.show_error_message(f"Error updating the job: {str(e)}")
            return False

def main():
    app = QApplication(sys.argv)
    window = JobManagementApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
