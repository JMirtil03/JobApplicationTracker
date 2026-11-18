"""CareerPath IT web application."""

import os
import secrets
from datetime import date

from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for

import database
from recommendations import CERT_DISCLAIMER, qualification_plan
from skills import (
    CAREER_CATEGORIES,
    MATCH_EXPLANATION,
    NO_SKILLS_MESSAGE,
    extract_skills,
    normalize_skill_list,
    rank_jobs,
    suggest_category,
)
from validation import INTERVIEW_TYPES, JOB_TYPES, STATUSES, validate_application, validate_company, validate_contact, validate_job, validate_profile

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "").strip() or secrets.token_hex(32)


def render_page(template, active, status=200, **context):
    return render_template(template, active_page=active, **context), status


def ensure_csrf():
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_hex(16)
        session["csrf_token"] = token
    return token


def csrf_ok():
    sent = request.form.get("csrf_token", "")
    saved = session.get("csrf_token", "")
    if not sent or not saved:
        return False
    return secrets.compare_digest(sent, saved)


def reject_csrf():
    flash("The form expired. Refresh the page and submit it again.", "error")
    return redirect(request.referrer or url_for("dashboard"))


@app.context_processor
def inject_globals():
    return {
        "csrf_token": ensure_csrf(),
        "match_explanation": MATCH_EXPLANATION,
        "no_skills_message": NO_SKILLS_MESSAGE,
        "cert_disclaimer": CERT_DISCLAIMER,
    }


@app.template_filter("shortdate")
def shortdate(value):
    if not value:
        return "—"
    if isinstance(value, date):
        return value.strftime("%b %d, %Y")
    text = str(value)
    try:
        parsed = date.fromisoformat(text[:10])
    except ValueError:
        return text
    return parsed.strftime("%b %d, %Y")


@app.template_filter("iso")
def iso(value):
    if not value:
        return ""
    if hasattr(value, "isoformat"):
        return value.isoformat()[:10]
    return str(value)[:10]


def salary_text(minimum, maximum):
    def money(amount):
        return f"${int(amount):,}"

    if minimum is not None and maximum is not None:
        return f"{money(minimum)} – {money(maximum)}"
    if minimum is not None:
        return f"From {money(minimum)}"
    if maximum is not None:
        return f"Up to {money(maximum)}"
    return "Not listed"


app.jinja_env.globals["salary_text"] = salary_text


def blank_company():
    return {"company_name": "", "industry": "", "website": "", "city": "", "state": "", "notes": ""}


def company_form(row):
    return {
        "company_name": row.get("company_name") or "",
        "industry": row.get("industry") or "",
        "website": row.get("website") or "",
        "city": row.get("city") or "",
        "state": row.get("state") or "",
        "notes": row.get("notes") or "",
    }


def blank_job():
    return {
        "job_title": "",
        "company_id": "",
        "new_company_name": "",
        "job_type": "Full-time",
        "salary_min": "",
        "salary_max": "",
        "job_url": "",
        "date_posted": "",
        "career_category": "",
        "description": "",
        "skills": [],
        "extra_skills": "",
    }


def job_form(row):
    requirements = row.get("requirements") or {}
    return {
        "job_title": row.get("job_title") or "",
        "company_id": "" if row.get("company_id") is None else str(row.get("company_id")),
        "new_company_name": "",
        "job_type": row.get("job_type") or "Full-time",
        "salary_min": "" if row.get("salary_min") is None else str(row.get("salary_min")),
        "salary_max": "" if row.get("salary_max") is None else str(row.get("salary_max")),
        "job_url": row.get("job_url") or "",
        "date_posted": iso(row.get("date_posted")),
        "career_category": requirements.get("career_category") or "",
        "description": requirements.get("description") or "",
        "skills": list(requirements.get("required_skills") or []),
        "extra_skills": "",
    }


def blank_application():
    return {
        "job_id": "",
        "application_date": date.today().isoformat(),
        "status": "Applied",
        "resume_version": "",
        "cover_letter_sent": False,
        "interview_date": "",
        "interview_type": "",
        "interviewer": "",
        "interview_notes": "",
    }


