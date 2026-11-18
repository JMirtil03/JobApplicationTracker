"""Curated IT skill dictionary, extraction, and match math.

Extraction is a local phrase check. It is not an AI model and it is not perfect.
"""

import re
from decimal import Decimal, ROUND_HALF_UP

CAREER_CATEGORIES = [
    "IT Support",
    "Cybersecurity",
    "Networking",
    "Software Development",
    "Cloud",
    "Database Administration",
    "Systems Administration",
    "Data Analytics",
    "Other",
]

MATCH_EXPLANATION = (
    "Match percentage is the number of listed required skills you already have, "
    "divided by the total required skills, multiplied by 100. "
    "It describes that skill list only. It is not a hiring probability."
)

NO_SKILLS_MESSAGE = (
    "This job has no required skills listed, so a match percentage is not shown."
)

# Longer and more specific phrases are listed first so the review list is stable.
# Patterns are applied independently with word or phrase boundaries.
SKILL_DICTIONARY = [
    {"name": "Microsoft Entra ID", "patterns": [
        r"\bmicrosoft entra id\b",
        r"\bentra id\b",
        r"\bazure active directory\b",
        r"\bazure ad\b",
    ]},
    {"name": "Active Directory", "patterns": [
        r"(?<!azure\s)\bactive directory\b",
        r"\bad ds\b",
    ]},
    {"name": "Windows Server", "patterns": [r"\bwindows server\b"]},
    {"name": "Windows", "patterns": [r"\bwindows\b(?!\s+server\b)"]},
    {"name": "JavaScript", "patterns": [r"\bjavascript\b"]},
    {"name": "TypeScript", "patterns": [r"\btypescript\b"]},
    {"name": "PowerShell", "patterns": [r"\bpowershell\b", r"\bpower\s+shell\b"]},
    {"name": "Python", "patterns": [r"\bpython\b"]},
    {"name": "Java", "patterns": [r"\bjava\b(?!\s*script\b)"]},
    {"name": "C#", "patterns": [r"\bc#\b", r"\bc sharp\b", r"\bcsharp\b"]},
    {"name": "PostgreSQL", "patterns": [r"\bpostgresql\b", r"\bpostgres\b"]},
    {"name": "MySQL", "patterns": [r"\bmysql\b"]},
    {"name": "MongoDB", "patterns": [r"\bmongodb\b"]},
    {"name": "Oracle Database", "patterns": [r"\boracle database\b", r"\boracle sql\b"]},
    {"name": "SQL", "patterns": [r"\bsql\b"]},
    {"name": "Linux", "patterns": [r"\blinux\b"]},
    {"name": "Bash", "patterns": [r"\bbash\b"]},
    {"name": "Networking", "patterns": [r"(?<!social\s)\bnetworking\b"]},
    {"name": "Subnetting", "patterns": [r"\bsubnetting\b", r"\bsubnets?\b"]},
    {"name": "DNS", "patterns": [r"\bdns\b", r"\bdomain name system\b"]},
    {"name": "DHCP", "patterns": [r"\bdhcp\b"]},
    {"name": "TCP/IP", "patterns": [r"\btcp\s*/\s*ip\b"]},
    {"name": "Cisco", "patterns": [r"\bcisco\b"]},
    {"name": "CCNA", "patterns": [r"\bccna\b"]},
    {"name": "VPN", "patterns": [r"\bvpn\b"]},
    {"name": "Troubleshooting", "patterns": [r"\btroubleshooting\b"]},
    {"name": "Ticketing Systems", "patterns": [
        r"\bticketing systems?\b",
        r"\bticketing\b",
        r"\bservice\s*now\b",
        r"\bjira service management\b",
    ]},
    {"name": "Microsoft 365", "patterns": [r"\bmicrosoft 365\b", r"\boffice 365\b", r"\bm365\b"]},
    {"name": "Group Policy", "patterns": [r"\bgroup policy\b", r"\bgpo\b"]},
    {"name": "Intune", "patterns": [r"\bmicrosoft intune\b", r"\bintune\b"]},
    {"name": "AWS", "patterns": [r"\baws\b", r"\bamazon web services\b"]},
    {"name": "Microsoft Azure", "patterns": [
        r"\bazure\b(?!\s+active directory\b)(?!\s+ad\b)",
    ]},
    {"name": "Google Cloud", "patterns": [r"\bgoogle cloud(?: platform)?\b", r"\bgcp\b"]},
    {"name": "Cloud Services", "patterns": [
        r"\bcloud services\b",
        r"\bcloud computing\b",
        r"\bcloud platforms?\b",
    ]},
    {"name": "Cybersecurity", "patterns": [
        r"\bcybersecurity\b",
        r"\bcyber security\b",
        r"\binformation security\b",
        r"\binfosec\b",
    ]},
    {"name": "SIEM", "patterns": [r"\bsiem\b", r"\bsecurity information and event management\b"]},
    {"name": "Incident Response", "patterns": [r"\bincident response\b"]},
    {"name": "Firewall", "patterns": [r"\bfirewalls?\b"]},
    {"name": "Splunk", "patterns": [r"\bsplunk\b"]},
    {"name": "Wireshark", "patterns": [r"\bwireshark\b"]},
    {"name": "CompTIA Security+", "patterns": [r"\bcomptia security\+\b", r"\bsecurity\+\b"]},
    {"name": "CompTIA Network+", "patterns": [r"\bcomptia network\+\b", r"\bnetwork\+\b"]},
    {"name": "CompTIA A+", "patterns": [r"\bcomptia a\+\b", r"\ba\+\s+certification\b"]},
    {"name": "Docker", "patterns": [r"\bdocker\b"]},
    {"name": "Kubernetes", "patterns": [r"\bkubernetes\b", r"\bk8s\b"]},
    {"name": "Terraform", "patterns": [r"\bterraform\b"]},
    {"name": "CI/CD", "patterns": [r"\bci/cd\b", r"\bcontinuous integration\b"]},
    {"name": "Git", "patterns": [r"\bgit\b"]},
    {"name": "REST APIs", "patterns": [r"\brestful\b", r"\brest(?:ful)?\s+apis?\b"]},
    {"name": "Flask", "patterns": [r"\bflask\b"]},
    {"name": "Django", "patterns": [r"\bdjango\b"]},
    {"name": "React", "patterns": [
        r"\breact\.js\b",
        r"\breactjs\b",
        r"(?:with|using|in)\s+react\b",
    ]},
    {"name": "Node.js", "patterns": [r"\bnode\.?js\b"]},
    {"name": "HTML", "patterns": [r"\bhtml5?\b"]},
    {"name": "CSS", "patterns": [r"\bcss3?\b"]},
    {"name": "Pandas", "patterns": [r"\bpandas\b"]},
    {"name": "Tableau", "patterns": [r"\btableau\b"]},
    {"name": "Power BI", "patterns": [r"\bpower\s*bi\b"]},
    {"name": "Excel", "patterns": [r"\bmicrosoft excel\b", r"\bexcel\b"]},
    {"name": "VMware", "patterns": [r"\bvmware\b", r"\bv\s*sphere\b"]},
    {"name": "Customer Support", "patterns": [r"\bcustomer support\b", r"\bcustomer service\b"]},
    {"name": "Backup and Recovery", "patterns": [
        r"\bbackup and recovery\b",
        r"\bdisaster recovery\b",
    ]},
    {"name": "Agile", "patterns": [r"\bagile\b", r"\bscrum\b"]},
]

