"""Form validation. Returns display values and, when valid, a database payload."""

import re
from datetime import datetime

from skills import CAREER_CATEGORIES, normalize_skill_list, parse_skill_text

JOB_TYPES = ["Full-time", "Part-time", "Contract", "Internship"]
STATUSES = ["Applied", "Screening", "Interview", "Offer", "Rejected", "Withdrawn"]
INTERVIEW_TYPES = ["Phone", "Video", "On-site", "Technical", "Other"]

_URL = re.compile(r"^https?://\S+$", re.IGNORECASE)
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE = re.compile(r"^[0-9+\-().\s]{7,20}$")


def _text(value, limit):
    return re.sub(r"\s+", " ", str(value or "").strip())[:limit]


def _block(value, limit):
    return str(value or "").replace("\r\n", "\n").strip()[:limit]


def _optional_url(value, limit, field, errors):
    text = _text(value, limit)
    if text and not _URL.match(text):
        errors[field] = "Enter a full URL that starts with http:// or https://."
    return text


def _whole_number(value, field, errors, label):
    text = _text(value, 12)
    if not text:
        return text, None
    if not re.fullmatch(r"\d{1,9}", text):
        errors[field] = f"{label} must be a whole number from 0 through 999,999,999."
        return text, None
    return text, int(text)


def _date(value, field, errors, required):
    text = _text(value, 10)
    if not text:
        if required:
            errors[field] = "Enter a date."
        return text, None
    try:
        parsed = datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        errors[field] = "Enter a valid date."
        return text, None
    return text, parsed


def _choice(value, choices, field, errors, label, required):
    text = str(value or "").strip()
    if not text and not required:
        return ""
    if text not in choices:
        errors[field] = f"Select a valid {label}."
        return text
    return text


def _company_id(value, company_ids, errors):
    text = str(value or "").strip()
    if not text:
        return None
    if not text.isdigit():
        errors["company_id"] = "Select a valid company."
        return None
    company_id = int(text)
    if company_ids is not None and company_id not in company_ids:
        errors["company_id"] = "Select a company that exists."
        return None
    return company_id


def _job_id(value, job_ids, errors):
    text = str(value or "").strip()
    if not text or not text.isdigit():
        errors["job_id"] = "Select a job."
        return None
    job_id = int(text)
    if job_ids is not None and job_id not in job_ids:
        errors["job_id"] = "Select a job that exists."
        return None
    return job_id


def skill_values(form):
    raw = form.getlist("skills") if hasattr(form, "getlist") else form.get("skills", [])
    if isinstance(raw, str):
        raw = [raw]
    extra = parse_skill_text(form.get("extra_skills", ""))
    return normalize_skill_list(list(raw or []) + extra)


def validate_company(form):
    errors = {}
    data = {
        "company_name": _text(form.get("company_name"), 100),
        "industry": _text(form.get("industry"), 50),
        "website": _optional_url(form.get("website"), 200, "website", errors),
        "city": _text(form.get("city"), 50),
        "state": _text(form.get("state"), 50),
        "notes": _block(form.get("notes"), 10000),
    }
    if not data["company_name"]:
        errors["company_name"] = "Enter the company name."
    payload = None
    if not errors:
        payload = {
            "company_name": data["company_name"],
            "industry": data["industry"] or None,
            "website": data["website"] or None,
            "city": data["city"] or None,
            "state": data["state"] or None,
            "notes": data["notes"] or None,
        }
    return data, payload, errors


