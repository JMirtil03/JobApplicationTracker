
# CareerPath IT

**Understand the role. Build the skills. Advance your career.**

CareerPath IT is a full-stack web application developed for COP4751 Advanced Database Management.

The purpose of CareerPath IT is to help people explore IT career opportunities, understand job requirements, identify missing technical skills, and find practical ways to improve their qualifications.

The application also allows users to manage companies, job listings, applications, and professional contacts.

**Developed by Jonathan Mirtil**

## 1. Technologies Used

- Python 3
- Flask
- MySQL
- mysql-connector-python
- HTML and CSS
- python-dotenv
- Git and GitHub
- Cursor AI for code development assistance

The application runs locally and does not require a paid AI API.

## 2. Main Features

### Dashboard

The dashboard provides an overview of:

- Total job applications
- Saved jobs
- Interviews
- Job offers
- Recent applications

### Company Management

Users can create, view, edit, and delete company records.

Company information includes its name, industry, website, location, and notes.

### Job Management

Users can:

- Add and manage IT job positions.
- Enter job requirements manually.
- Paste job descriptions to identify technical skills.
- Review and correct extracted skills.
- Organize positions by IT career category.
- Save original job descriptions.
- View salary information and employment types.

### Application Tracking

Users can track:

- Application dates
- Application statuses
- Resume versions
- Cover letters
- Interview details

Supported statuses include Applied, Screening, Interview, Offer, Rejected, and Withdrawn.

### Contact Management

Users can store and manage recruiter and company contact information.

### Job Match and Skill Gap Analysis

CareerPath IT compares a user's current skills with the requirements of saved job positions.

The application displays:

- Skill match percentage
- Matching qualifications
- Missing technical skills
- Practical learning recommendations
- Relevant certifications
- Educational resources

The platform supports different IT career fields, including IT Support, Cybersecurity, Networking, Software Development, Cloud Computing, Database Administration, Systems Administration, and Data Analytics.

## 3. Database Design

CareerPath IT uses a MySQL database named `careerpath_it`.

The database contains four required tables:

1. `companies`
2. `jobs`
3. `applications`
4. `contacts`

### Database Relationships

- `jobs.company_id` references `companies.company_id`.
- `applications.job_id` references `jobs.job_id`.
- `contacts.company_id` references `companies.company_id`.

The database includes primary keys, foreign keys, and JSON data types.

### JSON Data

The `jobs.requirements` column stores job descriptions, required skills, and career categories.

Example:

```json
{
  "description": "Provide technical support and troubleshoot computer problems.",
  "required_skills": [
    "Windows",
    "Networking",
    "Troubleshooting"
  ],
  "career_category": "IT Support"
}
```

The `applications.interview_data` column stores information such as interview dates, interview types, interviewer names, and interview notes.

The `schema.sql` file contains the database creation script.

The script uses `CREATE DATABASE IF NOT EXISTS` and `CREATE TABLE IF NOT EXISTS` to avoid intentionally deleting existing data.

## 4. Installation Instructions

### Prerequisites

Install the following software:

- Python 3
- MySQL Server
- MySQL Workbench (recommended)
- PyCharm, Cursor, or another compatible code editor

### Step 1: Download the Project

Download or clone the GitHub repository.

Open a terminal in the `JobApplicationTracker` project folder.

### Step 2: Create a Virtual Environment

Run:

```powershell
py -3 -m venv .venv
```

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell prevents activation, use `.venv\Scripts\python.exe` directly to run Python commands.

### Step 3: Install Dependencies

Run:

```powershell
python -m pip install -r requirements.txt
```

This installs the Python packages required by the application.

### Step 4: Configure MySQL

Copy the example environment file:

```powershell
copy .env.example .env
```

Open `.env` and configure the following settings:

```dotenv
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=YOUR_MYSQL_PASSWORD
MYSQL_DATABASE=careerpath_it

SECRET_KEY=YOUR_GENERATED_SECRET_KEY

FLASK_DEBUG=1
PORT=5000
```

Replace the password and secret-key placeholders with your own local values.

To generate a Flask secret key, run:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Do not upload `.env` to GitHub or expose database credentials.

### Step 5: Create the Database

1. Open MySQL Workbench.
2. Connect to your MySQL Server.
3. Select **File > Open SQL Script**.
4. Open `schema.sql`.
5. Execute the SQL script.

Verify that the tables exist by running:

```sql
USE careerpath_it;
SHOW TABLES;
```

The results should show:

- applications
- companies
- contacts
- jobs

The database name must match the value of `MYSQL_DATABASE` in `.env`.

### Step 6: Optional Demonstration Data

The project includes an optional script for fictional sample companies and IT jobs.

Run:

```powershell
python seed_demo.py
```

The script is designed to add demonstration records when the companies table is empty.

These records are fictional and do not represent real job openings.

### Step 7: Start the Application

Run:

```powershell
python app.py
```

Open a browser and visit:

http://127.0.0.1:5000

The CareerPath IT dashboard should appear.

## 5. Job Description Skill Extraction

CareerPath IT provides two methods for entering job requirements.

**Manual Entry**

Users can manually enter technical skills when creating a job listing.

**Job Description Extraction**

Users can paste a complete job description and select the option to identify technical skills.

The application uses a local dictionary of IT skills and common aliases.

For example, an IT Help Desk job description may include:

