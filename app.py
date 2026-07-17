import streamlit as st
import chromadb
from chromadb.utils import embedding_functions

# --- 1. SETUP THE VECTOR DATABASE ---
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

# Initialize our database
db_collection = setup_database()

# Check if database has records
try:
    db_count = db_collection.count()
except Exception:
    db_count = 0

# --- 2. THE USER INTERFACE (Streamlit) ---
st.set_page_config(
    page_title="GitHub Idea Matcher - Find Frameworks by Intent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Custom CSS
st.markdown("""
<style>
    /* Styling headers and body */
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
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        font-size: 1.2rem;
        color: #A0AEC0;
        margin-bottom: 2rem;
    }
    
    /* Card design for repositories */
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
        gap: 0.5rem;
    }
    
    .badge {
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.8rem;
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
    
    .repo-desc {
        color: #E2E8F0;
        font-size: 1rem;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    
    .repo-match-label {
        font-size: 0.8rem;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 0.05em;
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
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("### ⚙️ Search Controls")
language_filter = st.sidebar.selectbox(
    "Filter by Language", 
    ["All", "Python", "JavaScript", "TypeScript", "Rust", "Go"]
)

st.sidebar.divider()
st.sidebar.markdown(f"**Database Status:**")
if db_count > 0:
    st.sidebar.success(f"Loaded: {db_count} chunks")
else:
    st.sidebar.warning("Database is empty!")

# Header section
st.markdown("<h1 class='main-title'>🧠 GitHub Idea Matcher</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Describe your project idea in plain English. The AI matches it semantically to the README files of popular frameworks—even without keyword overlap.</p>", unsafe_allow_html=True)

# Handle empty DB state
if db_count == 0:
    st.markdown("""
    <div class='warning-box'>
        <h4>⚠️ Local Vector Database is Empty</h4>
        <p>Before using the matcher, you need to populate the database with GitHub repository data. Please run the ingestion script from your terminal:</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.code("python data_ingestion.py -l all -m 50", language="bash")
    st.info("💡 Note: You can create a `.env` file containing `GITHUB_TOKEN=your_token` in the root folder to prevent rate limit limits.")
else:
    # Import our new discovery tools
    from mcp_server import (
        verify_workspace_fit, 
        compose_solution_stack, 
        get_repo_health, 
        profile_repo_hardware_footprint, 
        align_system_architecture
    )
    
    # Define 6 tabs for different discovery suite tools
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔍 Semantic Search", 
        "🏗️ Stack Composer", 
        "📋 Workspace Fit", 
        "🩺 Repo Health", 
        "🎛️ Edge Profile", 
        "🏛️ Architecture Aligner"
    ])
    
    # --- TAB 1: SEMANTIC SEARCH & MATCHING ---
    with tab1:
        user_idea = st.text_input(
            "What are you trying to build?", 
            placeholder="e.g., A fast backend server with user authentication and automatic database migration support.",
            key="search_input"
        )
        
        search_clicked = st.button("🔍 Find Frameworks", use_container_width=True)
        
        if search_clicked and user_idea:
            with st.spinner("Analyzing semantic space and matching repos..."):
                # Setup Query arguments
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
                st.session_state["search_results"] = results
                st.session_state["last_query"] = user_idea
                
        results = st.session_state.get("search_results")
        
        if results:
            if not results or not results['ids'] or len(results['ids'][0]) == 0:
                st.info("No matches found. Try modifying your search idea or removing filters.")
            else:
                st.markdown("### 🏆 Top Semantic Matches")
                
                for i in range(len(results['ids'][0])):
                    metadata = results['metadatas'][0][i]
                    repo_name = metadata.get('name', 'Unknown')
                    repo_url = metadata.get('url', '#')
                    repo_lang = metadata.get('language', 'Unknown')
                    repo_stars = metadata.get('stars', 0)
                    matched_text = results['documents'][0][i]
                    
                    # Star formatting
                    if repo_stars >= 1000:
                        stars_str = f"{repo_stars / 1000:.1f}k"
                    else:
                        stars_str = str(repo_stars)
                        
                    # Card structure
                    st.markdown(f"""
                    <div class="repo-card">
                        <div class="repo-header">
                            <div class="repo-title">
                                <a href="{repo_url}" target="_blank">{repo_name}</a>
                            </div>
                            <div class="badge-container">
                                <span class="badge badge-lang">{repo_lang}</span>
                                <span class="badge badge-stars">⭐ {stars_str} stars</span>
                            </div>
                        </div>
                        <div class="repo-match-label">Matched Context:</div>
                        <div class="repo-match-chunk">{matched_text}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Interactive Action Buttons
                    col1, col2, col3, col4 = st.columns(4)
                    
                    fit_key = f"btn_fit_{repo_name}_{i}"
                    health_key = f"btn_health_{repo_name}_{i}"
                    profile_key = f"btn_profile_{repo_name}_{i}"
                    align_key = f"btn_align_{repo_name}_{i}"
                    
                    with col1:
                        if st.button("📋 Workspace Fit", key=fit_key):
                            st.session_state[f"active_action_{i}"] = ("fit", repo_name)
                    with col2:
                        if st.button("🩺 Repo Health", key=health_key):
                            st.session_state[f"active_action_{i}"] = ("health", repo_name)
                    with col3:
                        if st.button("🎛️ Edge Profile", key=profile_key):
                            st.session_state[f"active_action_{i}"] = ("profile", repo_name)
                    with col4:
                        if st.button("🏛️ Align Arch", key=align_key):
                            st.session_state[f"active_action_{i}"] = ("align", repo_name)
                            
                    # Run the selected action for this repo
                    active_act = st.session_state.get(f"active_action_{i}")
                    if active_act and active_act[1] == repo_name:
                        action_type = active_act[0]
                        with st.spinner(f"Analyzing {repo_name}..."):
                            if action_type == "fit":
                                scorecard = verify_workspace_fit(repo_name)
                                st.markdown(scorecard)
                            elif action_type == "health":
                                health_report = get_repo_health(repo_name)
                                st.markdown(health_report)
                            elif action_type == "profile":
                                st.info("💡 Profiling with standard microcontroller specs (ESP32, 256KB SRAM, 1024KB Flash)")
                                profile = profile_repo_hardware_footprint(repo_name, "ESP32")
                                st.markdown(profile)
                            elif action_type == "align":
                                align_report = align_system_architecture(repo_name)
                                st.markdown(align_report)
                        st.divider()

    # --- TAB 2: STACK COMPOSER ---
    with tab2:
        st.markdown("### 🏗️ Agentic Stack Composer")
        st.markdown("Decompose a complex, multi-layered system idea and construct a compatible blueprint stack of open-source libraries.")
        
        composer_idea = st.text_input(
            "Describe the overall system idea",
            placeholder="e.g. secure offline-first mobile app with synchronization",
            key="composer_input"
        )
        composer_results_num = st.slider("Max components per layer", 1, 5, 3, key="composer_n_results")
        
        if st.button("Generate Stack Blueprint", use_container_width=True):
            if composer_idea:
                with st.spinner("Analyzing layers and searching index..."):
                    blueprint = compose_solution_stack(composer_idea, composer_results_num)
                    st.markdown(blueprint)
            else:
                st.warning("Please enter a system idea first.")

    # --- TAB 3: WORKSPACE FIT ---
    with tab3:
        st.markdown("### 📋 Workspace Compatibility & License Guard")
        st.markdown("Scan your workspace files and licenses, and compare them against a proposed GitHub repository.")
        
        fit_repo = st.text_input(
            "Target GitHub Repository Name",
            placeholder="e.g. psf/requests",
            key="fit_repo_input"
        )
        fit_workspace = st.text_input(
            "Workspace Path",
            value=".",
            key="fit_workspace_input"
        )
        
        if st.button("Check Workspace Fit", use_container_width=True):
            if fit_repo:
                with st.spinner("Analyzing workspace compatibility..."):
                    scorecard = verify_workspace_fit(fit_repo, fit_workspace)
                    st.markdown(scorecard)
            else:
                st.warning("Please enter a target repository name.")

    # --- TAB 4: REPO HEALTH ---
    with tab4:
        st.markdown("### 🩺 Pulse & Health Telemetry")
        st.markdown("Fetch real-time repository health, activity metrics, and OSV security vulnerabilities.")
        
        health_repo = st.text_input(
            "Target GitHub Repository Name",
            placeholder="e.g. encode/django-rest-framework",
            key="health_repo_input"
        )
        
        if st.button("Run Health Check", use_container_width=True):
            if health_repo:
                with st.spinner("Fetching telemetry and OSV vulnerabilities..."):
                    report = get_repo_health(health_repo)
                    st.markdown(report)
            else:
                st.warning("Please enter a target repository name.")

    # --- TAB 5: HARDWARE FOOTPRINT ---
    with tab5:
        st.markdown("### 🎛️ Edge-Deploy Resource & Footprint Profiler")
        st.markdown("Profile a codebase's estimated compiled and runtime memory footprint against specified hardware constraints.")
        
        profile_repo = st.text_input(
            "Target GitHub Repository Name",
            placeholder="e.g. lvgl/lvgl",
            key="profile_repo_input"
        )
        profile_hardware = st.text_input(
            "Target Hardware Board/MCU",
            value="ESP32",
            key="profile_hardware_input"
        )
        profile_sram = st.number_input(
            "SRAM Limit (KB)",
            value=256.0,
            step=32.0,
            key="profile_sram_input"
        )
        profile_flash = st.number_input(
            "Flash Limit (KB)",
            value=1024.0,
            step=128.0,
            key="profile_flash_input"
        )
        
        if st.button("Run Hardware Profile", use_container_width=True):
            if profile_repo:
                with st.spinner("Analyzing codebase specifications..."):
                    profile = profile_repo_hardware_footprint(profile_repo, profile_hardware, profile_sram, profile_flash)
                    st.markdown(profile)
            else:
                st.warning("Please enter a target repository name.")

    # --- TAB 6: ARCHITECTURE ALIGNER ---
    with tab6:
        st.markdown("### 🏛️ Architectural Alignment & Drift Check")
        st.markdown("Check how a proposed repository fits into the design patterns of your local workspace structure.")
        
        align_repo = st.text_input(
            "Proposed Library/Repository Name",
            placeholder="e.g. SQLAlchemy",
            key="align_repo_input"
        )
        align_workspace = st.text_input(
            "Workspace Path",
            value=".",
            key="align_workspace_input"
        )
        
        if st.button("Check Architectural Alignment", use_container_width=True):
            if align_repo:
                with st.spinner("Analyzing project design patterns..."):
                    align_report = align_system_architecture(align_repo, align_workspace)
                    st.markdown(align_report)
            else:
                st.warning("Please enter a proposed repository name.")

