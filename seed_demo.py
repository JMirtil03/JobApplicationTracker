"""Insert fictional CareerPath IT demonstration records.

The rows are examples for a class demonstration. They are not live job openings
and they are not a person's employment history.

The script inserts data only when the companies table is empty. It does not
delete existing rows.
"""

import json
import sys
from datetime import date

import database

DEMO_NOTE = "Demonstration record for CareerPath IT. Not a real employer or a live job opening."


def requirements(description, skills, category):
    return json.dumps({
        "description": "DEMONSTRATION DATA: " + description,
        "required_skills": skills,
        "career_category": category,
    }, ensure_ascii=False)


def interview(notes):
    return json.dumps({
        "interview_date": "2026-03-04",
        "interview_type": "Video",
        "interviewer": "Sample interviewer",
        "notes": notes,
    }, ensure_ascii=False)


COMPANIES = [
    ("Northbridge Technical Services", "Managed IT", "https://example.com/northbridge", "Miami", "FL"),
    ("Lumen Harbor Health", "Healthcare", "https://example.com/lumen-harbor", "Orlando", "FL"),
    ("Fieldpoint Networks", "Telecommunications", "https://example.com/fieldpoint", "Tallahassee", "FL"),
    ("Harborline Software", "Software", "https://example.com/harborline", "Jacksonville", "FL"),
    ("Bluepeak Cloud", "Cloud Services", "https://example.com/bluepeak", "Atlanta", "GA"),
    ("Redcedar Financial", "Finance", "https://example.com/redcedar", "Charlotte", "NC"),
    ("Keystone Public Schools", "Education", "https://example.com/keystone", "Gainesville", "FL"),
    ("Cedarline Analytics", "Data Analytics", "https://example.com/cedarline", "Tampa", "FL"),
]

JOBS = [
    (0, "IT Support Specialist", "Full-time", 42000, 52000, "https://example.com/jobs/it-support-demo", date(2026, 2, 2),
     "Support staff with Windows, Microsoft 365, Active Directory account changes, and ServiceNow ticketing. Troubleshooting is daily work.",
     ["Windows", "Microsoft 365", "Active Directory", "Ticketing Systems", "Troubleshooting"], "IT Support"),
    (1, "Junior Cybersecurity Analyst", "Full-time", 68000, 82000, "https://example.com/jobs/security-demo", date(2026, 2, 10),
     "Review SIEM alerts, investigate suspicious login activity, and help with incident response. Linux and networking knowledge help.",
     ["Cybersecurity", "SIEM", "Incident Response", "Linux", "Networking"], "Cybersecurity"),
    (2, "Network Technician", "Full-time", 55000, 70000, "https://example.com/jobs/network-demo", date(2026, 1, 20),
     "Maintain Cisco networks. Daily work includes DNS, DHCP, TCP/IP troubleshooting, and subnetting.",
     ["Networking", "Cisco", "DNS", "DHCP", "TCP/IP", "Subnetting"], "Networking"),
    (3, "Python Developer", "Full-time", 80000, 105000, "https://example.com/jobs/python-demo", date(2026, 2, 18),
     "Build internal tools with Python, Flask, SQL, Git, and REST APIs.",
     ["Python", "Flask", "SQL", "Git", "REST APIs"], "Software Development"),
    (4, "Cloud Support Associate", "Full-time", 70000, 90000, "https://example.com/jobs/cloud-demo", date(2026, 3, 1),
     "Support customers using AWS and Microsoft Azure. Cloud services and Linux troubleshooting are required.",
     ["AWS", "Microsoft Azure", "Cloud Services", "Linux", "Troubleshooting"], "Cloud"),
    (5, "Database Administrator", "Full-time", 85000, 110000, "https://example.com/jobs/dba-demo", date(2026, 1, 28),
     "Administer MySQL, write SQL, and own backup and recovery for financial applications.",
     ["MySQL", "SQL", "Backup and Recovery", "Linux"], "Database Administration"),
    (6, "Systems Administrator", "Full-time", 72000, 94000, "https://example.com/jobs/sysadmin-demo", date(2026, 2, 24),
     "Operate Windows Server, Active Directory, Group Policy, PowerShell, and Microsoft Entra ID.",
     ["Windows Server", "Active Directory", "Group Policy", "PowerShell", "Microsoft Entra ID"], "Systems Administration"),
    (7, "Data Analyst", "Full-time", 64000, 84000, "https://example.com/jobs/analyst-demo", date(2026, 3, 6),
     "Analyze operational data with SQL, Excel, Power BI, and Tableau. Python is a plus.",
     ["SQL", "Excel", "Power BI", "Tableau", "Python"], "Data Analytics"),
]


def main():
    try:
        conn = database.connect()
    except database.DatabaseUnavailable as exc:
        print(exc)
        return 1
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM companies")
        if cursor.fetchone()[0]:
            print("Companies already exist. Demonstration data was not inserted.")
            return 0
        company_ids = []
        for name, industry, website, city, state in COMPANIES:
            cursor.execute(
                """
                INSERT INTO companies (company_name, industry, website, city, state, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (name, industry, website, city, state, DEMO_NOTE),
            )
            company_ids.append(cursor.lastrowid)
        job_ids = []
        for index, title, job_type, salary_min, salary_max, url, posted, summary, skills, category in JOBS:
            cursor.execute(
                """
                INSERT INTO jobs
                  (company_id, job_title, job_type, salary_min, salary_max, job_url, date_posted, requirements)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    company_ids[index],
                    title,
                    job_type,
                    salary_min,
                    salary_max,
                    url,
                    posted,
                    requirements(summary, skills, category),
                ),
            )
            job_ids.append(cursor.lastrowid)
        cursor.execute(
            """
            INSERT INTO contacts
              (company_id, contact_name, title, email, phone, linkedin_url, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                company_ids[0],
                "Sample Contact",
                "IT Manager (demonstration)",
                "sample.contact@example.com",
                "555-0100",
                "https://example.com/sample-contact",
                DEMO_NOTE,
            ),
        )
        applications = [
            (job_ids[0], date(2026, 2, 12), "Interview", "Support-v2", True, "Demonstration interview. Not a real meeting."),
            (job_ids[3], date(2026, 2, 20), "Applied", "Dev-v1", True, ""),
            (job_ids[4], date(2026, 3, 8), "Offer", "Cloud-v1", True, "Demonstration offer. Not real employment."),
            (job_ids[7], date(2026, 3, 12), "Rejected", "Analyst-v1", False, ""),
        ]
        for job_id, applied, status, resume, cover, notes in applications:
            cursor.execute(
                """
                INSERT INTO applications
                  (job_id, application_date, status, resume_version, cover_letter_sent, interview_data)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (job_id, applied, status, resume, cover, interview(notes)),
            )
        conn.commit()
    except Exception as exc:
        conn.rollback()
        print("Demonstration data was not inserted.")
        print(exc.__class__.__name__ + ": " + str(exc))
        print("Apply schema.sql before running this script.")
        return 1
    finally:
        conn.close()
    print("Inserted fictional demonstration data.")
    print("These records are not live job openings and are not employment history.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