- Windows
- Active Directory
- Networking
- DNS
- DHCP
- Troubleshooting
- Ticketing Systems
- Microsoft 365
- CompTIA A+

Users can review and correct the identified skills before saving.

The extraction process is rule-based and may not recognize every technical skill. Users should verify the results before saving.

## 6. Job Match Calculation

CareerPath IT calculates the percentage of required skills that match a user's current qualifications.

**Formula:**

Match Percentage = (Matching Required Skills / Total Required Skills) × 100

For example, if a job lists nine qualifications and the user matches four:

```text
4 / 9 × 100 = 44.44%
```

The application displays the rounded percentage and identifies missing qualifications.

Jobs are ranked based on their calculated skill matches.

The percentage represents a comparison of listed qualifications and does not guarantee that a user will qualify for a job or receive an offer.

For jobs without listed required skills, a meaningful percentage cannot be calculated.

## 7. Career Qualification Recommendations

CareerPath IT provides practical recommendations to help users develop missing technical skills.

### Active Directory

Practice creating and managing user accounts, security groups, permissions, and password resets in a Windows Server lab.

### Networking

Practice IP addressing, subnetting, DNS, DHCP, and basic network troubleshooting.

### Ticketing Systems

Practice documenting technical problems, assigning priorities, recording troubleshooting steps, and closing resolved support tickets.

### Linux

Install Linux in a virtual machine and practice command-line navigation, user accounts, permissions, and service management.

### SQL

Practice SELECT, INSERT, UPDATE, DELETE, JOIN, and GROUP BY queries using a sample database.

### Certifications

The application may recommend relevant certifications, including:

- CompTIA A+
- CompTIA Network+
- CompTIA Security+
- Cisco CCNA

Certification recommendations are based on missing skills.

Certifications can help demonstrate technical knowledge, but they do not guarantee employment.

CareerPath IT uses a local Python recommendation library rather than a paid AI API.

## 8. Testing

### Automated Testing

The project includes automated tests for selected features.

Run:

```powershell
python -m compileall -q app.py database.py skills.py recommendations.py validation.py seed_demo.py
```

Then run:

```powershell
python -m unittest discover -s tests -v
```

Automated tests do not replace manual testing with a working MySQL database and web browser.

### Manual Testing Results

The following features were tested during development:

- [x] MySQL database created successfully.
- [x] All four required tables verified.
- [x] Flask server launched successfully.
- [x] Dashboard loaded in the browser.
- [x] Company record created and displayed.
- [x] Job record created and displayed.
- [x] Job description skill extraction tested.
- [x] Nine qualifications extracted from a sample Help Desk job description.
- [x] Job requirements saved successfully.
- [x] Job Match calculated four of nine skills as 44%.
- [x] Missing technical skills identified.
- [x] Qualification recommendations displayed.
- [x] Application record created and displayed.
- [x] Application status updated from Applied to Interview.
- [x] Dashboard statistics reflected the application update.
- [x] Contact record created and displayed.
- [x] Contact deletion confirmation tested.
- [x] Delete button styling corrected.

### Additional Tests

- [ ] Verify editing and deleting company records.
- [ ] Verify editing and deleting job records.
- [ ] Verify editing and deleting application records.
- [ ] Verify foreign-key restrictions.
- [ ] Test manual skill entry without a job description.
- [ ] Test a job without required skills.
- [ ] Test recommendations for unknown skills.
- [ ] Test the responsive layout on a smaller browser window.
- [ ] Test optional sample-data loading.

These additional items should be marked as complete only after successful testing.

## 9. Project Structure

```text
JobApplicationTracker/
|
|-- app.py
|-- database.py
|-- schema.sql
|-- skills.py
|-- recommendations.py
|-- validation.py
|-- seed_demo.py
|-- requirements.txt
|-- README.md
|-- AI_USAGE.md
|-- .env.example
|-- .gitignore
|
|-- templates/
|   |-- base.html
|   |-- dashboard.html
|   |-- companies.html
|   |-- jobs.html
|   |-- applications.html
|   |-- contacts.html
|   |-- job_match.html
|   |-- additional form and detail templates
|
|-- static/
|   |-- style.css
|
|-- tests/
```

Additional templates support the application's forms, detail views, and deletion confirmation.

## 10. Development Process

CareerPath IT was developed using Python, Flask, MySQL, HTML, and CSS, with Cursor AI as the primary coding assistant.

During development, I configured the MySQL database, installed the required Python dependencies, tested the application's features, and corrected issues discovered during testing.

I also used ChatGPT for troubleshooting, including resolving Python dependency errors and correcting a CSS styling issue with the Delete buttons.

Working on this project helped me gain more practical experience with database management, full-stack application development, and troubleshooting.

Additional information about AI assistance, prompts, modifications, and lessons learned is documented in `AI_USAGE.md`.

## 11. Project Demonstration

The project demonstration includes:

1. CareerPath IT running in a web browser.
2. The Flask development server running locally.
3. The MySQL database and its four required tables.
4. Creating and managing company records.
5. Adding a job and identifying skills from a pasted description.
6. Comparing job requirements against a user's qualifications.
7. Viewing missing skills and learning recommendations.
8. Creating and updating job applications.
9. Viewing the dashboard statistics.

The required demonstration video should be between 3 and 7 minutes.

## 12. Developer

**Jonathan Mirtil**

COP4751 — Advanced Database Management

**Project:** CareerPath IT

A professional IT job application tracking and career qualification analysis platform.