ALIASES = {
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "py": "Python",
    "python": "Python",
    "python3": "Python",
    "python 3": "Python",
    "java": "Java",
    "c#": "C#",
    "c sharp": "C#",
    "csharp": "C#",
    "sql": "SQL",
    "mysql": "MySQL",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "postgre": "PostgreSQL",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "oracle": "Oracle Database",
    "oracle database": "Oracle Database",
    "entra": "Microsoft Entra ID",
    "entra id": "Microsoft Entra ID",
    "microsoft entra": "Microsoft Entra ID",
    "microsoft entra id": "Microsoft Entra ID",
    "azure ad": "Microsoft Entra ID",
    "azure active directory": "Microsoft Entra ID",
    "ad": "Active Directory",
    "active directory": "Active Directory",
    "windows": "Windows",
    "windows server": "Windows Server",
    "win server": "Windows Server",
    "linux": "Linux",
    "bash": "Bash",
    "powershell": "PowerShell",
    "power shell": "PowerShell",
    "networking": "Networking",
    "subnetting": "Subnetting",
    "dns": "DNS",
    "dhcp": "DHCP",
    "tcp/ip": "TCP/IP",
    "tcpip": "TCP/IP",
    "cisco": "Cisco",
    "ccna": "CCNA",
    "vpn": "VPN",
    "troubleshooting": "Troubleshooting",
    "ticketing": "Ticketing Systems",
    "ticketing system": "Ticketing Systems",
    "ticketing systems": "Ticketing Systems",
    "servicenow": "Ticketing Systems",
    "service now": "Ticketing Systems",
    "service-now": "Ticketing Systems",
    "itsm": "Ticketing Systems",
    "m365": "Microsoft 365",
    "office 365": "Microsoft 365",
    "office365": "Microsoft 365",
    "microsoft 365": "Microsoft 365",
    "gpo": "Group Policy",
    "group policy": "Group Policy",
    "intune": "Intune",
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Microsoft Azure",
    "microsoft azure": "Microsoft Azure",
    "gcp": "Google Cloud",
    "google cloud": "Google Cloud",
    "google cloud platform": "Google Cloud",
    "cloud": "Cloud Services",
    "cloud services": "Cloud Services",
    "cloud computing": "Cloud Services",
    "cybersecurity": "Cybersecurity",
    "cyber security": "Cybersecurity",
    "information security": "Cybersecurity",
    "infosec": "Cybersecurity",
    "siem": "SIEM",
    "incident response": "Incident Response",
    "firewall": "Firewall",
    "firewalls": "Firewall",
    "splunk": "Splunk",
    "wireshark": "Wireshark",
    "security+": "CompTIA Security+",
    "comptia security+": "CompTIA Security+",
    "network+": "CompTIA Network+",
    "comptia network+": "CompTIA Network+",
    "a+": "CompTIA A+",
    "comptia a+": "CompTIA A+",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "terraform": "Terraform",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "git": "Git",
    "rest": "REST APIs",
    "rest api": "REST APIs",
    "restful": "REST APIs",
    "flask": "Flask",
    "django": "Django",
    "react": "React",
    "react.js": "React",
    "reactjs": "React",
    "node": "Node.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "html": "HTML",
    "css": "CSS",
    "pandas": "Pandas",
    "tableau": "Tableau",
    "power bi": "Power BI",
    "powerbi": "Power BI",
    "excel": "Excel",
    "vmware": "VMware",
    "vsphere": "VMware",
    "customer support": "Customer Support",
    "customer service": "Customer Support",
    "backup and recovery": "Backup and Recovery",
    "disaster recovery": "Backup and Recovery",
    "agile": "Agile",
    "scrum": "Agile",
}