def application_form(row):
    interview = row.get("interview_data") or {}
    return {
        "job_id": "" if row.get("job_id") is None else str(row.get("job_id")),
        "application_date": iso(row.get("application_date")),
        "status": row.get("status") or "Applied",
        "resume_version": row.get("resume_version") or "",
        "cover_letter_sent": bool(row.get("cover_letter_sent")),
        "interview_date": interview.get("interview_date") or "",
        "interview_type": interview.get("interview_type") or "",
        "interviewer": interview.get("interviewer") or "",
        "interview_notes": interview.get("notes") or "",
    }


def blank_contact():
    return {
        "company_id": "",
        "contact_name": "",
        "title": "",
        "email": "",
        "phone": "",
        "linkedin_url": "",
        "notes": "",
    }


def contact_form(row):
    return {
        "company_id": "" if row.get("company_id") is None else str(row.get("company_id")),
        "contact_name": row.get("contact_name") or "",
        "title": row.get("title") or "",
        "email": row.get("email") or "",
        "phone": row.get("phone") or "",
        "linkedin_url": row.get("linkedin_url") or "",
        "notes": row.get("notes") or "",
    }


def id_set(rows, key):
    return {row[key] for row in rows}


def save_job(payload, job_id=None):
    """Insert or update a job. Reuse a company when the typed name already exists."""
    new_name = payload.get("new_company_name")
    if new_name:
        existing = database.find_company_id_by_name(new_name)
        payload = dict(payload)
        if existing:
            payload["company_id"] = existing
            payload["new_company_name"] = None
        elif job_id:
            payload["company_id"] = database.insert_company({
                "company_name": new_name,
                "industry": None,
                "website": None,
                "city": None,
                "state": None,
                "notes": None,
            })
            payload["new_company_name"] = None
        else:
            new_job_id, _company_id = database.insert_company_and_job(new_name, payload)
            return new_job_id
    if job_id:
        database.update_job(job_id, payload)
        return job_id
    return database.insert_job(payload)


@app.errorhandler(database.DatabaseUnavailable)
def database_unavailable(exc):
    return render_page(
        "message.html",
        "",
        status=503,
        heading="Database connection needed",
        message=str(exc),
        hint="Start MySQL, copy .env.example to .env, set the password, and apply schema.sql. The exact commands are in README.md.",
    )


@app.errorhandler(404)
def page_not_found(_exc):
    return render_page(
        "message.html",
        "",
        status=404,
        heading="Page not found",
        message="That page does not exist.",
        hint="",
    )


@app.route("/")
def dashboard():
    return render_page(
        "dashboard.html",
        "dashboard",
        stats=database.dashboard_stats(),
        recent=database.recent_applications(),
    )


@app.route("/companies")
def companies():
    return render_page("companies.html", "companies", companies=database.list_companies())


@app.route("/companies/new", methods=["GET", "POST"])
def new_company():
    if request.method == "POST":
        if not csrf_ok():
            return reject_csrf()
        form, payload, errors = validate_company(request.form)
        if errors:
            return render_page(
                "company_form.html", "companies", status=400, form=form, errors=errors,
                mode="create", form_action=url_for("new_company"),
            )
        company_id = database.insert_company(payload)
        flash("Company saved.", "success")
        return redirect(url_for("company_detail", company_id=company_id))
    return render_page(
        "company_form.html", "companies", form=blank_company(), errors={},
        mode="create", form_action=url_for("new_company"),
    )


@app.route("/companies/<int:company_id>")
def company_detail(company_id):
    company = database.get_company(company_id)
    if not company:
        abort(404)
    return render_page(
        "company_detail.html",
        "companies",
        company=company,
        jobs=database.jobs_for_company(company_id),
        contacts=database.contacts_for_company(company_id),
    )


@app.route("/companies/<int:company_id>/edit", methods=["GET", "POST"])
def edit_company(company_id):
    company = database.get_company(company_id)
    if not company:
        abort(404)
    if request.method == "POST":
        if not csrf_ok():
            return reject_csrf()
        form, payload, errors = validate_company(request.form)
        if errors:
            return render_page(
                "company_form.html", "companies", status=400, form=form, errors=errors,
                mode="edit", form_action=url_for("edit_company", company_id=company_id),
            )
        database.update_company(company_id, payload)
        flash("Company updated.", "success")
        return redirect(url_for("company_detail", company_id=company_id))
    return render_page(
        "company_form.html", "companies", form=company_form(company), errors={},
        mode="edit", form_action=url_for("edit_company", company_id=company_id),
    )