def validate_job(form, company_ids):
    errors = {}
    salary_min, salary_min_value = _whole_number(form.get("salary_min"), "salary_min", errors, "Minimum salary")
    salary_max, salary_max_value = _whole_number(form.get("salary_max"), "salary_max", errors, "Maximum salary")
    if salary_min_value is not None and salary_max_value is not None and salary_min_value > salary_max_value:
        errors["salary_max"] = "Maximum salary must be greater than or equal to minimum salary."
    posted, posted_value = _date(form.get("date_posted"), "date_posted", errors, required=False)
    category = _choice(form.get("career_category"), CAREER_CATEGORIES, "career_category", errors, "career category", required=False)
    job_type = _choice(form.get("job_type"), JOB_TYPES, "job_type", errors, "job type", required=True)
    company_id = _company_id(form.get("company_id"), company_ids, errors)
    new_company_name = _text(form.get("new_company_name"), 100)
    if new_company_name and company_id and "company_id" not in errors:
        errors["new_company_name"] = "Choose an existing company or enter a new company name, not both."
    if not new_company_name and not company_id and "company_id" not in errors:
        errors["company_id"] = "Select a company or enter a new company name."
    skills = skill_values(form)
    description = _block(form.get("description"), 20000)
    data = {
        "job_title": _text(form.get("job_title"), 100),
        "company_id": str(company_id or form.get("company_id") or "").strip(),
        "new_company_name": new_company_name,
        "job_type": job_type,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "job_url": _optional_url(form.get("job_url"), 300, "job_url", errors),
        "date_posted": posted,
        "career_category": category,
        "description": description,
        "skills": skills,
        "extra_skills": "",
    }
    if not data["job_title"]:
        errors["job_title"] = "Enter the job title."
    requirements = {
        "description": description,
        "required_skills": skills,
        "career_category": category,
    }
    payload = None
    if not errors:
        payload = {
            "company_id": None if new_company_name else company_id,
            "new_company_name": new_company_name or None,
            "job_title": data["job_title"],
            "job_type": job_type,
            "salary_min": salary_min_value,
            "salary_max": salary_max_value,
            "job_url": data["job_url"] or None,
            "date_posted": posted_value,
            "requirements": requirements,
        }
    return data, payload, errors


def validate_application(form, job_ids):
    errors = {}
    applied, applied_value = _date(form.get("application_date"), "application_date", errors, required=True)
    interview_date, interview_date_value = _date(form.get("interview_date"), "interview_date", errors, required=False)
    status = _choice(form.get("status"), STATUSES, "status", errors, "status", required=True)
    interview_type = _choice(form.get("interview_type"), INTERVIEW_TYPES, "interview_type", errors, "interview type", required=False)
    job_id = _job_id(form.get("job_id"), job_ids, errors)
    if job_ids is not None and not job_ids and "job_id" not in errors:
        errors["job_id"] = "Add a job before recording an application."
    data = {
        "job_id": str(job_id or form.get("job_id") or "").strip(),
        "application_date": applied,
        "status": status,
        "resume_version": _text(form.get("resume_version"), 50),
        "cover_letter_sent": str(form.get("cover_letter_sent") or "") == "1",
        "interview_date": interview_date,
        "interview_type": interview_type,
        "interviewer": _text(form.get("interviewer"), 100),
        "interview_notes": _block(form.get("interview_notes"), 5000),
    }
    payload = None
    if not errors:
        payload = {
            "job_id": job_id,
            "application_date": applied_value,
            "status": status,
            "resume_version": data["resume_version"] or None,
            "cover_letter_sent": data["cover_letter_sent"],
            "interview_data": {
                "interview_date": interview_date_value.isoformat() if interview_date_value else "",
                "interview_type": interview_type,
                "interviewer": data["interviewer"],
                "notes": data["interview_notes"],
            },
        }
    return data, payload, errors


def validate_contact(form, company_ids):
    errors = {}
    company_id = _company_id(form.get("company_id"), company_ids, errors)
    if company_ids is not None and not company_ids and "company_id" not in errors:
        errors["company_id"] = "Add a company before recording a contact."
    if not company_id and "company_id" not in errors:
        errors["company_id"] = "Select a company."
    email = _text(form.get("email"), 100)
    if email and not _EMAIL.match(email):
        errors["email"] = "Enter a valid email address."
    phone = _text(form.get("phone"), 20)
    if phone and not _PHONE.match(phone):
        errors["phone"] = "Enter a phone number using 7 to 20 digits, spaces, or + - ( )."
    data = {
        "company_id": str(company_id or form.get("company_id") or "").strip(),
        "contact_name": _text(form.get("contact_name"), 100),
        "title": _text(form.get("title"), 100),
        "email": email,
        "phone": phone,
        "linkedin_url": _optional_url(form.get("linkedin_url"), 200, "linkedin_url", errors),
        "notes": _block(form.get("notes"), 10000),
    }
    if not data["contact_name"]:
        errors["contact_name"] = "Enter the contact name."
    payload = None
    if not errors:
        payload = {
            "company_id": company_id,
            "contact_name": data["contact_name"],
            "title": data["title"] or None,
            "email": data["email"] or None,
            "phone": data["phone"] or None,
            "linkedin_url": data["linkedin_url"] or None,
            "notes": data["notes"] or None,
        }
    return data, payload, errors


def validate_profile(form):
    skills = parse_skill_text(form.get("skills", ""))
    certifications = parse_skill_text(form.get("certifications", ""))
    return {"skills": skills, "certifications": certifications}
