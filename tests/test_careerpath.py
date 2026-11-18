"""Tests that do not connect to MySQL."""

import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from mysql.connector import IntegrityError

import app as app_module
import database
import recommendations
import skills
from validation import validate_application, validate_company, validate_contact, validate_job, validate_profile

ROOT = Path(__file__).resolve().parents[1]

COMPANY = {
    "company_id": 1,
    "company_name": "Northbridge Technical Services",
    "industry": "Managed IT",
    "website": "https://example.com/northbridge",
    "city": "Miami",
    "state": "FL",
    "notes": "Demonstration record",
    "job_count": 1,
    "contact_count": 0,
}

JOB = {
    "job_id": 1,
    "company_id": 1,
    "company_name": "Northbridge Technical Services",
    "job_title": "Python Developer",
    "job_type": "Full-time",
    "salary_min": 80000,
    "salary_max": 105000,
    "job_url": "https://example.com/jobs/python-demo",
    "date_posted": date(2026, 2, 18),
    "requirements": {
        "description": "Build tools with Python and SQL. Tableau is required.",
        "required_skills": ["Python", "SQL", "Tableau"],
        "career_category": "Software Development",
    },
}

EMPTY_JOB = {
    "job_id": 2,
    "company_id": 1,
    "company_name": "Northbridge Technical Services",
    "job_title": "Untitled Role",
    "job_type": "Contract",
    "salary_min": None,
    "salary_max": None,
    "job_url": None,
    "date_posted": None,
    "requirements": {"description": "", "required_skills": [], "career_category": ""},
}

APPLICATION = {
    "application_id": 1,
    "job_id": 1,
    "company_id": 1,
    "job_title": "Python Developer",
    "company_name": "Northbridge Technical Services",
    "application_date": date(2026, 2, 20),
    "status": "Applied",
    "resume_version": "Dev-v1",
    "cover_letter_sent": True,
    "interview_data": {
        "interview_date": "",
        "interview_type": "",
        "interviewer": "",
        "notes": "",
    },
}

CONTACT = {
    "contact_id": 1,
    "company_id": 1,
    "company_name": "Northbridge Technical Services",
    "contact_name": "Sample Contact",
    "title": "IT Manager (demonstration)",
    "email": "sample.contact@example.com",
    "phone": "555-0100",
    "linkedin_url": "https://example.com/sample-contact",
    "notes": "Demonstration record",
}


