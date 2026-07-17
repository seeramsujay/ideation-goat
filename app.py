import os
import streamlit as st
import chromadb
from chromadb.utils import embedding_functions

from analyzers.workspace_analyzer import analyze_workspace
from analyzers.compatibility_scorer import score_compatibility
from analyzers.health_analyzer import analyze_repo_health
from analyzers.lockin_profiler import check_ecosystem_lockin
from analyzers.bug_profiler import analyze_repo_bugs

# --- 1. SETUP THE VECTOR DATABASE & CACHED ANALYZERS ---
@st.cache_resource
def setup_database():
    client = chromadb.PersistentClient(path="./chroma_data")
    default_ef = embedding_functions.DefaultEmbeddingFunction()
    
    try:
        collection = client.get_collection(
            name="github_repos", 
            embedding_function=default_ef
        )
    except ValueError:
        collection = client.create_collection(
            name="github_repos", 
            embedding_function=default_ef
        )
    return collection

@st.cache_data(ttl=3600, show_spinner=False)
def cached_health_analysis(repo_name: str):
    return analyze_repo_health(repo_name)

@st.cache_data(ttl=3600, show_spinner=False)
def cached_lockin_analysis(repo_name: str):
    return check_ecosystem_lockin(repo_name)

@st.cache_data(ttl=3600, show_spinner=False)
def cached_bug_analysis(repo_name: str):
    return analyze_repo_bugs(repo_name)

# Initialize our database
db_collection = setup_database()

# Check if database has records
try:
    db_count = db_collection.count()
except Exception:
    db_count = 0