@app.route("/companies/<int:company_id>/delete", methods=["GET", "POST"])
def delete_company(company_id):
    company = database.get_company(company_id)
    if not company:
        abort(404)
    counts = database.company_reference_counts(company_id)
    blocked = ""
    if counts["jobs"] or counts["contacts"]:
        blocked = (
            f"This company is linked to {counts['jobs']} job(s) and {counts['contacts']} contact(s). "
            "Delete or move those records first."
        )
    if request.method == "POST":
        if not csrf_ok():
            return reject_csrf()
        if blocked:
            flash(blocked, "error")
            return redirect(url_for("company_detail", company_id=company_id))
        try:
            database.delete_company(company_id)
        except database.ForeignKeyError:
            flash("This company cannot be deleted while jobs or contacts still reference it.", "error")
            return redirect(url_for("company_detail", company_id=company_id))
        flash("Company deleted.", "success")
        return redirect(url_for("companies"))
    return render_page(
        "delete_confirm.html",
        "companies",
        heading="Delete company",
        message=f"Delete {company['company_name']}? This cannot be undone.",
        blocked_reason=blocked,
        action=url_for("delete_company", company_id=company_id),
        cancel_url=url_for("company_detail", company_id=company_id),
    )


def job_page(form, errors, mode, action, status=200):
    return render_page(
        "job_form.html",
        "jobs",
        status=status,
        form=form,
        errors=errors,
        companies=database.list_company_options(),
        categories=CAREER_CATEGORIES,
        job_types=JOB_TYPES,
        mode=mode,
        form_action=action,
    )


@app.route("/jobs")
def jobs():
    return render_page("jobs.html", "jobs", jobs=database.list_jobs())


@app.route("/jobs/new", methods=["GET", "POST"])
def new_job():
    if request.method == "POST":
        if not csrf_ok():
            return reject_csrf()
        companies = database.list_company_options()
        form, payload, errors = validate_job(request.form, id_set(companies, "company_id"))
        if request.form.get("action") == "extract":
            if not form["description"]:
                flash("Paste a job description before identifying skills.", "error")
            else:
                form["skills"] = normalize_skill_list(extract_skills(form["description"]) + form["skills"])
                if not form["career_category"]:
                    form["career_category"] = suggest_category(form["skills"])
                flash(
                    "Review the identified skills before saving. Matching uses a curated skill list, so it can miss unusual skills or include the wrong one.",
                    "warning",
                )
            return job_page(form, {}, "create", url_for("new_job"))
        if errors:
            return job_page(form, errors, "create", url_for("new_job"), status=400)
        job_id = save_job(payload)
        if not payload["requirements"]["required_skills"]:
            flash("Job saved without required skills. A match percentage will not be calculated until you add skills.", "warning")
        else:
            flash("Job saved.", "success")
        return redirect(url_for("job_detail", job_id=job_id))
    return job_page(blank_job(), {}, "create", url_for("new_job"))


@app.route("/jobs/<int:job_id>")
def job_detail(job_id):
    job = database.get_job(job_id)
    if not job:
        abort(404)
    return render_page(
        "job_detail.html",
        "jobs",
        job=job,
        applications=database.applications_for_job(job_id),
    )


