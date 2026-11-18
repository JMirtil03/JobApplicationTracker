"""MySQL access for CareerPath IT. All queries use parameters."""

import json
import os

import mysql.connector
from mysql.connector import Error as MySQLError
from mysql.connector import IntegrityError
from dotenv import load_dotenv

load_dotenv()


class DatabaseUnavailable(Exception):
    """MySQL could not be reached or refused the configured login."""


class ForeignKeyError(Exception):
    """The statement conflicts with a company or job relationship."""


def _config():
    return {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", "careerpath_it"),
        "connection_timeout": 5,
        "charset": "utf8mb4",
        "use_unicode": True,
    }


def connect():
    try:
        return mysql.connector.connect(**_config())
    except MySQLError as exc:
        raise DatabaseUnavailable(
            "MySQL is not available. Check MYSQL_HOST, MYSQL_PORT, MYSQL_USER, "
            "MYSQL_PASSWORD, and MYSQL_DATABASE in the .env file, and confirm schema.sql has been applied."
        ) from exc


def _raise_known(exc):
    if isinstance(exc, IntegrityError) and getattr(exc, "errno", None) in (1451, 1452):
        raise ForeignKeyError("This record is still linked to another record.") from exc
    if isinstance(exc, MySQLError) and getattr(exc, "errno", None) in (1044, 1045, 1049, 2003):
        raise DatabaseUnavailable(
            "MySQL is not available. Check the settings in the .env file and confirm schema.sql has been applied."
        ) from exc
    raise exc


def fetch_all(sql, params=()):
    conn = connect()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        return cursor.fetchall()
    except MySQLError as exc:
        _raise_known(exc)
    finally:
        conn.close()


def fetch_one(sql, params=()):
    rows = fetch_all(sql, params)
    return rows[0] if rows else None


def execute(sql, params=()):
    conn = connect()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.lastrowid
    except MySQLError as exc:
        conn.rollback()
        _raise_known(exc)
    finally:
        conn.close()


def parse_json(value, default):
    if value is None or value == "":
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return default


def _requirements(value):
    raw = parse_json(value, {})
    if not isinstance(raw, dict):
        raw = {}
    skills = raw.get("required_skills") or []
    if isinstance(skills, str):
        skills = [part.strip() for part in skills.split(",")]
    if not isinstance(skills, list):
        skills = []
    return {
        "description": str(raw.get("description") or ""),
        "required_skills": [str(skill) for skill in skills if str(skill).strip()],
        "career_category": str(raw.get("career_category") or ""),
    }


def _interview(value):
    raw = parse_json(value, {})
    if not isinstance(raw, dict):
        raw = {}
    return {
        "interview_date": str(raw.get("interview_date") or ""),
        "interview_type": str(raw.get("interview_type") or ""),
        "interviewer": str(raw.get("interviewer") or ""),
        "notes": str(raw.get("notes") or ""),
    }


def _dump(value):
    return json.dumps(value, ensure_ascii=False)


def _hydrate_job(row):
    if not row:
        return None
    row["requirements"] = _requirements(row.get("requirements"))
    return row


def _hydrate_application(row):
    if not row:
        return None
    row["interview_data"] = _interview(row.get("interview_data"))
    row["cover_letter_sent"] = bool(row.get("cover_letter_sent"))
    return row


def list_companies():
    return fetch_all(
        """
        SELECT c.company_id, c.company_name, c.industry, c.website, c.city, c.state, c.notes,
               (SELECT COUNT(*) FROM jobs j WHERE j.company_id = c.company_id) AS job_count,
               (SELECT COUNT(*) FROM contacts ct WHERE ct.company_id = c.company_id) AS contact_count
        FROM companies c
        ORDER BY c.company_name
        """
    )


def get_company(company_id):
    return fetch_one(
        """
        SELECT company_id, company_name, industry, website, city, state, notes
        FROM companies
        WHERE company_id = %s
        """,
        (company_id,),
    )


def company_reference_counts(company_id):
    row = fetch_one(
        """
        SELECT
          (SELECT COUNT(*) FROM jobs WHERE company_id = %s) AS jobs,
          (SELECT COUNT(*) FROM contacts WHERE company_id = %s) AS contacts
        """,
        (company_id, company_id),
    )
    return {"jobs": int(row["jobs"]), "contacts": int(row["contacts"])} if row else {"jobs": 0, "contacts": 0}


def find_company_id_by_name(name):
    row = fetch_one(
        "SELECT company_id FROM companies WHERE company_name = %s LIMIT 1",
        (name,),
    )
    return row["company_id"] if row else None


