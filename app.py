
import hashlib
from datetime import datetime
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Cyber Evidence | Investigation Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------
# Theme
# ---------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
  --bg:#050914;
  --panel:#0b1425;
  --panel2:#0e1a2e;
  --text:#edf5ff;
  --muted:#91a2b9;
  --cyan:#38d9ff;
  --blue:#5865ff;
  --green:#46e0a1;
  --line:#172338;
}

.stApp {
  background:
    radial-gradient(circle at 80% 0%, rgba(56,217,255,.10), transparent 28%),
    radial-gradient(circle at 5% 20%, rgba(88,101,255,.08), transparent 30%),
    var(--bg);
  color:var(--text);
}
.block-container {max-width:1200px; padding-top:2rem; padding-bottom:3rem;}
h1,h2,h3 {font-family:"Space Grotesk",sans-serif !important;}
.hero {
  padding: 4rem 0 3rem;
}
.eyebrow {
  color:#38d9ff;
  text-transform:uppercase;
  letter-spacing:2px;
  font-size:.72rem;
  font-weight:800;
}
.gradient {
  background:linear-gradient(90deg,#fff,#38d9ff,#8b98ff);
  -webkit-background-clip:text;
  color:transparent;
}
.subtitle {color:#91a2b9;font-size:1.05rem;max-width:760px;}
.card {
  background:linear-gradient(180deg,#0e1a2e,#09121f);
  border:1px solid #172338;
  border-radius:16px;
  padding:1.2rem;
  min-height:130px;
}
.card-title {font-weight:700;font-size:1.05rem;}
.card-text {color:#8193aa;font-size:.88rem;margin-top:.4rem;}
.kpi {
  background:#0b1425;
  border:1px solid #172338;
  border-radius:14px;
  padding:1rem;
}
.kpi small {color:#71869f;}
.kpi strong {display:block;font-size:1.8rem;margin-top:.25rem;}
.notice {
  background:#091a2a;
  border:1px solid #23415a;
  border-radius:12px;
  padding:1rem;
  color:#91a2b9;
}
.small-muted {color:#71869f;font-size:.82rem;}
[data-testid="stSidebar"] {
  background:#07101d;
  border-right:1px solid #172338;
}
[data-testid="stSidebar"] h2 {font-size:1.1rem;}
button[kind="primary"] {
  background:linear-gradient(135deg,#38d9ff,#5865ff) !important;
  color:#03101c !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Demo data
# ---------------------------
cases = [
    {"id":"CASE-2026-014","title":"Digital Fraud Investigation","type":"Fraud","description":"Demo cyber-fraud investigation case.","priority":"High","status":"Active","created_by":"Investigator01","created_date":"28-09-2026"},
    {"id":"CASE-2026-011","title":"Unauthorized Account Access","type":"Access","description":"Demo unauthorized account access case.","priority":"Medium","status":"Closed","created_by":"Investigator01","created_date":"25-09-2026"},
    {"id":"CASE-2026-009","title":"Suspicious Network Activity","type":"Network","description":"Demo suspicious network activity case.","priority":"High","status":"Active","created_by":"ForensicAnalyst01","created_date":"22-09-2026"},
]

evidence = [
    {"id":"EVD-001","case":"CASE-2026-014","type":"Document","source":"Sample Source A","collector":"Investigator01","hash":"Recorded SHA-256","status":"Verified"},
    {"id":"EVD-002","case":"CASE-2026-014","type":"Image","source":"Sample Source B","collector":"Investigator01","hash":"Recorded SHA-256","status":"Verified"},
]

custody = [
    ["EVD-001","Investigator01","ForensicAnalyst01","26-09-2026 11:30","Authorized forensic examination","LAB-01 / Evidence Locker A"],
    ["EVD-002","Investigator01","Custodian01","27-09-2026 14:15","Secure storage","LAB-01 / Evidence Locker B"],
]

audit = [
    ["28-09-2026 09:10","admin","LOGIN","User","USR-001"],
    ["28-09-2026 09:22","Investigator01","CREATE_CASE","Case","CASE-2026-014"],
    ["28-09-2026 09:31","Investigator01","REGISTER_EVIDENCE","Evidence","EVD-001"],
    ["28-09-2026 09:42","ForensicAnalyst01","HASH_VERIFY","Evidence","EVD-001"],
]

# Keep records in the Streamlit session so newly created cases remain visible
# while the app session is open. This can later be replaced by a database.
if "cases" not in st.session_state:
    st.session_state.cases = cases.copy()
if "audit" not in st.session_state:
    st.session_state.audit = audit.copy()

# ---------------------------
# Helpers
# ---------------------------
def card(title, text, icon=""):
    st.markdown(
        f'<div class="card"><div class="card-title">{icon} {title}</div>'
        f'<div class="card-text">{text}</div></div>',
        unsafe_allow_html=True
    )

def page_header(label, title, description=""):
    st.markdown(f'<div class="eyebrow">{label}</div>', unsafe_allow_html=True)
    st.title(title)
    if description:
        st.markdown(f'<p class="subtitle">{description}</p>', unsafe_allow_html=True)

# ---------------------------
# Session state
# ---------------------------
if "page" not in st.session_state:
    st.session_state.page = "Landing"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = "Administrator"

# ---------------------------
# Sidebar
# ---------------------------
with st.sidebar:
    st.markdown("## 🛡️ CYBER EVIDENCE")
    st.caption("Investigation & Evidence Management")
    st.divider()

    if not st.session_state.logged_in:
        st.markdown("### Public Pages")
        pages = ["Landing", "Features", "Workflow", "Architecture", "Team", "Login / Demo"]
    else:
        st.markdown("### Secure Workspace")
        pages = ["Dashboard", "Cases", "Evidence", "Chain of Custody", "Reports", "Audit Logs", "Landing"]

    current_index = pages.index(st.session_state.page) if st.session_state.page in pages else 0
    selected = st.radio("Navigate", pages, index=current_index)
    st.session_state.page = selected

    st.divider()
    if st.session_state.logged_in:
        st.success(f"Logged in as {st.session_state.role}")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.page = "Landing"
            st.rerun()

# ---------------------------
# Landing
# ---------------------------
if st.session_state.page == "Landing":
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">Controlled Digital-Forensics Platform</div>', unsafe_allow_html=True)
    st.markdown('<h1>Secure evidence.<br><span class="gradient">Strengthen investigations.</span></h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">A centralized Cybercrime Investigation & Evidence Management System '
        'for organizing cases, documenting digital evidence, checking SHA-256 integrity, '
        'tracking chain of custody, recording investigation activities and generating structured reports.</p>',
        unsafe_allow_html=True
    )
    c1, c2 = st.columns([1,1])
    with c1:
        if st.button("Explore Platform →", type="primary", use_container_width=True):
            st.session_state.page = "Login / Demo"
            st.rerun()
    with c2:
        if st.button("See How It Works", use_container_width=True):
            st.session_state.page = "Workflow"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### Platform overview")
    cols = st.columns(3)
    for col, title, value, color in zip(
        cols,
        ["Active Cases","Evidence Items","Integrity"],
        ["24","186","100%"],
        ["cyan","white","green"]
    ):
        with col:
            st.markdown(f'<div class="kpi"><small>{title.upper()}</small><strong class="{color}">{value}</strong></div>', unsafe_allow_html=True)

    st.markdown("### Why this platform")
    cols = st.columns(3)
    items = [
        ("Centralized Records","Manage cases, evidence metadata, activities and findings in one structured application.","📁"),
        ("Evidence Integrity","Record and compare SHA-256 values for controlled sample evidence.","#️⃣"),
        ("Traceable Custody","Maintain chronological evidence handling and transfer records.","🔗"),
    ]
    for col, item in zip(cols, items):
        with col:
            card(*item)

# ---------------------------
# Features
# ---------------------------
elif st.session_state.page == "Features":
    page_header("Core Capabilities","Everything investigators need to document the workflow.",
                "Click a capability to inspect what it does.")
    features = [
        ("Authentication & RBAC","Secure login and role-based permissions.","🔐"),
        ("Case Management","Create, assign, update, search and close investigation cases.","📁"),
        ("Evidence Registration","Unique identifiers, metadata, source, collector and storage reference.","🧾"),
        ("SHA-256 Verification","Record and compare SHA-256 values for controlled sample evidence.","#️⃣"),
        ("Chain of Custody","Record evidence transfers and handling history.","🔗"),
        ("Investigation Timeline","Document activities, observations and findings with timestamps.","🕒"),
        ("Audit Logging","Record important system actions for accountability.","🛡️"),
        ("Reports & Search","Search, filter and generate structured reports.","📊"),
    ]
    cols = st.columns(4)
    for i, item in enumerate(features):
        with cols[i % 4]:
            if st.button(f"{item[2]} {item[0]}", key=f"feature_{i}", use_container_width=True):
                st.info(item[1])

# ---------------------------
# Workflow
# ---------------------------
elif st.session_state.page == "Workflow":
    page_header("Investigation Workflow","From login to case closure.",
                "The documented workflow keeps investigation records organized and evidence handling traceable.")
    steps = [
        ("01","Login","Authenticate user"),("02","Permissions","Check role access"),
        ("03","Case","Create or select"),("04","Evidence","Register metadata"),
        ("05","Integrity","Record SHA-256"),("06","Custody","Track transfers"),
        ("07","Activities","Record findings"),("08","Verify","Check integrity"),
        ("09","Report","Generate output"),("10","Close","Complete workflow"),
    ]
    cols = st.columns(5)
    for i,(n,t,d) in enumerate(steps):
        with cols[i % 5]:
            st.markdown(f'<div class="card"><div class="eyebrow">{n}</div><b>{t}</b><div class="card-text">{d}</div></div>', unsafe_allow_html=True)
        if i % 5 == 4:
            st.write("")

# ---------------------------
# Architecture
# ---------------------------
elif st.session_state.page == "Architecture":
    page_header("System Architecture","Three layers. One controlled workflow.")
    cols = st.columns(4)
    layers = [
        ("Web Interface","Login, dashboard, case screens, evidence screens and reports."),
        ("Backend / API","Business rules, authentication, permissions, hashing and custody workflows."),
        ("Database","Users, cases, evidence metadata, custody events, activities and audit logs."),
        ("Controlled Storage","Controlled storage/reference for authorized sample evidence."),
    ]
    for col,(t,d) in zip(cols,layers):
        with col:
            card(t,d,"▣")
    st.markdown("### Architecture flow")
    st.code("Users → Web Interface → Backend/API → Authentication & Authorization → Case/Evidence/Custody Services → Database + Controlled Evidence Storage")

# ---------------------------
# Team
# ---------------------------
elif st.session_state.page == "Team":
    page_header("Project Team","Four members. One investigation platform.",
                "Academic Year 2026–2027")
    team = [
        ("Vanga Kalyani","Backend & Authentication","API/backend, login, RBAC, user management"),
        ("Sunkara Savithri","Evidence & Integrity","Evidence module, metadata, SHA-256 verification"),
        ("Gadula Baby Sri","Database, Custody & Audit","Database, chain of custody, audit logging"),
        ("Pasalapudi Rajitha","Frontend, Reports & Testing","UI, dashboard, reports, testing and documentation"),
    ]
    for name,role,work in team:
        with st.expander(f"{name} — {role}"):
            st.write(work)

# ---------------------------
# Login
# ---------------------------
elif st.session_state.page == "Login / Demo":
    page_header("Authorized Access","Secure Demo Login",
                "This Streamlit prototype uses synthetic demo data and does not collect real credentials.")
    with st.form("login_form"):
        email = st.text_input("Email", value="admin@cyberevidence.local")
        password = st.text_input("Password", value="admin123", type="password")
        role = st.selectbox("Role", ["Administrator","Investigator","Forensic Analyst","Evidence Custodian","Supervisor"])
        submitted = st.form_submit_button("Enter Dashboard →", type="primary")
    st.markdown('<div class="notice">Demo credentials: <b>admin@cyberevidence.local</b> / <b>admin123</b></div>', unsafe_allow_html=True)
    if submitted:
        if email and password:
            st.session_state.logged_in = True
            st.session_state.role = role
            st.session_state.page = "Dashboard"
            st.rerun()
        else:
            st.error("Enter the demo email and password.")

# Secure pages require login
elif not st.session_state.logged_in:
    st.warning("Please use Login / Demo first.")
    if st.button("Go to Login", type="primary"):
        st.session_state.page = "Login / Demo"
        st.rerun()

# ---------------------------
# Dashboard
# ---------------------------
elif st.session_state.page == "Dashboard":
    page_header("Secure Workspace","Investigation Dashboard",
                f"Role: {st.session_state.role}")
    cols = st.columns(4)
    for col,title,value in zip(cols,["Active Cases","Evidence Items","Verified Hashes","Audit Events"],["24","186","100%","428"]):
        with col:
            st.markdown(f'<div class="kpi"><small>{title.upper()}</small><strong>{value}</strong></div>',unsafe_allow_html=True)
    st.markdown("### Modules")
    cols=st.columns(3)
    modules=[("Cases","Cases"),("Evidence","Evidence"),("Chain of Custody","Chain of Custody"),("Reports","Reports"),("Audit Logs","Audit Logs")]
    for col,(title,page) in zip(cols*2,modules):
        with col:
            if st.button(title, key=f"dash_{page}", use_container_width=True):
                st.session_state.page=page
                st.rerun()
    st.markdown('<div class="notice">Prototype note: all dashboard records are synthetic demonstration data.</div>',unsafe_allow_html=True)

# ---------------------------
# Cases
# ---------------------------
elif st.session_state.page == "Cases":
    page_header("Case Management","Investigation Cases","Create, search and inspect cybercrime investigation case records.")

    # Create Case form
    with st.expander("➕ Create New Case", expanded=False):
        with st.form("create_case_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                case_id = st.text_input("Case ID *", value=f"CASE-2026-{len(st.session_state.cases)+15:03d}")
                title = st.text_input("Title *", placeholder="e.g., Online Payment Fraud Investigation")
                case_type = st.selectbox("Type *", ["Fraud", "Phishing", "Unauthorized Access", "Cyber Harassment", "Network", "Malware", "Data Theft", "Other"])
                priority = st.selectbox("Priority *", ["Low", "Medium", "High", "Critical"], index=1)
            with c2:
                status = st.selectbox("Status *", ["Active", "Pending", "On Hold", "Closed"], index=0)
                created_by = st.text_input("Created By *", value=st.session_state.get("username", "Investigator01"))
                created_date = st.date_input("Created Date *", value=datetime.now().date())
                description = st.text_area("Description *", placeholder="Enter a short description of the cybercrime case.")

            submitted = st.form_submit_button("Create Case", type="primary", use_container_width=True)

            if submitted:
                # Basic validation
                required = {
                    "Case ID": case_id.strip(), "Title": title.strip(),
                    "Created By": created_by.strip(), "Description": description.strip()
                }
                missing = [name for name, value in required.items() if not value]
                duplicate = any(x["id"].lower() == case_id.strip().lower() for x in st.session_state.cases)

                if missing:
                    st.error("Please fill the required fields: " + ", ".join(missing) + ".")
                elif duplicate:
                    st.error(f"Case ID {case_id.strip()} already exists. Please use a unique Case ID.")
                else:
                    new_case = {
                        "id": case_id.strip(),
                        "title": title.strip(),
                        "type": case_type,
                        "description": description.strip(),
                        "priority": priority,
                        "status": status,
                        "created_by": created_by.strip(),
                        "created_date": created_date.strftime("%d-%m-%Y"),
                    }
                    st.session_state.cases.insert(0, new_case)
                    st.session_state.audit.insert(0, [
                        datetime.now().strftime("%d-%m-%Y %H:%M"),
                        created_by.strip(), "CREATE_CASE", "Case", case_id.strip()
                    ])
                    st.session_state.case_created = case_id.strip()
                    st.rerun()

    if st.session_state.get("case_created"):
        st.success(f"Case {st.session_state.case_created} created successfully and added to the case records.")
        st.session_state.case_created = None

    q=st.text_input("Search cases",placeholder="CASE-2026-014, fraud, active...")
    filtered=[x for x in st.session_state.cases if q.lower() in " ".join(str(v) for v in x.values()).lower()] if q else st.session_state.cases

    display_cases = [
        {
            "Case ID": x["id"], "Title": x["title"], "Type": x["type"],
            "Priority": x["priority"], "Status": x["status"],
            "Created By": x["created_by"], "Created Date": x["created_date"]
        } for x in filtered
    ]
    st.dataframe(display_cases, use_container_width=True, hide_index=True)

    if filtered:
        selected_id = st.selectbox("Inspect case", [x["id"] for x in filtered])
        selected = next(x for x in filtered if x["id"] == selected_id)
        with st.container(border=True):
            st.subheader(selected["title"])
            a,b,c,d = st.columns(4)
            a.metric("Case ID", selected["id"])
            b.metric("Status", selected["status"])
            c.metric("Priority", selected["priority"])
            d.metric("Type", selected["type"])
            st.write("**Description:**", selected["description"])
            st.write(f"**Created By:** {selected['created_by']}  |  **Created Date:** {selected['created_date']}")

# ---------------------------
# Evidence
# ---------------------------
elif st.session_state.page == "Evidence":
    page_header("Evidence Integrity","Evidence Management",
                "Select a local sample file to calculate SHA-256 in the browser/server session.")
    uploaded=st.file_uploader("Select a sample evidence file")
    if uploaded:
        data=uploaded.getvalue()
        sha=hashlib.sha256(data).hexdigest()
        st.success("SHA-256 calculated successfully.")
        st.code(sha)
        st.write(f"**File:** {uploaded.name}")
        st.write(f"**Size:** {len(data):,} bytes")
    st.markdown("### Registered evidence")
    st.dataframe(evidence,use_container_width=True,hide_index=True)
    st.markdown('<div class="notice">A matching hash supports an integrity check; it does not independently establish the origin, authenticity or legality of evidence.</div>',unsafe_allow_html=True)

# ---------------------------
# Custody
# ---------------------------
elif st.session_state.page == "Chain of Custody":
    page_header("Evidence Handling","Chain of Custody","Chronological evidence handling records.")
    st.dataframe(
        [{"Evidence ID":x[0],"From":x[1],"To":x[2],"Date/Time":x[3],"Reason":x[4],"Location":x[5]} for x in custody],
        use_container_width=True,hide_index=True
    )
    if st.button("+ Record Custody Event",type="primary"):
        st.info("Custody-event form is ready for backend integration: Evidence ID, From User, To User, Transfer Date, Reason, Location and Remarks.")

# ---------------------------
# Reports
# ---------------------------
elif st.session_state.page == "Reports":
    page_header("Report Generation","Investigation Reports","Create a printable structured report from synthetic records.")
    c1,c2=st.columns(2)
    with c1:
        card("Case Report","Case overview, status, activities and evidence references.","📄")
        if st.button("Generate Case Report",type="primary"):
            st.session_state.report_type="Case"
    with c2:
        card("Evidence Report","Evidence metadata, hashes and custody references.","🧾")
        if st.button("Generate Evidence Report",type="primary"):
            st.session_state.report_type="Evidence"
    if "report_type" in st.session_state:
        st.divider()
        st.subheader(f"{st.session_state.report_type} Report")
        st.write("Cybercrime Investigation & Evidence Management System")
        st.write("CASE-2026-014 · Active")
        st.write("EVD-001 · SHA-256 recorded · Chain-of-custody available")
        st.write("Generated:",datetime.now().strftime("%d-%m-%Y %H:%M"))
        st.info("Use the browser print command to save this view as PDF.")

# ---------------------------
# Audit
# ---------------------------
elif st.session_state.page == "Audit Logs":
    page_header("Security & Accountability","Audit Logs","Important system actions in chronological order.")
    st.dataframe(
        [{"Timestamp":x[0],"User":x[1],"Action":x[2],"Entity":x[3],"Entity ID":x[4]} for x in st.session_state.audit],
        use_container_width=True,hide_index=True
    )