class SkillTests(unittest.TestCase):
    def test_extracts_requested_skills_and_skips_false_positives(self):
        text = """
        The technician supports Windows 11 and Windows Server, Active Directory, and Azure Active Directory.
        Daily work includes DNS, DHCP, troubleshooting, Linux, SQL, and Python.
        JavaScript is useful. The team documents tickets in ServiceNow.
        AWS and Microsoft Azure cloud services are in scope, along with cybersecurity and a SIEM.
        Social networking experience and GitHub access are not technical requirements.
        An ad hoc report may be requested. Excellent communication is expected.
        """
        found = set(skills.extract_skills(text))
        for name in [
            "Python", "SQL", "JavaScript", "Windows", "Windows Server", "Linux",
            "Active Directory", "Microsoft Entra ID", "Networking", "DNS", "DHCP",
            "Troubleshooting", "Cloud Services", "AWS", "Microsoft Azure",
            "Cybersecurity", "SIEM", "Ticketing Systems",
        ]:
            if name == "Networking":
                continue
            self.assertIn(name, found)
        self.assertNotIn("Java", found)
        self.assertNotIn("Git", found)
        self.assertNotIn("Excel", found)
        self.assertNotIn("Networking", found)
        self.assertIn("Networking", skills.extract_skills("Networking tasks include router support."))
        self.assertNotIn("Networking", skills.extract_skills("Social networking experience is a plus."))
        self.assertEqual(skills.extract_skills("Azure Active Directory"), ["Microsoft Entra ID"])
        self.assertEqual(skills.extract_skills("Windows Server"), ["Windows Server"])
        self.assertNotIn("React", skills.extract_skills("Be ready to react to incidents quickly."))
        self.assertIn("React", skills.extract_skills("Experience with React is required."))
        self.assertEqual(skills.extract_skills("JavaScript developer"), ["JavaScript"])
        self.assertEqual(skills.extract_skills("Java developer"), ["Java"])

    def test_normalizes_aliases_spacing_and_duplicates(self):
        self.assertEqual(
            skills.normalize_skill_list([" py ", "Python", "python3", "AD", "azure ad"]),
            ["Python", "Active Directory", "Microsoft Entra ID"],
        )

    def test_match_percentage_and_empty_requirements(self):
        compared = skills.compare_skills(["Python", "sql"], ["Python", "SQL", "Tableau"])
        self.assertEqual(compared["percentage"], 67)
        self.assertEqual(compared["matched_count"], 2)
        self.assertEqual(compared["required_count"], 3)
        self.assertEqual(compared["missing"], ["Tableau"])
        empty = skills.compare_skills(["Python"], [])
        self.assertIsNone(empty["percentage"])
        self.assertNotEqual(empty["percentage"], 100)
        self.assertEqual(skills.compare_skills([], ["Python"])["percentage"], 0)
        ranked = skills.rank_jobs([EMPTY_JOB, JOB], ["Python", "SQL"])
        self.assertEqual([item["job_title"] for item in ranked], ["Python Developer", "Untitled Role"])
        self.assertIsNone(ranked[1]["percentage"])

    def test_half_up_rounding(self):
        self.assertEqual(skills.match_percentage(1, 8), 13)
        self.assertEqual(skills.match_percentage(1, 1), 100)

    def test_category_suggestion(self):
        self.assertEqual(skills.suggest_category(["Python", "Flask", "SQL"]), "Software Development")


class RecommendationTests(unittest.TestCase):
    def test_every_dictionary_skill_has_curated_guidance(self):
        names = {entry["name"] for entry in skills.SKILL_DICTIONARY}
        self.assertEqual(names, set(recommendations.RECOMMENDATIONS))

    def test_guidance_is_specific_for_examples_and_generic_otherwise(self):
        active_directory = recommendations.guidance_for("Active Directory")["guidance"].lower()
        self.assertIn("windows server", active_directory)
        self.assertIn("password", active_directory)
        self.assertIn("select", recommendations.guidance_for("SQL")["guidance"].lower())
        self.assertIn("automation", recommendations.guidance_for("Python")["guidance"].lower())
        self.assertIn("virtual machine", recommendations.guidance_for("Linux")["guidance"].lower())
        generic = recommendations.guidance_for("COBOL")
        self.assertIn("no curated practice plan", generic["guidance"].lower())
        self.assertEqual(generic["links"], [])

    def test_certifications_are_not_attached_to_every_skill(self):
        self.assertEqual(recommendations.certifications_for_missing(["Python", "SQL", "Git"]), [])
        network = recommendations.certifications_for_missing(["Networking", "DNS", "DHCP"])
        self.assertEqual([item["name"] for item in network], ["CompTIA Network+"])
        self.assertIn("does not guarantee", network[0]["why"].lower())
        support = [item["name"] for item in recommendations.certifications_for_missing(["Windows", "Troubleshooting"])]
        self.assertIn("CompTIA A+", support)
        self.assertNotIn("CompTIA Security+", support)
        cisco = [item["name"] for item in recommendations.certifications_for_missing(["Cisco"])]
        self.assertEqual(cisco, ["Cisco CCNA"])

    def test_links_use_known_official_hosts(self):
        allowed = {
            "learn.microsoft.com", "ubuntu.com", "www.gnu.org", "skillsforall.com",
            "www.netacad.com", "www.cisco.com", "www.comptia.org", "dev.mysql.com",
            "www.postgresql.org", "www.mongodb.com", "docs.oracle.com", "docs.python.org",
            "dev.java", "developer.mozilla.org", "www.typescriptlang.org",
            "flask.palletsprojects.com", "docs.djangoproject.com", "react.dev", "nodejs.org",
            "docs.docker.com", "kubernetes.io", "developer.hashicorp.com", "git-scm.com",
            "docs.aws.amazon.com", "skillbuilder.aws", "cloud.google.com", "docs.splunk.com",
            "www.wireshark.org", "docs.vmware.com", "pandas.pydata.org", "www.tableau.com",
            "support.microsoft.com",
        }
        links = []
        for item in recommendations.RECOMMENDATIONS.values():
            links.extend(item["links"])
        for cert in recommendations.CERTIFICATIONS:
            links.append({"url": cert["url"]})
        self.assertGreater(len(links), 0)
        for link in links:
            url = link["url"]
            self.assertTrue(url.startswith("https://"), url)
            host = url.split("/")[2]
            self.assertIn(host, allowed, url)