PRIMARY_CATEGORY = {
    "Windows": "IT Support",
    "Troubleshooting": "IT Support",
    "Ticketing Systems": "IT Support",
    "Microsoft 365": "IT Support",
    "Customer Support": "IT Support",
    "CompTIA A+": "IT Support",
    "Excel": "Data Analytics",
    "Cybersecurity": "Cybersecurity",
    "SIEM": "Cybersecurity",
    "Incident Response": "Cybersecurity",
    "Firewall": "Cybersecurity",
    "Splunk": "Cybersecurity",
    "Wireshark": "Cybersecurity",
    "CompTIA Security+": "Cybersecurity",
    "Networking": "Networking",
    "Subnetting": "Networking",
    "DNS": "Networking",
    "DHCP": "Networking",
    "TCP/IP": "Networking",
    "Cisco": "Networking",
    "CCNA": "Networking",
    "VPN": "Networking",
    "CompTIA Network+": "Networking",
    "Python": "Software Development",
    "Java": "Software Development",
    "JavaScript": "Software Development",
    "TypeScript": "Software Development",
    "C#": "Software Development",
    "Git": "Software Development",
    "REST APIs": "Software Development",
    "Flask": "Software Development",
    "Django": "Software Development",
    "React": "Software Development",
    "Node.js": "Software Development",
    "HTML": "Software Development",
    "CSS": "Software Development",
    "CI/CD": "Software Development",
    "Docker": "Software Development",
    "Agile": "Software Development",
    "AWS": "Cloud",
    "Microsoft Azure": "Cloud",
    "Google Cloud": "Cloud",
    "Cloud Services": "Cloud",
    "Terraform": "Cloud",
    "Kubernetes": "Cloud",
    "SQL": "Database Administration",
    "MySQL": "Database Administration",
    "PostgreSQL": "Database Administration",
    "MongoDB": "Database Administration",
    "Oracle Database": "Database Administration",
    "Active Directory": "Systems Administration",
    "Windows Server": "Systems Administration",
    "Microsoft Entra ID": "Systems Administration",
    "PowerShell": "Systems Administration",
    "Group Policy": "Systems Administration",
    "Intune": "Systems Administration",
    "VMware": "Systems Administration",
    "Linux": "Systems Administration",
    "Bash": "Systems Administration",
    "Backup and Recovery": "Systems Administration",
    "Pandas": "Data Analytics",
    "Tableau": "Data Analytics",
    "Power BI": "Data Analytics",
}