def insert_company(data):
    return execute(
        """
        INSERT INTO companies (company_name, industry, website, city, state, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (data["company_name"], data["industry"], data["website"], data["city"], data["state"], data["notes"]),
    )


def update_company(company_id, data):
    execute(
        """
        UPDATE companies
        SET company_name = %s, industry = %s, website = %s, city = %s, state = %s, notes = %s
        WHERE company_id = %s
        """,
        (data["company_name"], data["industry"], data["website"], data["city"], data["state"], data["notes"], company_id),
    )


def delete_company(company_id):
    execute("DELETE FROM companies WHERE company_id = %s", (company_id,))


def list_company_options():
    return fetch_all("SELECT company_id, company_name FROM companies ORDER BY company_name")


def list_jobs():
    rows = fetch_all(
        """
        SELECT j.job_id, j.company_id, j.job_title, j.job_type, j.salary_min, j.salary_max,
               j.job_url, j.date_posted, j.requirements, c.company_name
        FROM jobs j
        JOIN companies c ON c.company_id = j.company_id
        ORDER BY j.date_posted DESC, j.job_title
        """
    )
    return [_hydrate_job(row) for row in rows]


def get_job(job_id):
    return _hydrate_job(fetch_one(
        """
        SELECT j.job_id, j.company_id, j.job_title, j.job_type, j.salary_min, j.salary_max,
               j.job_url, j.date_posted, j.requirements, c.company_name
        FROM jobs j
        JOIN companies c ON c.company_id = j.company_id
        WHERE j.job_id = %s
        """,
        (job_id,),
    ))


def job_reference_counts(job_id):
    row = fetch_one(
        "SELECT COUNT(*) AS applications FROM applications WHERE job_id = %s",
        (job_id,),
    )
    return {"applications": int(row["applications"])} if row else {"applications": 0}


def _insert_job_cursor(cursor, data):
    cursor.execute(
        """
        INSERT INTO jobs
          (company_id, job_title, job_type, salary_min, salary_max, job_url, date_posted, requirements)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            data["company_id"],
            data["job_title"],
            data["job_type"],
            data["salary_min"],
            data["salary_max"],
            data["job_url"],
            data["date_posted"],
            _dump(data["requirements"]),
        ),
    )
    return cursor.lastrowid


def insert_job(data):
    return execute(
        """
        INSERT INTO jobs
          (company_id, job_title, job_type, salary_min, salary_max, job_url, date_posted, requirements)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            data["company_id"],
            data["job_title"],
            data["job_type"],
            data["salary_min"],
            data["salary_max"],
            data["job_url"],
            data["date_posted"],
            _dump(data["requirements"]),
        ),
    )


def insert_company_and_job(company_name, job_data):
    conn = connect()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO companies (company_name) VALUES (%s)", (company_name,))
        job_data = dict(job_data)
        job_data["company_id"] = cursor.lastrowid
        job_id = _insert_job_cursor(cursor, job_data)
        conn.commit()
        return job_id, job_data["company_id"]
    except MySQLError as exc:
        conn.rollback()
        _raise_known(exc)
    finally:
        conn.close()


def update_job(job_id, data):
    execute(
        """
        UPDATE jobs
        SET company_id = %s, job_title = %s, job_type = %s, salary_min = %s, salary_max = %s,
            job_url = %s, date_posted = %s, requirements = %s
        WHERE job_id = %s
        """,
        (
            data["company_id"],
            data["job_title"],
            data["job_type"],
            data["salary_min"],
            data["salary_max"],
            data["job_url"],
            data["date_posted"],
            _dump(data["requirements"]),
            job_id,
        ),
    )


def delete_job(job_id):
    execute("DELETE FROM jobs WHERE job_id = %s", (job_id,))


def list_job_options():
    return fetch_all(
        """
        SELECT j.job_id, j.job_title, c.company_name
        FROM jobs j
        JOIN companies c ON c.company_id = j.company_id
        ORDER BY c.company_name, j.job_title
        """
    )


def jobs_for_company(company_id):
    rows = fetch_all(
        """
        SELECT job_id, job_title, job_type, date_posted, requirements
        FROM jobs
        WHERE company_id = %s
        ORDER BY job_title
        """,
        (company_id,),
    )
    return [_hydrate_job(row) for row in rows]


def list_applications():
    rows = fetch_all(
        """
        SELECT a.application_id, a.job_id, a.application_date, a.status, a.resume_version,
               a.cover_letter_sent, a.interview_data, j.job_title, c.company_name, c.company_id
        FROM applications a
        JOIN jobs j ON j.job_id = a.job_id
        JOIN companies c ON c.company_id = j.company_id
        ORDER BY a.application_date DESC, a.application_id DESC
        """
    )
    return [_hydrate_application(row) for row in rows]


def get_application(application_id):
    return _hydrate_application(fetch_one(
        """
        SELECT a.application_id, a.job_id, a.application_date, a.status, a.resume_version,
               a.cover_letter_sent, a.interview_data, j.job_title, c.company_name, c.company_id
        FROM applications a
        JOIN jobs j ON j.job_id = a.job_id
        JOIN companies c ON c.company_id = j.company_id
        WHERE a.application_id = %s
        """,
        (application_id,),
    ))


def applications_for_job(job_id):
    rows = fetch_all(
        """
        SELECT application_id, application_date, status, resume_version, cover_letter_sent, interview_data
        FROM applications
        WHERE job_id = %s
        ORDER BY application_date DESC
        """,
        (job_id,),
    )
    return [_hydrate_application(row) for row in rows]


def insert_application(data):
    return execute(
        """
        INSERT INTO applications
          (job_id, application_date, status, resume_version, cover_letter_sent, interview_data)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            data["job_id"],
            data["application_date"],
            data["status"],
            data["resume_version"],
            data["cover_letter_sent"],
            _dump(data["interview_data"]),
        ),
    )