@app.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
def edit_job(job_id):
    job = database.get_job(job_id)
    if not job:
        abort(404)
    if request.method == "POST":
        if not csrf_ok():
            return reject_csrf()
        companies = database.list_company_options()
        form, payload, errors = validate_job(request.form, id_set(companies, "company_id"))
        if request.form.get("action") == "extract":
            if not form["description"]:
                flash("Paste a job description before identifying skills.", "error")
            else:
                form["skills"] = normalize_skill_list(extract_skills(form["description"]) + form["skills"])
                if not form["career_category"]:
                    form["career_category"] = suggest_category(form["skills"])
                flash(
                    "Review the identified skills before saving. Matching uses a curated skill list, so it can miss unusual skills or include the wrong one.",
                    "warning",
                )
            return job_page(form, {}, "edit", url_for("edit_job", job_id=job_id))
        if errors:
            return job_page(form, errors, "edit", url_for("edit_job", job_id=job_id), status=400)
        save_job(payload, job_id=job_id)
        flash("Job updated.", "success")
        return redirect(url_for("job_detail", job_id=job_id))
    return job_page(job_form(job), {}, "edit", url_for("edit_job", job_id=job_id))


@app.route("/jobs/<int:job_id>/delete", methods=["GET", "POST"])
def delete_job(job_id):
    job = database.get_job(job_id)
    if not job:
        abort(404)
    counts = database.job_reference_counts(job_id)
    blocked = ""
    if counts["applications"]:
        blocked = (
            f"This job is linked to {counts['applications']} application(s). "
            "Delete those applications first."
        )
    if request.method == "POST":
        if not csrf_ok():
            return reject_csrf()
        if blocked:
            flash(blocked, "error")
            return redirect(url_for("job_detail", job_id=job_id))
        try:
            database.delete_job(job_id)
        except database.ForeignKeyError:
            flash("This job cannot be deleted while applications still reference it.", "error")
            return redirect(url_for("job_detail", job_id=job_id))
        flash("Job deleted.", "success")
        return redirect(url_for("jobs"))
    return render_page(
        "delete_confirm.html",
        "jobs",
        heading="Delete job",
        message=f"Delete {job['job_title']} at {job['company_name']}? This cannot be undone.",
        blocked_reason=blocked,
        action=url_for("delete_job", job_id=job_id),
        cancel_url=url_for("job_detail", job_id=job_id),
    )


def application_page(form, errors, mode, action, status=200):
    return render_page(
        "application_form.html",
        "applications",
        status=status,
        form=form,
        errors=errors,
        jobs=database.list_job_options(),
        statuses=STATUSES,
        interview_types=INTERVIEW_TYPES,
        mode=mode,
        form_action=action,
    )


@app.route("/applications")
def applications():
    return render_page("applications.html", "applications", applications=database.list_applications())


@app.route("/applications/new", methods=["GET", "POST"])
def new_application():
    if request.method == "POST":
        if not csrf_ok():
            return reject_csrf()
        jobs = database.list_job_options()
        form, payload, errors = validate_application(request.form, id_set(jobs, "job_id"))
        if errors:
            return application_page(form, errors, "create", url_for("new_application"), status=400)
        application_id = database.insert_application(payload)
        flash("Application saved.", "success")
        return redirect(url_for("application_detail", application_id=application_id))
    return application_page(blank_application(), {}, "create", url_for("new_application"))


@app.route("/applications/<int:application_id>")
def application_detail(application_id):
    application = database.get_application(application_id)
    if not application:
        abort(404)
    return render_page("application_detail.html", "applications", application=application)


@app.route("/applications/<int:application_id>/edit", methods=["GET", "POST"])
def edit_application(application_id):
    application = database.get_application(application_id)
    if not application:
        abort(404)
    if request.method == "POST":
        if not csrf_ok():
            return reject_csrf()
        jobs = database.list_job_options()
        form, payload, errors = validate_application(request.form, id_set(jobs, "job_id"))
        if errors:
            return application_page(form, errors, "edit", url_for("edit_application", application_id=application_id), status=400)
        database.update_application(application_id, payload)
        flash("Application updated.", "success")
        return redirect(url_for("application_detail", application_id=application_id))
    return application_page(application_form(application), {}, "edit", url_for("edit_application", application_id=application_id))


@app.route("/applications/<int:application_id>/delete", methods=["GET", "POST"])
def delete_application(application_id):
    application = database.get_application(application_id)
    if not application:
        abort(404)
    if request.method == "POST":
        if not csrf_ok():
            return reject_csrf()
        database.delete_application(application_id)
        flash("Application deleted.", "success")
        return redirect(url_for("applications"))
    label = f"{application['job_title']} at {application['company_name']}"
    return render_page(
        "delete_confirm.html",
        "applications",
        heading="Delete application",
        message=f"Delete the application for {label}? This cannot be undone.",
        blocked_reason="",
        action=url_for("delete_application", application_id=application_id),
        cancel_url=url_for("application_detail", application_id=application_id),
    )


