"""Local qualification guidance. Edit this file to change the advice.

Nothing in this module calls a paid API. Skills that are not listed receive
an honest generic suggestion from guidance_for().
"""

CERT_DISCLAIMER = (
    "A certification can organize your study. It does not guarantee an interview, "
    "a job offer, or employment."
)

RECOMMENDATIONS = {
    "Active Directory": {
        "guidance": "Create a Windows Server lab and practice managing users, security groups, permissions, and password resets. Disable a test account and confirm the user can no longer sign in.",
        "links": [{
            "label": "Microsoft Learn: Active Directory Domain Services",
            "url": "https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview",
        }],
    },
    "Microsoft Entra ID": {
        "guidance": "In a Microsoft Learn sandbox or a trial tenant, create a user, add that user to a group, and turn on multi-factor authentication. Then explain the difference between this cloud directory and on-premises Active Directory.",
        "links": [{
            "label": "Microsoft Learn: What is Microsoft Entra ID?",
            "url": "https://learn.microsoft.com/en-us/entra/fundamentals/what-is-entra",
        }],
    },
    "Windows": {
        "guidance": "Install Windows in a virtual machine. Create a local account, install updates, map a drive, and troubleshoot one network or startup problem from the error message back to the fix.",
        "links": [{
            "label": "Microsoft Learn training",
            "url": "https://learn.microsoft.com/en-us/training/",
        }],
    },
    "Windows Server": {
        "guidance": "Install Windows Server in a lab and add one role, such as file sharing or DNS. Create a share, set permissions, and practice restarting the service after a change.",
        "links": [{
            "label": "Microsoft Learn: Get started with Windows Server",
            "url": "https://learn.microsoft.com/en-us/windows-server/get-started/get-started-with-windows-server",
        }],
    },
    "Linux": {
        "guidance": "Install Linux in a virtual machine. Practice command-line navigation, file permissions, user accounts, and starting or stopping a service.",
        "links": [{
            "label": "Ubuntu Desktop download",
            "url": "https://ubuntu.com/download/desktop",
        }],
    },
    "Bash": {
        "guidance": "Write a short Bash script that accepts a folder path, lists the files, and copies matching files to a backup folder. Run it on a Linux virtual machine.",
        "links": [{
            "label": "GNU Bash manual",
            "url": "https://www.gnu.org/software/bash/manual/",
        }],
    },
    "PowerShell": {
        "guidance": "On a Windows lab machine, use PowerShell to list local users, export the result to a file, and restart a service. Save the commands in a script you can run again.",
        "links": [{
            "label": "Microsoft Learn: PowerShell 101",
            "url": "https://learn.microsoft.com/en-us/powershell/scripting/learn/ps101/01-getting-started",
        }],
    },
    "Networking": {
        "guidance": "Practice subnetting on paper, then configure DNS, DHCP, and a basic router or switch in a lab such as Cisco Packet Tracer.",
        "links": [
            {"label": "Cisco Skills for All", "url": "https://skillsforall.com/"},
            {"label": "Cisco Networking Academy", "url": "https://www.netacad.com/"},
        ],
    },
    "Subnetting": {
        "guidance": "Calculate network, broadcast, and usable host addresses for several prefixes, including /24, /26, and /27. Check the work with a subnet calculator only after you finish by hand.",
        "links": [{"label": "Cisco Skills for All", "url": "https://skillsforall.com/"}],
    },
    "DNS": {
        "guidance": "Draw the lookup from a name to an IP address. In a lab, create an A record and confirm the client resolves it.",
        "links": [{"label": "Cisco Networking Academy", "url": "https://www.netacad.com/"}],
    },
    "DHCP": {
        "guidance": "Configure a DHCP scope in a lab, add a reservation for one device, and renew the client lease so you can see the address change or stay reserved.",
        "links": [{"label": "Cisco Networking Academy", "url": "https://www.netacad.com/"}],
    },
    "TCP/IP": {
        "guidance": "Practice IP addressing and subnet masks, then use ping and tracert or traceroute to show where a connection stops.",
        "links": [{"label": "Cisco Skills for All", "url": "https://skillsforall.com/"}],
    },
    "Cisco": {
        "guidance": "In Packet Tracer or a router lab, configure hostnames, interfaces, and a simple route. Save the config and reload the device to prove it persists.",
        "links": [{"label": "Cisco Networking Academy", "url": "https://www.netacad.com/"}],
    },
    "CCNA": {
        "guidance": "Study the current official CCNA objectives and lab the configuration topics: switching, routing, IP services, and basic security. Passing the exam shows baseline knowledge; it does not guarantee a job.",
        "links": [{
            "label": "Cisco CCNA certification",
            "url": "https://www.cisco.com/c/en/us/training-events/training-certifications/certifications/associate/ccna.html",
        }],
    },
    "VPN": {
        "guidance": "Set up a lab VPN or review a remote-access design and explain what is encrypted, how a user authenticates, and what happens when the tunnel drops.",
        "links": [{"label": "Cisco Networking Academy", "url": "https://www.netacad.com/"}],
    },
    "Troubleshooting": {
        "guidance": "Use a written process: record the symptom, test one likely cause, change one thing, and document the result. Repeat on three sample support problems.",
        "links": [{"label": "CompTIA certifications", "url": "https://www.comptia.org/en-us/certifications/"}],
    },
    "Ticketing Systems": {
        "guidance": "Practice creating a ticket, setting the priority, writing what the user reported, recording the steps you tried, and closing it with the resolution.",
        "links": [],
    },
    "Customer Support": {
        "guidance": "Practice a five-minute support call: confirm the problem in the user's words, set an expectation, give one clear next step, and write the same facts in a ticket.",
        "links": [],
    },
    "Microsoft 365": {
        "guidance": "In a Microsoft 365 trial or Learn sandbox, create a user, assign a license, reset the sign-in, and find the mailbox or OneDrive for that account.",
        "links": [{
            "label": "Microsoft Learn: Microsoft 365",
            "url": "https://learn.microsoft.com/en-us/microsoft-365/",
        }],
    },
    "Group Policy": {
        "guidance": "In an Active Directory lab, create a test organizational unit, link a Group Policy object, and apply one setting such as a password rule. Confirm the client received the policy.",
        "links": [{
            "label": "Microsoft Learn: Group Policy overview",
            "url": "https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-policy/group-policy-overview",
        }],
    },
    "Intune": {
        "guidance": "Use a Microsoft endpoint management lab to enroll one device and assign one configuration or compliance policy. Check the device status and retire the enrollment when you finish.",
        "links": [{
            "label": "Microsoft Learn: Microsoft Intune",
            "url": "https://learn.microsoft.com/en-us/mem/intune/",
        }],
    },
    "SQL": {
        "guidance": "Practice SELECT, JOIN, GROUP BY, INSERT, UPDATE, and DELETE on a sample database. Write each statement against a copy of the data, not a database you cannot restore.",
        "links": [{"label": "MySQL documentation", "url": "https://dev.mysql.com/doc/"}],
    },
    "MySQL": {
        "guidance": "Install MySQL, load a sample schema, and practice joins plus a filtered UPDATE. Create a backup and restore it into a second schema.",
        "links": [{"label": "MySQL documentation", "url": "https://dev.mysql.com/doc/"}],
    },
    "PostgreSQL": {
        "guidance": "Install PostgreSQL and complete the official tutorial queries. Then add one table, insert rows, and join it back to the tutorial data.",
        "links": [{
            "label": "PostgreSQL tutorial",
            "url": "https://www.postgresql.org/docs/current/tutorial.html",
        }],
    },
    "MongoDB": {
        "guidance": "Follow the official getting-started tutorial to insert, find, update, and delete documents. Then explain when a document model is a poor fit compared with SQL tables.",
        "links": [{
            "label": "MongoDB getting started",
            "url": "https://www.mongodb.com/docs/manual/tutorial/getting-started/",
        }],
    },
    "Oracle Database": {
        "guidance": "Use Oracle's database documentation to connect to a sample schema and run SELECT, JOIN, INSERT, UPDATE, and DELETE statements.",
        "links": [{
            "label": "Oracle Database documentation",
            "url": "https://docs.oracle.com/en/database/oracle/oracle-database/",
        }],
    },
    "Python": {
        "guidance": "Develop small automation scripts: read a CSV, rename a batch of files, or check whether a list of hosts responds. Keep the scripts in a folder you can explain line by line.",
        "links": [{"label": "Python tutorial", "url": "https://docs.python.org/3/tutorial/"}],
    },
    "Java": {
        "guidance": "Write a small Java program that reads input, stores objects in a list, and prints a result. Build it from the command line so you understand the source file, compiler, and runtime.",
        "links": [{"label": "Learn Java", "url": "https://dev.java/learn/"}],
    },
    "JavaScript": {
        "guidance": "Build a one-page script that reads form input, validates it, and updates the page. Then explain how that browser script differs from Java.",
        "links": [{
            "label": "MDN JavaScript Guide",
            "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
        }],
    },
    "TypeScript": {
        "guidance": "Retype a small JavaScript example with TypeScript types for the function inputs and return value. Fix the compiler errors before running it.",
        "links": [{
            "label": "TypeScript documentation",
            "url": "https://www.typescriptlang.org/docs/",
        }],
    },
    "C#": {
        "guidance": "Write a console program that reads a text file, filters the lines, and writes a report. Practice classes and a list before adding a framework.",
        "links": [{
            "label": "Microsoft Learn training",
            "url": "https://learn.microsoft.com/en-us/training/",
        }],
    },
    "Git": {
        "guidance": "Create a repository, make two commits, create a branch, and merge it. Inspect the history and recover a file from the earlier commit.",
        "links": [{"label": "Git documentation", "url": "https://git-scm.com/doc"}],
    },
    "HTML": {
        "guidance": "Build a simple page with a heading, a form, a table, and labels tied to each input. Check that a screen reader can reach every control.",
        "links": [{
            "label": "MDN HTML",
            "url": "https://developer.mozilla.org/en-US/docs/Web/HTML",
        }],
    },
    "CSS": {
        "guidance": "Style one page with a readable font, spacing, and a layout that works on a narrow screen. Use the browser inspector to see which rule wins.",
        "links": [{
            "label": "MDN CSS",
            "url": "https://developer.mozilla.org/en-US/docs/Web/CSS",
        }],
    },
    "REST APIs": {
        "guidance": "Call a public read-only API with a documented HTTP GET, then write one endpoint of your own that returns JSON for a list and for a single item.",
        "links": [{
            "label": "MDN: HTTP overview",
            "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP",
        }],
    },
    "Flask": {
        "guidance": "Build a three-route Flask app that lists records, shows one record, and accepts a validated form. Keep the database password out of the source code.",
        "links": [{
            "label": "Flask documentation",
            "url": "https://flask.palletsprojects.com/",
        }],
    },
    "Django": {
        "guidance": "Complete the official writing-your-first-Django-app tutorial through models, views, and the admin. Compare that structure with the Flask app you are using here.",
        "links": [{
            "label": "Django documentation",
            "url": "https://docs.djangoproject.com/en/stable/intro/tutorial01/",
        }],
    },
    "React": {
        "guidance": "Build a component that lists items, adds an item from a form, and filters the list. Keep the state in one place and check the official learn guide when the UI gets out of sync.",
        "links": [{"label": "React learn guide", "url": "https://react.dev/learn"}],
    },
    "Node.js": {
        "guidance": "Write a Node.js script that reads a JSON file and prints a summary. Then create one HTTP route that returns that summary.",
        "links": [{"label": "Node.js learn", "url": "https://nodejs.org/en/learn"}],
    },
    "Docker": {
        "guidance": "Follow the official getting-started guide to build an image, run a container, and remove it. Note which files the image copies and which port it publishes.",
        "links": [{"label": "Docker getting started", "url": "https://docs.docker.com/get-started/"}],
    },
    "Kubernetes": {
        "guidance": "Complete the official Kubernetes basics tutorial. Deploy the sample application, scale it, and then delete the deployment so the lab does not keep running.",
        "links": [{
            "label": "Kubernetes basics",
            "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/",
        }],
    },
    "Terraform": {
        "guidance": "Complete an official Terraform tutorial that creates one resource, changes it, and destroys it. Read the plan before you apply it.",
        "links": [{
            "label": "Terraform tutorials",
            "url": "https://developer.hashicorp.com/terraform/tutorials",
        }],
    },
    "CI/CD": {
        "guidance": "Put a small project in Git and add one workflow that installs dependencies and runs tests on every push. Read a failed log and fix the command.",
        "links": [{"label": "Git documentation", "url": "https://git-scm.com/doc"}],
    },
    "AWS": {
        "guidance": "Complete an official AWS hands-on tutorial that creates one service, checks that it works, and deletes it. Watch the billing page before and after.",
        "links": [
            {"label": "AWS documentation", "url": "https://docs.aws.amazon.com/"},
            {"label": "AWS Skill Builder", "url": "https://skillbuilder.aws/"},
        ],
    },
    "Microsoft Azure": {
        "guidance": "Complete a Microsoft Learn module that creates a resource group and one resource, then delete the resource group. Record what each resource costs in the lab.",
        "links": [{
            "label": "Microsoft Learn: Azure training",
            "url": "https://learn.microsoft.com/en-us/training/browse/?products=azure",
        }],
    },
    "Google Cloud": {
        "guidance": "Follow a Google Cloud quickstart to create one resource, view its logs, and delete the project or resource when the exercise ends.",
        "links": [{"label": "Google Cloud documentation", "url": "https://cloud.google.com/docs"}],
    },
    "Cloud Services": {
        "guidance": "Pick one provider and deploy a single small resource. Identify the region, identity, network, storage, and how you will shut it down.",
        "links": [{"label": "Microsoft Learn training", "url": "https://learn.microsoft.com/en-us/training/"}],
    },
    "Cybersecurity": {
        "guidance": "Use safe beginner labs that cover logs, security fundamentals, and incident response. Practice only on systems you own or that a lab provider gives you permission to use.",
        "links": [{
            "label": "CompTIA Security+",
            "url": "https://www.comptia.org/en-us/certifications/security/",
        }],
    },
    "SIEM": {
        "guidance": "Import sample logs into a lab SIEM or a log viewer and write a search that finds failed sign-ins. Describe one alert you would investigate and one you would tune.",
        "links": [{"label": "Splunk documentation", "url": "https://docs.splunk.com/Documentation"}],
    },
    "Splunk": {
        "guidance": "Use Splunk's documentation to load sample data and run a search that counts events by sourcetype or host. Save the search and explain the result.",
        "links": [{"label": "Splunk documentation", "url": "https://docs.splunk.com/Documentation"}],
    },
    "Wireshark": {
        "guidance": "Capture traffic on your own lab machine, filter for DNS, and identify the query and response. Do not capture other people's traffic.",
        "links": [{"label": "Wireshark documentation", "url": "https://www.wireshark.org/docs/"}],
    },
    "Firewall": {
        "guidance": "On a lab firewall or host firewall, write one allow rule and one deny rule. Test both with a connection attempt and record which ports were involved.",
        "links": [{"label": "Cisco Networking Academy", "url": "https://www.netacad.com/"}],
    },
    "Incident Response": {
        "guidance": "Walk through a sample incident on paper: detect, contain, eradicate, recover, and write the lessons learned. Use logs you are allowed to read.",
        "links": [{
            "label": "CompTIA Security+",
            "url": "https://www.comptia.org/en-us/certifications/security/",
        }],
    },
    "CompTIA A+": {
        "guidance": "Study the current official A+ objectives and practice the support tasks they list: hardware, operating systems, and troubleshooting. The certificate is evidence of study, not a job offer.",
        "links": [{
            "label": "CompTIA A+",
            "url": "https://www.comptia.org/en-us/certifications/a/",
        }],
    },
    "CompTIA Network+": {
        "guidance": "Study the current official Network+ objectives and lab the fundamentals: media, addressing, DNS, DHCP, and troubleshooting. The certificate does not guarantee employment.",
        "links": [{
            "label": "CompTIA Network+",
            "url": "https://www.comptia.org/en-us/certifications/network/",
        }],
    },
    "CompTIA Security+": {
        "guidance": "Study the current official Security+ objectives and practice the basics in a legal lab: threats, secure configuration, and incident response concepts. The certificate does not guarantee employment.",
        "links": [{
            "label": "CompTIA Security+",
            "url": "https://www.comptia.org/en-us/certifications/security/",
        }],
    },
    "VMware": {
        "guidance": "Use VMware's documentation to create a virtual machine, take a snapshot, change the guest, and revert the snapshot.",
        "links": [{"label": "VMware documentation", "url": "https://docs.vmware.com/"}],
    },
    "Backup and Recovery": {
        "guidance": "Back up a sample database or a folder, delete a test record or file, and restore only that item. Time the restore and write down the steps.",
        "links": [{"label": "MySQL documentation", "url": "https://dev.mysql.com/doc/"}],
    },
    "Pandas": {
        "guidance": "Load a CSV with pandas, filter rows, group by one column, and write the summary to a new file. Be able to explain each line without reading it aloud from memory.",
        "links": [{
            "label": "pandas getting started",
            "url": "https://pandas.pydata.org/docs/getting_started/index.html",
        }],
    },
    "Tableau": {
        "guidance": "Use Tableau's training to connect a sample spreadsheet, build one chart, and add a filter. State what question the chart answers.",
        "links": [{"label": "Tableau training", "url": "https://www.tableau.com/learn"}],
    },
    "Power BI": {
        "guidance": "In Power BI Desktop, import a spreadsheet, create a relationship if there are two tables, and publish one report page with a slicer.",
        "links": [{
            "label": "Microsoft Learn: Power BI",
            "url": "https://learn.microsoft.com/en-us/power-bi/",
        }],
    },
    "Excel": {
        "guidance": "Clean a sample sheet with tables, filters, and one formula such as SUMIF or XLOOKUP. Then build a pivot table that answers a specific question.",
        "links": [{"label": "Excel help", "url": "https://support.microsoft.com/excel"}],
    },
    "Agile": {
        "guidance": "Write three small user stories with acceptance checks. Plan them into a one-week practice sprint, finish one, and note what you would change next time.",
        "links": [],
    },
}