_CANONICAL = {entry["name"].lower(): entry["name"] for entry in SKILL_DICTIONARY}
_CANONICAL.update(ALIASES)


def canonical_skill(raw):
    """Return the standard skill name, or a cleaned custom name."""
    cleaned = re.sub(r"\s+", " ", str(raw or "").strip())
    if not cleaned or len(cleaned) > 80:
        return None
    if not re.search(r"[A-Za-z0-9]", cleaned):
        return None
    return _CANONICAL.get(cleaned.lower(), cleaned)


def normalize_skill_list(skills):
    """Normalize names, aliases, spacing, and duplicates. Order is preserved."""
    result = []
    seen = set()
    for skill in skills or []:
        canon = canonical_skill(skill)
        if not canon:
            continue
        marker = canon.lower()
        if marker in seen:
            continue
        seen.add(marker)
        result.append(canon)
    return result


def parse_skill_text(text):
    """Split a comma, semicolon, or newline separated skill list."""
    parts = re.split(r"[\n,;]+", text or "")
    return normalize_skill_list(parts)


def extract_skills(text):
    """Find dictionary skills mentioned in a job description."""
    if not text or not str(text).strip():
        return []
    found = []
    for entry in SKILL_DICTIONARY:
        for pattern in entry["patterns"]:
            if re.search(pattern, text, flags=re.IGNORECASE):
                found.append(entry["name"])
                break
    return normalize_skill_list(found)


def suggest_category(skills):
    """Suggest one career category from the skill list. The user can change it."""
    scores = {category: 0 for category in CAREER_CATEGORIES if category != "Other"}
    for skill in normalize_skill_list(skills):
        category = PRIMARY_CATEGORY.get(skill)
        if category in scores:
            scores[category] += 1
    best_category = ""
    best_score = 0
    for category in CAREER_CATEGORIES:
        score = scores.get(category, 0)
        if score > best_score:
            best_category = category
            best_score = score
    return best_category


def match_percentage(matched_count, required_count):
    """Round half up to a whole percent. Return None when there is nothing to compare."""
    if required_count <= 0:
        return None
    value = (Decimal(matched_count) * Decimal(100)) / Decimal(required_count)
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def compare_skills(user_skills, required_skills):
    """Compare a user's skills with one job's required skill list."""
    required = normalize_skill_list(required_skills)
    owned = set(normalize_skill_list(user_skills))
    if not required:
        return {
            "percentage": None,
            "matched": [],
            "missing": [],
            "matched_count": 0,
            "required_count": 0,
        }
    matched = [skill for skill in required if skill in owned]
    missing = [skill for skill in required if skill not in owned]
    return {
        "percentage": match_percentage(len(matched), len(required)),
        "matched": matched,
        "missing": missing,
        "matched_count": len(matched),
        "required_count": len(required),
    }


def rank_jobs(jobs, user_skills):
    """Rank saved jobs by match percentage. Jobs without skills sort last."""
    ranked = []
    for job in jobs:
        requirements = job.get("requirements") or {}
        comparison = compare_skills(user_skills, requirements.get("required_skills") or [])
        ranked.append({
            "job_id": job.get("job_id"),
            "job_title": job.get("job_title") or "",
            "company_name": job.get("company_name") or "",
            "job_type": job.get("job_type") or "",
            "career_category": requirements.get("career_category") or "",
            **comparison,
        })
    ranked.sort(key=lambda item: (
        item["percentage"] is None,
        -(item["percentage"] if item["percentage"] is not None else 0),
        item["job_title"].lower(),
    ))
    return ranked
