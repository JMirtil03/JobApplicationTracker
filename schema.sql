-- CareerPath IT
-- COP4751 Advanced Database Management
-- Creates the course database and the four required tables.
-- This script does not remove databases, tables, or rows.

CREATE DATABASE IF NOT EXISTS careerpath_it
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE careerpath_it;

-- requirements JSON shape used by the application:
-- {
--   "description": "original job description",
--   "required_skills": ["Python", "SQL"],
--   "career_category": "Software Development"
-- }
--
-- interview_data JSON shape used by the application:
-- {
--   "interview_date": "2026-03-01",
--   "interview_type": "Video",
--   "interviewer": "Name",
--   "notes": "What was discussed"
-- }

CREATE TABLE IF NOT EXISTS companies (
  company_id INT PRIMARY KEY AUTO_INCREMENT,
  company_name VARCHAR(100) NOT NULL,
  industry VARCHAR(50),
  website VARCHAR(200),
  city VARCHAR(50),
  state VARCHAR(50),
  notes TEXT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS jobs (
  job_id INT PRIMARY KEY AUTO_INCREMENT,
  company_id INT,
  job_title VARCHAR(100) NOT NULL,
  job_type ENUM('Full-time', 'Part-time', 'Contract', 'Internship'),
  salary_min INT,
  salary_max INT,
  job_url VARCHAR(300),
  date_posted DATE,
  requirements JSON,
  CONSTRAINT fk_jobs_company
    FOREIGN KEY (company_id) REFERENCES companies (company_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS applications (
  application_id INT PRIMARY KEY AUTO_INCREMENT,
  job_id INT,
  application_date DATE NOT NULL,
  status ENUM('Applied', 'Screening', 'Interview', 'Offer', 'Rejected', 'Withdrawn'),
  resume_version VARCHAR(50),
  cover_letter_sent BOOLEAN,
  interview_data JSON,
  CONSTRAINT fk_applications_job
    FOREIGN KEY (job_id) REFERENCES jobs (job_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS contacts (
  contact_id INT PRIMARY KEY AUTO_INCREMENT,
  company_id INT,
  contact_name VARCHAR(100) NOT NULL,
  title VARCHAR(100),
  email VARCHAR(100),
  phone VARCHAR(20),
  linkedin_url VARCHAR(200),
  notes TEXT,
  CONSTRAINT fk_contacts_company
    FOREIGN KEY (company_id) REFERENCES companies (company_id)
) ENGINE=InnoDB;