class ValidationTests(unittest.TestCase):
    def test_company_and_contact_validation(self):
        _form, payload, errors = validate_company({"company_name": "  ", "website": "javascript:alert(1)"})
        self.assertIn("company_name", errors)
        self.assertIn("website", errors)
        self.assertIsNone(payload)
        _form, payload, errors = validate_company({"company_name": "Northbridge"})
        self.assertEqual(errors, {})
        self.assertEqual(payload["company_name"], "Northbridge")
        self.assertIsNone(payload["website"])
        _form, _payload, errors = validate_contact(
            {"company_id": "1", "contact_name": "Sample", "email": "not-an-email", "phone": "abc"},
            {1},
        )
        self.assertIn("email", errors)
        self.assertIn("phone", errors)

    def test_job_and_application_validation(self):
        form, payload, errors = validate_job({
            "job_title": "Analyst",
            "company_id": "1",
            "job_type": "Full-time",
            "salary_min": "90000",
            "salary_max": "10",
            "extra_skills": "sql, SQL, py",
            "description": "Original description",
        }, {1})
        self.assertIn("salary_max", errors)
        self.assertIsNone(payload)
        self.assertEqual(form["skills"], ["SQL", "Python"])
        _form, payload, errors = validate_job({
            "job_title": "Analyst",
            "new_company_name": "Cedarline",
            "job_type": "Internship",
            "career_category": "Data Analytics",
            "extra_skills": "Excel",
            "description": "Keep this text",
        }, set())
        self.assertEqual(errors, {})
        self.assertEqual(payload["requirements"]["description"], "Keep this text")
        self.assertEqual(payload["requirements"]["required_skills"], ["Excel"])
        self.assertEqual(payload["requirements"]["career_category"], "Data Analytics")
        _form, payload, errors = validate_application({"job_id": "1", "status": "Applied"}, {1})
        self.assertIn("application_date", errors)
        _form, payload, errors = validate_application({
            "job_id": "1",
            "application_date": "2026-02-20",
            "status": "Interview",
            "cover_letter_sent": "1",
            "interview_type": "Video",
            "interview_notes": "Asked about SQL joins.",
        }, {1})
        self.assertEqual(errors, {})
        self.assertTrue(payload["cover_letter_sent"])
        self.assertEqual(payload["interview_data"]["notes"], "Asked about SQL joins.")
        self.assertEqual(payload["status"], "Interview")

    def test_profile_combines_aliases(self):
        profile = validate_profile({"skills": "py, SQL", "certifications": "security+"})
        self.assertEqual(profile["skills"], ["Python", "SQL"])
        self.assertEqual(profile["certifications"], ["CompTIA Security+"])