CERTIFICATIONS = [
    {
        "name": "CompTIA A+",
        "why": "It is useful for entry-level IT support because it covers hardware, operating systems, troubleshooting, and how support work is done. It does not guarantee a job.",
        "url": "https://www.comptia.org/en-us/certifications/a/",
        "related_skills": [
            "Windows",
            "Troubleshooting",
            "Ticketing Systems",
            "Customer Support",
            "CompTIA A+",
        ],
    },
    {
        "name": "CompTIA Network+",
        "why": "It is useful when a role requires networking fundamentals such as addressing, DNS, DHCP, and network troubleshooting. It does not guarantee a job.",
        "url": "https://www.comptia.org/en-us/certifications/network/",
        "related_skills": [
            "Networking",
            "DNS",
            "DHCP",
            "TCP/IP",
            "Subnetting",
            "VPN",
            "CompTIA Network+",
        ],
    },
    {
        "name": "CompTIA Security+",
        "why": "It is useful for foundational cybersecurity knowledge, including threats, secure configuration, and incident response concepts. It does not guarantee a job.",
        "url": "https://www.comptia.org/en-us/certifications/security/",
        "related_skills": [
            "Cybersecurity",
            "SIEM",
            "Firewall",
            "Incident Response",
            "CompTIA Security+",
        ],
    },
    {
        "name": "Cisco CCNA",
        "why": "It is relevant when a job specifically asks for Cisco networking, because the exam focuses on configuring and troubleshooting those networks. It does not guarantee a job.",
        "url": "https://www.cisco.com/c/en/us/training-events/training-certifications/certifications/associate/ccna.html",
        "related_skills": ["Cisco", "CCNA"],
    },
]


def guidance_for(skill):
    """Return curated advice, or an honest generic plan when none is stored."""
    item = RECOMMENDATIONS.get(skill)
    if not item:
        return {
            "skill": skill,
            "guidance": (
                f"There is no curated practice plan for {skill} in this application. "
                "Find current official documentation or training for this skill, practice it "
                "in a small lab or sample project, and write down the tasks you completed."
            ),
            "links": [],
        }
    return {"skill": skill, "guidance": item["guidance"], "links": item["links"]}


def certifications_for_missing(missing_skills):
    """Recommend a certification only when a related required skill is missing."""
    missing = set(missing_skills or [])
    selected = []
    for cert in CERTIFICATIONS:
        overlap = [skill for skill in cert["related_skills"] if skill in missing]
        if overlap:
            selected.append({
                "name": cert["name"],
                "why": cert["why"],
                "url": cert["url"],
                "because": overlap,
            })
    return selected


def qualification_plan(missing_skills):
    return {
        "skills": [guidance_for(skill) for skill in missing_skills],
        "certifications": certifications_for_missing(missing_skills),
    }