def contact_page(form, errors, mode, action, status=200):
    return render_page(
        "contact_form.html",
        "contacts",
        status=status,
        form=form,
        errors=errors,
        companies=database.list_company_options(),
        mode=mode,
        form_action=action,
    )


@app.route("/contacts")
def contacts():
    return render_page("contacts.html", "contacts", contacts=database.list_contacts())


@app.route("/contacts/new", methods=["GET", "POST"])
def new_contact():
    if request.method == "POST":
        if not csrf_ok():
            return reject_csrf()
        companies = database.list_company_options()
        form, payload, errors = validate_contact(request.form, id_set(companies, "company_id"))
        if errors:
            return contact_page(form, errors, "create", url_for("new_contact"), status=400)
        contact_id = database.insert_contact(payload)
        flash("Contact saved.", "success")
        return redirect(url_for("contact_detail", contact_id=contact_id))
    return contact_page(blank_contact(), {}, "create", url_for("new_contact"))


@app.route("/contacts/<int:contact_id>")
def contact_detail(contact_id):
    contact = database.get_contact(contact_id)
    if not contact:
        abort(404)
    return render_page("contact_detail.html", "contacts", contact=contact)


@app.route("/contacts/<int:contact_id>/edit", methods=["GET", "POST"])
def edit_contact(contact_id):
    contact = database.get_contact(contact_id)
    if not contact:
        abort(404)
    if request.method == "POST":
        if not csrf_ok():
            return reject_csrf()
        companies = database.list_company_options()
        form, payload, errors = validate_contact(request.form, id_set(companies, "company_id"))
        if errors:
            return contact_page(form, errors, "edit", url_for("edit_contact", contact_id=contact_id), status=400)
        database.update_contact(contact_id, payload)
        flash("Contact updated.", "success")
        return redirect(url_for("contact_detail", contact_id=contact_id))
    return contact_page(contact_form(contact), {}, "edit", url_for("edit_contact", contact_id=contact_id))


@app.route("/contacts/<int:contact_id>/delete", methods=["GET", "POST"])
def delete_contact(contact_id):
    contact = database.get_contact(contact_id)
    if not contact:
        abort(404)
    if request.method == "POST":
        if not csrf_ok():
            return reject_csrf()
        database.delete_contact(contact_id)
        flash("Contact deleted.", "success")
        return redirect(url_for("contacts"))
    return render_page(
        "delete_confirm.html",
        "contacts",
        heading="Delete contact",
        message=f"Delete {contact['contact_name']}? This cannot be undone.",
        blocked_reason="",
        action=url_for("delete_contact", contact_id=contact_id),
        cancel_url=url_for("contact_detail", contact_id=contact_id),
    )


def profile_skills():
    skills = session.get("user_skills") or []
    certifications = session.get("user_certifications") or []
    return normalize_skill_list(list(skills) + list(certifications))


@app.route("/job-match", methods=["GET", "POST"])
def job_match():
    if request.method == "POST":
        if not csrf_ok():
            return reject_csrf()
        profile = validate_profile(request.form)
        session["user_skills"] = profile["skills"]
        session["user_certifications"] = profile["certifications"]
        session["profile_saved"] = True
        flash("Your skills were saved in this browser session.", "success")
        return redirect(url_for("job_match"))
    owned = profile_skills()
    saved = bool(session.get("profile_saved"))
    results = []
    if saved and owned:
        for result in rank_jobs(database.list_jobs(), owned):
            result["plan"] = qualification_plan(result["missing"])
            results.append(result)
    return render_page(
        "job_match.html",
        "job_match",
        skills=session.get("user_skills") or [],
        certifications=session.get("user_certifications") or [],
        profile_saved=saved,
        has_skills=bool(owned),
        results=results,
        saved_jobs=database.list_jobs() if not (saved and owned) else [],
    )


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