class SchemaTests(unittest.TestCase):
    def test_schema_has_required_tables_and_no_destructive_statements(self):
        schema = (ROOT / "schema.sql").read_text(encoding="utf-8")
        upper = schema.upper()
        self.assertNotIn("DROP TABLE", upper)
        self.assertNotIn("DROP DATABASE", upper)
        self.assertNotIn("TRUNCATE ", upper)
        for table in ("companies", "jobs", "applications", "contacts"):
            self.assertIn(f"CREATE TABLE IF NOT EXISTS {table}", schema)
        for column in [
            "company_id INT PRIMARY KEY AUTO_INCREMENT",
            "company_name VARCHAR(100) NOT NULL",
            "industry VARCHAR(50)",
            "website VARCHAR(200)",
            "job_id INT PRIMARY KEY AUTO_INCREMENT",
            "job_title VARCHAR(100) NOT NULL",
            "job_type ENUM('Full-time', 'Part-time', 'Contract', 'Internship')",
            "salary_min INT",
            "salary_max INT",
            "job_url VARCHAR(300)",
            "date_posted DATE",
            "requirements JSON",
            "application_id INT PRIMARY KEY AUTO_INCREMENT",
            "application_date DATE NOT NULL",
            "status ENUM('Applied', 'Screening', 'Interview', 'Offer', 'Rejected', 'Withdrawn')",
            "resume_version VARCHAR(50)",
            "cover_letter_sent BOOLEAN",
            "interview_data JSON",
            "contact_id INT PRIMARY KEY AUTO_INCREMENT",
            "contact_name VARCHAR(100) NOT NULL",
            "linkedin_url VARCHAR(200)",
            "REFERENCES companies (company_id)",
            "REFERENCES jobs (job_id)",
        ]:
            self.assertIn(column, schema)
        source = (ROOT / "database.py").read_text(encoding="utf-8")
        self.assertNotIn('f"SELECT', source)
        self.assertNotIn('f"INSERT', source)
        self.assertNotIn('f"UPDATE', source)
        self.assertNotIn('f"DELETE', source)
        self.assertIn("%s", source)

    def test_foreign_key_errors_are_translated(self):
        error = IntegrityError(msg="Cannot delete or update a parent row", errno=1451)
        with self.assertRaises(database.ForeignKeyError):
            database._raise_known(error)