# --- 2. THE USER INTERFACE (Streamlit) ---
st.set_page_config(
    page_title="NitroForge: GitHub Idea Matcher & Architectural Consultant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main-title {
        background: linear-gradient(135deg, #FF3366 0%, #FF9933 50%, #9933FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 3rem;
        margin-bottom: 0.2rem;
    }
    
    .subtitle {
        font-size: 1.15rem;
        color: #A0AEC0;
        margin-bottom: 2rem;
    }
    
    .repo-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        transition: transform 0.2s, border-color 0.2s;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .repo-card:hover {
        transform: translateY(-2px);
        border-color: rgba(255, 255, 255, 0.2);
        background: rgba(255, 255, 255, 0.05);
    }
    
    .repo-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.8rem;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    
    .repo-title a {
        font-size: 1.4rem;
        font-weight: 600;
        color: #63B3ED !important;
        text-decoration: none;
    }
    
    .repo-title a:hover {
        text-decoration: underline;
    }
    
    .badge-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    
    .badge {
        padding: 0.25rem 0.65rem;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 500;
    }
    
    .badge-lang {
        background-color: #2D3748;
        color: #E2E8F0;
        border: 1px solid #4A5568;
    }
    
    .badge-stars {
        background-color: rgba(236, 201, 75, 0.1);
        color: #F6E05E;
        border: 1px solid rgba(236, 201, 75, 0.3);
    }

    .badge-compat {
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .repo-match-label {
        font-size: 0.8rem;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.8rem;
        margin-bottom: 0.3rem;
    }
    
    .repo-match-chunk {
        font-size: 0.9rem;
        color: #CBD5E0;
        background: rgba(0, 0, 0, 0.2);
        padding: 0.8rem;
        border-radius: 6px;
        border-left: 3px solid #FF9933;
    }
    
    .warning-box {
        background: rgba(229, 62, 62, 0.1);
        border: 1px solid rgba(229, 62, 62, 0.3);
        padding: 1.5rem;
        border-radius: 8px;
        color: #FC8181;
        margin-bottom: 2rem;
    }

    .info-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
st.sidebar.markdown("### ⚙️ Search Controls")
language_filter = st.sidebar.selectbox(
    "Filter by Language", 
    ["All", "Python", "JavaScript", "TypeScript", "Rust", "Go"]
)

st.sidebar.divider()

# Workspace AST Analyzer Section
st.sidebar.markdown("### 📁 Workspace AST Analyzer")
workspace_path = st.sidebar.text_input(
    "Local Workspace Path",
    value=os.getcwd(),
    help="Enter the folder path of your current local project to run real-time AST compatibility checks."
)

if st.sidebar.button("📁 Analyze My Workspace", use_container_width=True):
    with st.spinner("Parsing AST & dependency tree..."):
        profile = analyze_workspace(workspace_path)
        st.session_state["workspace_profile"] = profile

# Display active workspace profile if loaded
if "workspace_profile" in st.session_state:
    prof = st.session_state["workspace_profile"]
    if "error" in prof:
        st.sidebar.error(prof["error"])
    else:
        st.sidebar.success(f"**Loaded:** `{os.path.basename(prof['path'])}`")
        st.sidebar.markdown(f"- **Primary Lang:** `{prof['primary_language']}`")
        if prof["frameworks_detected"]:
            st.sidebar.markdown(f"- **Frameworks:** `{', '.join(prof['frameworks_detected'])}`")
        if prof["build_tools"]:
            st.sidebar.markdown(f"- **Build Tool:** `{', '.join(prof['build_tools'])}`")
        st.sidebar.caption(f"Checked {len(prof['dependencies'])} dependencies.")

st.sidebar.divider()
st.sidebar.markdown(f"**Database Status:**")
if db_count > 0:
    st.sidebar.success(f"Loaded: {db_count} chunks")
else:
    st.sidebar.warning("Database is empty!")

# Header section
st.markdown("<h1 class='main-title'>⚡ NitroForge</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Semantic GitHub Idea Matcher & Zero-Friction Architectural Consultant. Match by intent, audit health, profile ecosystem lock-in, and check local workspace AST compatibility in real-time.</p>", unsafe_allow_html=True)

# Handle empty DB state
if db_count == 0:
    st.markdown("""
    <div class='warning-box'>
        <h4>⚠️ Local Vector Database is Empty</h4>
        <p>Before using the matcher, you need to populate the database with GitHub repository data. Please run the ingestion script from your terminal:</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.code("python data_ingestion.py -l all -m 50", language="bash")
    st.info("💡 Note: You can create a `.env` file containing `GITHUB_TOKEN=your_token` in the root folder to prevent rate limit restrictions.")
else:
    # User Input
    user_idea = st.text_input(
        "What are you trying to build?", 
        placeholder="e.g., A fast microservices backend with real-time WebSocket communication and user authentication.",
        key="search_input"
    )
    
    search_clicked = st.button("🔍 Find & Audit Frameworks", use_container_width=True)
    
    if search_clicked or (user_idea and st.session_state.get("last_query") != user_idea):
        st.session_state["last_query"] = user_idea
        
        if user_idea:
            with st.spinner("Analyzing semantic vector space and cross-referencing architectural audits..."):
                where_clause = {}
                if language_filter != "All":
                    where_clause = {"language": language_filter}
                    
                query_args = {
                    "query_texts": [user_idea],
                    "n_results": 5
                }
                if where_clause:
                    query_args["where"] = where_clause
                    
                results = db_collection.query(**query_args)
                
                if not results or not results['ids'] or len(results['ids'][0]) == 0:
                    st.info("No matches found. Try modifying your search idea or removing language filters.")
                else:
                    st.markdown("### 🏆 Top Architectural Matches & Audits")
                    
                    for i in range(len(results['ids'][0])):
                        metadata = results['metadatas'][0][i]
                        repo_name = metadata.get('name', 'Unknown')
                        repo_url = metadata.get('url', '#')
                        repo_lang = metadata.get('language', 'Unknown')
                        repo_stars = metadata.get('stars', 0)
                        matched_text = results['documents'][0][i]
                        
                        if repo_stars >= 1000:
                            stars_str = f"{repo_stars / 1000:.1f}k"
                        else:
                            stars_str = str(repo_stars)
                            
                        # Run / retrieve analyses
                        health = cached_health_analysis(repo_name)
                        lockin = cached_lockin_analysis(repo_name)
                        
                        compat_info = None
                        if "workspace_profile" in st.session_state and "error" not in st.session_state["workspace_profile"]:
                            compat_info = score_compatibility(st.session_state["workspace_profile"], repo_name, repo_lang, matched_text)
                        
                        # Format Health Badge
                        h_status = health.get("status", "Caution")
                        if h_status == "Healthy":
                            h_badge = "🟢 Health: 80-100 (Healthy)"
                            h_color = "#48BB78"
                        elif h_status == "Caution":
                            h_badge = f"🟡 Health: {health.get('health_score', 50)} (Caution)"
                            h_color = "#ECC94B"
                        else:
                            h_badge = f"🔴 Health: {health.get('health_score', 20)} (High Risk)"
                            h_color = "#E53E3E"
                            
                        # Format Lock-in Badge
                        l_grade = lockin.get("portability_grade", "A")
                        l_color = lockin.get("grade_color", "#48BB78")
                        l_badge = f"⚓ Portability: Grade {l_grade}"
                        
                        # Format Compatibility Badge
                        compat_badge = ""
                        if compat_info:
                            c_score = compat_info["score"]
                            c_color = compat_info["color"]
                            compat_badge = f'<span class="badge badge-compat" style="background-color: {c_color}22; color: {c_color}; border-color: {c_color}66;">🧬 Compatibility: {c_score}% ({compat_info["level"]})</span>'

                        st.markdown(f"""
                        <div class="repo-card">
                            <div class="repo-header">
                                <div class="repo-title">
                                    <a href="{repo_url}" target="_blank">{repo_name}</a>
                                </div>
                                <div class="badge-container">
                                    <span class="badge badge-lang">{repo_lang}</span>
                                    <span class="badge badge-stars">⭐ {stars_str} stars</span>
                                    <span class="badge" style="background-color: {h_color}22; color: {h_color}; border: 1px solid {h_color}66;">{h_badge}</span>
                                    <span class="badge" style="background-color: {l_color}22; color: {l_color}; border: 1px solid {l_color}66;">{l_badge}</span>
                                    {compat_badge}
                                </div>
                            </div>
                            <div class="repo-match-label">Matched Context (Semantic Intent):</div>
                            <div class="repo-match-chunk">{matched_text}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Expandable sections inside each card container
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            with st.expander("🩺 Health & Security Risk Audit"):
                                st.markdown(f"**Composite Score:** `{health.get('health_score', 0)} / 100`")
                                st.markdown(f"- **Known OSV CVEs:** `{health.get('metrics', {}).get('cve_count', 0)}`")
                                st.markdown(f"- **Last Commit Date:** `{health.get('metrics', {}).get('last_commit_date', 'Unknown')}`")
                                st.markdown(f"- **Contributors Count:** `{health.get('metrics', {}).get('contributors_count', 1)}+`")
                                if health.get("flags"):
                                    st.markdown("**Warnings & Flags:**")
                                    for flag in health["flags"]:
                                        st.warning(flag)
                                else:
                                    st.success("No major security or inactivity risks detected.")
                                    
                        with col2:
                            with st.expander("🌐 Ecosystem Lock-In Profile"):
                                st.markdown(f"**Portability Grade:** `{l_grade}`")
                                st.write(lockin.get("summary", ""))
                                locked_deps = lockin.get("locked_dependencies", [])
                                if locked_deps:
                                    st.markdown("**Locked Dependencies Detected:**")
                                    for ld in locked_deps:
                                        st.error(f"`{ld['package']}` → **{ld['vendor']}**\n\n*{ld['reason']}*")
                                else:
                                    st.success("Zero vendor lock-in dependencies detected. Highly portable across self-hosted and multi-cloud targets.")
                                    
                        with col3:
                            with st.expander("🛠️ AST Compatibility Scorecard"):
                                if not compat_info:
                                    st.info("💡 Load your local workspace path from the sidebar to run AST compatibility scoring against this repository.")
                                else:
                                    st.markdown(f"**AST Match Score:** `{compat_info['score']}%` ({compat_info['level']})")
                                    st.write(compat_info["summary"])
                                    if compat_info["conflicts"]:
                                        st.markdown("**Identified Architectural Conflicts:**")
                                        for c in compat_info["conflicts"]:
                                            st.error(c)
                                    if compat_info["migration_hints"]:
                                        st.markdown("**Actionable Migration Hints:**")
                                        for hint in compat_info["migration_hints"]:
                                            st.success(f"💡 {hint}")

                        # Chronic Bug Profiler Full Expander across width
                        with st.expander(f"🪲 Chronic Bug Profiler & Issue Landscape ({repo_name})"):
                            with st.spinner("Fetching and clustering recent issue reports via TF-IDF..."):
                                bugs = cached_bug_analysis(repo_name)
                                total_analyzed = bugs.get("total_analyzed_issues", 0)
                                if total_analyzed == 0:
                                    st.info("Could not fetch sufficient recent issue titles for clustering (or repo has zero open/closed bugs).")
                                else:
                                    r_level = bugs.get("risk_level", "Low")
                                    if r_level == "High":
                                        st.error(f"⚠️ **High Chronic Bug Risk**: Analyzed {total_analyzed} recent issues. Found critical high-frequency pitfalls.")
                                    elif r_level == "Moderate":
                                        st.warning(f"🟡 **Moderate Bug Risk**: Analyzed {total_analyzed} recent issues. Review pitfalls below.")
                                    else:
                                        st.success(f"🟢 **Low Bug Risk**: Analyzed {total_analyzed} recent issues. Issue landscape appears stable.")
                                        
                                    pitfalls = bugs.get("top_pitfalls", [])
                                    for idx, p in enumerate(pitfalls):
                                        p_label = p.get("label", "General Issues")
                                        p_pct = p.get("percentage", 0)
                                        p_crit = p.get("is_critical", False)
                                        examples = p.get("example_issues", [])
                                        
                                        if p_crit:
                                            st.markdown(f"#### {idx+1}. 🚨 **{p_label}** — `{p_pct}%` of analyzed reports")
                                        else:
                                            st.markdown(f"#### {idx+1}. ℹ️ **{p_label}** — `{p_pct}%` of analyzed reports")
                                            
                                        if examples:
                                            st.markdown("  *Example issue reports:*")
                                            for ex in examples:
                                                st.caption(f"  - \"*{ex}*\"")
                        st.divider()
        else:
            st.warning("Please enter a description of your project idea first!")