def update_application(application_id, data):
    execute(
        """
        UPDATE applications
        SET job_id = %s, application_date = %s, status = %s, resume_version = %s,
            cover_letter_sent = %s, interview_data = %s
        WHERE application_id = %s
        """,
        (
            data["job_id"],
            data["application_date"],
            data["status"],
            data["resume_version"],
            data["cover_letter_sent"],
            _dump(data["interview_data"]),
            application_id,
        ),
    )


def delete_application(application_id):
    execute("DELETE FROM applications WHERE application_id = %s", (application_id,))


def list_contacts():
    return fetch_all(
        """
        SELECT ct.contact_id, ct.company_id, ct.contact_name, ct.title, ct.email, ct.phone,
               ct.linkedin_url, ct.notes, c.company_name
        FROM contacts ct
        JOIN companies c ON c.company_id = ct.company_id
        ORDER BY ct.contact_name
        """
    )


def get_contact(contact_id):
    return fetch_one(
        """
        SELECT ct.contact_id, ct.company_id, ct.contact_name, ct.title, ct.email, ct.phone,
               ct.linkedin_url, ct.notes, c.company_name
        FROM contacts ct
        JOIN companies c ON c.company_id = ct.company_id
        WHERE ct.contact_id = %s
        """,
        (contact_id,),
    )


def contacts_for_company(company_id):
    return fetch_all(
        """
        SELECT contact_id, contact_name, title, email, phone
        FROM contacts
        WHERE company_id = %s
        ORDER BY contact_name
        """,
        (company_id,),
    )


def insert_contact(data):
    return execute(
        """
        INSERT INTO contacts
          (company_id, contact_name, title, email, phone, linkedin_url, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            data["company_id"],
            data["contact_name"],
            data["title"],
            data["email"],
            data["phone"],
            data["linkedin_url"],
            data["notes"],
        ),
    )


def update_contact(contact_id, data):
    execute(
        """
        UPDATE contacts
        SET company_id = %s, contact_name = %s, title = %s, email = %s, phone = %s,
            linkedin_url = %s, notes = %s
        WHERE contact_id = %s
        """,
        (
            data["company_id"],
            data["contact_name"],
            data["title"],
            data["email"],
            data["phone"],
            data["linkedin_url"],
            data["notes"],
            contact_id,
        ),
    )


def delete_contact(contact_id):
    execute("DELETE FROM contacts WHERE contact_id = %s", (contact_id,))


def dashboard_stats():
    row = fetch_one(
        """
        SELECT
          (SELECT COUNT(*) FROM applications) AS applications,
          (SELECT COUNT(*) FROM applications WHERE status = 'Interview') AS interviews,
          (SELECT COUNT(*) FROM jobs) AS jobs,
          (SELECT COUNT(*) FROM applications WHERE status = 'Offer') AS offers
        """
    )
    if not row:
        return {"applications": 0, "interviews": 0, "jobs": 0, "offers": 0}
    return {key: int(row[key]) for key in ("applications", "interviews", "jobs", "offers")}


def recent_applications(limit=5):
    return fetch_all(
        """
        SELECT a.application_id, a.application_date, a.status, j.job_title, c.company_name
        FROM applications a
        JOIN jobs j ON j.job_id = a.job_id
        JOIN companies c ON c.company_id = j.company_id
        ORDER BY a.application_date DESC, a.application_id DESC
        LIMIT %s
        """,
        (int(limit),),
    )