class RouteTests(unittest.TestCase):
    def setUp(self):
        app_module.app.config["TESTING"] = True
        app_module.app.config["PROPAGATE_EXCEPTIONS"] = False
        self.client = app_module.app.test_client()
        returns = {
            "dashboard_stats": {"applications": 4, "interviews": 1, "jobs": 8, "offers": 1},
            "recent_applications": [{
                "application_id": 1,
                "application_date": date(2026, 2, 20),
                "status": "Applied",
                "job_title": "Python Developer",
                "company_name": "Northbridge Technical Services",
            }],
            "list_companies": [COMPANY],
            "get_company": COMPANY,
            "jobs_for_company": [JOB],
            "contacts_for_company": [CONTACT],
            "company_reference_counts": {"jobs": 0, "contacts": 0},
            "list_company_options": [{"company_id": 1, "company_name": COMPANY["company_name"]}],
            "list_jobs": [JOB, EMPTY_JOB],
            "get_job": JOB,
            "applications_for_job": [APPLICATION],
            "job_reference_counts": {"applications": 0},
            "list_applications": [APPLICATION],
            "list_job_options": [{"job_id": 1, "job_title": JOB["job_title"], "company_name": COMPANY["company_name"]}],
            "get_application": APPLICATION,
            "list_contacts": [CONTACT],
            "get_contact": CONTACT,
            "insert_company": 4,
            "update_company": None,
            "delete_company": None,
            "insert_job": 6,
            "update_job": None,
            "delete_job": None,
            "insert_company_and_job": (9, 3),
            "find_company_id_by_name": None,
            "insert_application": 7,
            "update_application": None,
            "delete_application": None,
            "insert_contact": 8,
            "update_contact": None,
            "delete_contact": None,
        }
        self.mocks = {
            name: patch(f"app.database.{name}", return_value=value).start()
            for name, value in returns.items()
        }
        self.addCleanup(patch.stopall)

    def token(self, path):
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200, path)
        html = response.get_data(as_text=True)
        marker = 'name="csrf_token" value="'
        self.assertIn(marker, html)
        return html.split(marker, 1)[1].split('"', 1)[0]

    def test_required_pages_render(self):
        pages = [
            "/", "/companies", "/companies/new", "/companies/1", "/companies/1/edit", "/companies/1/delete",
            "/jobs", "/jobs/new", "/jobs/1", "/jobs/1/edit", "/jobs/1/delete",
            "/applications", "/applications/new", "/applications/1", "/applications/1/edit", "/applications/1/delete",
            "/contacts", "/contacts/new", "/contacts/1", "/contacts/1/edit", "/contacts/1/delete",
            "/job-match",
        ]
        for path in pages:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertIn(b"Developed by Jonathan Mirtil.", response.data)
        dashboard = self.client.get("/").get_data(as_text=True)
        self.assertIn("Analyze a job", dashboard)
        self.assertIn("Understand the role. Build the skills. Advance your career.", dashboard)

    def test_company_crud_validation_and_delete_confirmation(self):
        token = self.token("/companies/new")
        invalid = self.client.post("/companies/new", data={"csrf_token": token, "company_name": " "})
        self.assertEqual(invalid.status_code, 400)
        self.mocks["insert_company"].assert_not_called()
        created = self.client.post("/companies/new", data={
            "csrf_token": token,
            "company_name": "Cedarline Analytics",
            "industry": "Data Analytics",
        })
        self.assertEqual(created.status_code, 302)
        self.assertIn("/companies/4", created.headers["Location"])
        self.mocks["insert_company"].assert_called_once()
        edit_token = self.token("/companies/1/edit")
        updated = self.client.post("/companies/1/edit", data={"csrf_token": edit_token, "company_name": "Cedarline Analytics"})
        self.assertEqual(updated.status_code, 302)
        self.mocks["update_company"].assert_called_once()
        self.mocks["company_reference_counts"].return_value = {"jobs": 2, "contacts": 1}
        blocked = self.client.get("/companies/1/delete").get_data(as_text=True)
        self.assertIn("Delete or move those records first", blocked)
        self.assertNotIn('type="submit"', blocked)
        self.mocks["company_reference_counts"].return_value = {"jobs": 0, "contacts": 0}
        delete_token = self.token("/companies/1/delete")
        deleted = self.client.post("/companies/1/delete", data={"csrf_token": delete_token})
        self.assertEqual(deleted.status_code, 302)
        self.mocks["delete_company"].assert_called_once_with(1)

    def test_job_extract_save_and_relationship_block(self):
        token = self.token("/jobs/new")
        extracted = self.client.post("/jobs/new", data={
            "csrf_token": token,
            "action": "extract",
            "description": "JavaScript developer. Social networking is irrelevant. We use GitHub and Python.",
            "job_type": "Full-time",
            "extra_skills": "COBOL",
        })
        body = extracted.get_data(as_text=True)
        self.assertIn('value="JavaScript"', body)
        self.assertIn('value="Python"', body)
        self.assertIn('value="COBOL"', body)
        self.assertNotIn('name="skills" value="Java"', body)
        self.assertNotIn('name="skills" value="Git"', body)
        self.assertNotIn('name="skills" value="Networking"', body)
        self.assertIn("not a complete reading", body.lower())
        bad_salary = self.client.post("/jobs/new", data={
            "csrf_token": token,
            "action": "save",
            "job_title": "Analyst",
            "company_id": "1",
            "job_type": "Full-time",
            "salary_min": "90000",
            "salary_max": "10",
        })
        self.assertEqual(bad_salary.status_code, 400)
        self.mocks["insert_job"].assert_not_called()
        saved = self.client.post("/jobs/new", data={
            "csrf_token": token,
            "action": "save",
            "job_title": "Data Analyst",
            "new_company_name": "Cedarline Analytics",
            "job_type": "Full-time",
            "career_category": "Data Analytics",
            "description": "Keep the original posting.",
            "extra_skills": "SQL, Excel",
        })
        self.assertEqual(saved.status_code, 302)
        company_name, payload = self.mocks["insert_company_and_job"].call_args[0]
        self.assertEqual(company_name, "Cedarline Analytics")
        self.assertEqual(payload["requirements"]["description"], "Keep the original posting.")
        self.assertEqual(payload["requirements"]["required_skills"], ["SQL", "Excel"])
        self.mocks["job_reference_counts"].return_value = {"applications": 2}
        blocked = self.client.get("/jobs/1/delete").get_data(as_text=True)
        self.assertIn("Delete those applications first", blocked)

    def test_application_and_contact_validation(self):
        token = self.token("/applications/new")
        missing_date = self.client.post("/applications/new", data={
            "csrf_token": token,
            "job_id": "1",
            "status": "Applied",
        })
        self.assertEqual(missing_date.status_code, 400)
        self.mocks["insert_application"].assert_not_called()
        saved = self.client.post("/applications/new", data={
            "csrf_token": token,
            "job_id": "1",
            "application_date": "2026-02-20",
            "status": "Screening",
            "resume_version": "Dev-v1",
            "cover_letter_sent": "1",
        })
        self.assertEqual(saved.status_code, 302)
        self.assertEqual(self.mocks["insert_application"].call_args[0][0]["status"], "Screening")
        contact_token = self.token("/contacts/new")
        bad_email = self.client.post("/contacts/new", data={
            "csrf_token": contact_token,
            "company_id": "1",
            "contact_name": "Sample Contact",
            "email": "not-an-email",
        })
        self.assertEqual(bad_email.status_code, 400)
        self.mocks["insert_contact"].assert_not_called()
        created = self.client.post("/contacts/new", data={
            "csrf_token": contact_token,
            "company_id": "1",
            "contact_name": "Sample Contact",
            "email": "sample.contact@example.com",
            "phone": "555-0100",
        })
        self.assertEqual(created.status_code, 302)
        self.mocks["insert_contact"].assert_called_once()

    def test_job_match_ranks_and_explains_missing_skills(self):
        token = self.token("/job-match")
        response = self.client.post("/job-match", data={
            "csrf_token": token,
            "skills": "py, SQL",
            "certifications": "",
        }, follow_redirects=True)
        body = response.get_data(as_text=True)
        self.assertIn("67%", body)
        self.assertIn("2 of 3 required skills", body)
        self.assertIn("Tableau", body)
        self.assertIn("Not calculated", body)
        self.assertNotIn("100%", body)
        self.assertIn("not a hiring probability", body.lower())
        self.assertIn("sample spreadsheet", body.lower())
        self.assertLess(body.index("Python Developer"), body.index("Untitled Role"))
        self.assertNotIn("Certifications to consider", body)

    def test_missing_page(self):
        self.mocks["get_company"].return_value = None
        self.assertEqual(self.client.get("/companies/999").status_code, 404)


class ProjectFileTests(unittest.TestCase):
    def test_required_files_exist(self):
        required = [
            "app.py", "database.py", "schema.sql", "requirements.txt", "README.md",
            "AI_USAGE.md", ".env.example", ".gitignore", "seed_demo.py",
            "templates/base.html", "templates/dashboard.html", "templates/companies.html",
            "templates/jobs.html", "templates/applications.html", "templates/contacts.html",
            "templates/job_match.html", "static/style.css",
        ]
        for relative in required:
            self.assertTrue((ROOT / relative).is_file(), relative)
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".env", gitignore)
        self.assertIn(".venv/", gitignore)


if __name__ == "__main__":
    unittest.main()
