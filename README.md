
# Biojobs

Students and graduates in the Boston/Cambridge area face a time-consuming challenge: identifying biomedical research labs that align with their skills and interests for potential "cold-call" employment or academic inquiries. This project proposes the **Boston Biomed Lab Matcher**, an intelligent bot designed to solve this problem. The bot will maintain a comprehensive database of biomedical labs, institutes, and departments by systematically scraping and consolidating data from major Boston/Cambridge institutions (including Harvard, MIT, BU, Tufts, and their affiliated research institutes). A user will upload their resume (CV), which the bot will analyze to extract key skills, research interests, and methodologies. The system will then match the user's profile against the lab database to generate a ranked list of "best-fit" labs. As a final, critical step, the bot will provide an AI-powered assistant to help the user **tailor their resume and draft a compelling, lab-specific "cold-call" email** for each suggested opportunity.

Based on recent 2024 industry reports, here is the estimated number of bio-related jobs in the Boston/Cambridge area.

While most official reports list data for the entire state, a reliable estimate for just the cities of **Boston and Cambridge is approximately 80,000 bio-related jobs.**

This estimate is based on the most recent statewide employment data from 2024 and key industry investment figures.

### 📈 How This Estimate Is Calculated

1.  **Statewide Total:** The Massachusetts Biotechnology Education Foundation (MassBioEd) and other sources report a total of **143,142 life sciences jobs** in Massachusetts in 2024.

2.  **Local Concentration:** A precise job count for just Boston and Cambridge isn't published. However, we can use 2024 venture capital (VC) funding as a strong proxy for job concentration.
    * In the first half of 2024, **56% of all life sciences VC funding** in Massachusetts went to companies located in Boston (21%) and Cambridge (35%).

3.  **Calculation:** 56% of the 143,142 statewide jobs is approximately **80,160 jobs**.

### 🔬 Key Context

* **The Hub of the Hub:** Boston and Cambridge are the undisputed epicenter of the state's life sciences industry. Key data points from 2023-2024 confirm this:
    * **R&D Growth:** In 2023, Boston's Seaport district (within Suffolk County) added more R&D jobs than any other area in the Commonwealth.
    * **Lab Space:** The vast majority of Massachusetts's lab space is concentrated in these two cities. In 2024, lab vacancy rates were 22.9% in Cambridge and 38.3% in Boston, reflecting the massive physical footprint of the industry.
* **Biopharma Subset:** A large portion of these roles are in "biopharma" (research, development, and manufacturing of drugs). In 2024, Massachusetts had **117,108 biopharma jobs** statewide, and the majority of these are concentrated in the Boston/Cambridge area.
* **Current Market:** The job market has slowed significantly from its peak in 2021-2022. Reports from 2024 and 2025 show that job growth has flattened, and the industry has seen a wave of layoffs, primarily centered in Cambridge and Boston.
-----

### **Requirements Document: Boston Biomed Lab Matcher**

**1.0 Introduction**

This document outlines the requirements for the **Boston Biomed Lab Matcher**, an automated tool designed to connect students and graduates with relevant biomedical research opportunities in the Boston/Cambridge area.

The bot's primary functions are:

1.  To build and maintain a "live" database of biomedical labs and their specific research focus.
2.  To analyze a user's resume/CV to create a "skill and interest profile."
3.  To match the user's profile against the lab database and suggest high-potential contacts.
4.  To provide AI-powered assistance to tailor application materials (resume and email) for a specific lab.

**2.0 Core Features & User Stories**

  * **As a student,** I want to upload my resume and quickly get a list of 10-15 local labs that are a perfect match for my skills in CRISPR and oncology.
  * **As a graduate,** I want to find the *specific* labs working on neurodegenerative diseases so I don't waste time emailing labs that only study immunology.
  * **As a user,** when I see a good match, I want to know *why* it's a match (e.g., "Your resume mentions 'confocal microscopy,' and this lab lists it as a key technique").
  * **As a user,** once I pick a lab, I want the bot to help me write a non-generic email that mentions the lab's *actual research* and *recent publications* so I sound informed and serious.

**3.0 Functional Requirements (FR)**

**FR-01: Lab Database**
The system shall maintain a database of research labs. Each entry must include:

  * `Lab_Name` / `Principal_Investigator (PI)`
  * `Institution` (e.g., "Harvard Medical School," "MIT," "Broad Institute")
  * `Department` (e.g., "Genetics," "Biological Engineering")
  * `Research_Focus_Summary` (A concise, AI-generated summary)
  * `Lab_Keywords` (e.g., "CRISPR," "neuroscience," "single-cell RNA-seq")
  * `Lab_Website_URL` (The source URL)
  * `Recent_Publications_URL` (If available)

**FR-02: Web Scraping Engine**

  * The system shall deploy a set of targeted scrapers for each major institutional hub (see Section 4.0).
  * The scrapers must be able to follow links from department pages (e.g., "Faculty") to individual lab or profile pages.
  * Scrapers will run on a schedule (e.g., weekly) to find new labs and update existing ones.

**FR-03: Resume Analysis Engine**

  * The system shall allow users to upload a resume (`.pdf`, `.docx`).
  * The system shall parse the text to extract:
      * **Skills & Techniques:** (e.g., "Python," "PCR," "Western Blot," "machine learning")
      * **Research Interests:** (e.g., "oncology," "gene therapy," "drug discovery")
      * **Experience Level:** (e.g., "undergraduate," "post-doc")

**FR-04: Matching & Suggestion Engine**

  * The system shall compare the user's resume profile (FR-03) against the `Lab_Keywords` and `Research_Focus_Summary` in the database (FR-01).
  * The system shall present a ranked list of suggested labs, ordered by "match score."
  * Each match *must* be presented with a justification (e.g., "Match found for: 'machine learning' and 'genomics'").

**FR-05: AI Tailoring Assistant**

  * When a user selects a lab, the system shall provide an AI-powered chat interface.
  * The system will "prime" the AI with:
    1.  The user's resume.
    2.  The target lab's `Research_Focus_Summary`.
    3.  (Optional) The text from one or two of the lab's recent publications.
  * The assistant will then help the user draft an email and revise resume bullet points to highlight the most relevant skills for *that specific lab*.

**4.0 Data Sources (Scraper Targets)**

This section details the websites the bot will scrape to build its database (FR-01). This is based on the known institutional structures in the Boston/Cambridge area.

| Institution | Primary Data Hub (Scraping Target) | Strategy |
| :--- | :--- | :--- |
| **Harvard & Affiliates** | `hms.harvard.edu` (Departments & Centers page) | **Top-Down:** 1. Scrape the list of all basic science departments (Genetics, Cell Biology, etc.). 2. Visit each department's "Faculty" or "Labs" page. 3. Follow links to each individual PI/Lab page to get their research summary. |
| **Affiliated Institutes** | `massgeneral.org/research` (MGH)<br>`brighamandwomens.org/research` (BWH)<br>`ragoninstitute.org`<br>`broadinstitute.org`<br>`wyss.harvard.edu` | **Hub-Based:** 1. Go to the main research institute page. 2. Find the "Faculty," "Research Labs," or "Core Faculty" directory. 3. Scrape the list of PIs and their lab descriptions. These are often more centralized than university pages. |
| **MIT** | `mit.edu/research/centers-labs-programs` | **Hub-Based:** 1. Get the master list of all labs and centers. 2. Filter for biomedical-related entities (e.g., Koch Institute, Picower Institute, IMES, Dept. of Biological Engineering). 3. Visit each entity's "Faculty" or "Labs" page and scrape the details. |
| **Boston University (BU)**| `bumc.bu.edu/medicine/research/research-centers`<br>`bu.edu/academics/eng/departments/biomedical-engineering/` | **Department-Based:** 1. Go to the School of Medicine's centers list and the BME labs list. 2. Scrape the "Faculty Research Areas" page from the Program in Biomedical Sciences (PiBS) to find faculty by topic. 3. Follow links to faculty profiles. |
| **Tufts University** | `medicine.tufts.edu/research/research-labs-centers` | **Center-Based:** 1. Scrape the main list of research centers (e.g., Molecular Cardiology Research Institute). 2. Visit the Graduate School of Biomedical Sciences (GSBS) page to find its faculty list and lab descriptions. |

**5.0 Non-Functional Requirements**

  * **NFR-01: Privacy & Security (CRITICAL):** A user's resume is highly sensitive. The system *must not* store resumes after the user's session is complete. All analysis must be done in-memory, and the data must be deleted immediately.
  * **NFR-02: Data Freshness:** Lab websites change. The scrapers must run at least weekly to keep the database current.
  * **NFR-03: Scalability:** The scrapers must be designed to be polite, respecting `robots.txt` files and using rate-limiting to avoid being blocked by university servers.

-----

### 🚀 Step-by-Step Project Plan (10-Step)

**Phase 1: Foundation & Data Ingestion (Weeks 1-4)**

1.  **Define Database Schema:** Architect the "Master Lab" database (as specified in FR-01).
2.  **Build Scraper Framework:** Build a robust, scalable scraping framework (e.g., using Python with Scrapy or Playwright) that can handle the different website structures.
3.  **Deploy "Seed" Scrapers:** Develop and launch the first scrapers for the major hubs (e.g., Harvard Medical School Departments, MIT Centers list).
4.  **Create AI Summarizer:** Write a script that takes the raw "research description" text from a scraped lab page and uses an LLM (like the Gemini API) to generate the clean `Research_Focus_Summary` and extract the `Lab_Keywords`. This standardizes the data.

**Phase 2: Backend & User Logic (Weeks 5-7)**
5\.  **Develop Resume Analysis API:** Create a secure endpoint that accepts a resume, parses it (using a library like `pdfminer` or `python-docx`), and uses an LLM to extract the skills/interests profile (FR-03).
6\.  **Build the Matching Engine:** Create the core logic that takes the JSON output from the resume parser and runs a vector search or keyword query against the Master Lab Database to find the best matches.

**Phase 3: Frontend & User Interface (Weeks 8-10)**
7\.  **Design the User Interface (UI):** Design a simple, 3-step web flow:
\* Step 1: Upload Resume (with a clear privacy disclaimer).
\* Step 2: View Results (A card-based list of matched labs with justification).
\* Step 3: "Get Help" (Launches the AI Tailoring Assistant for a selected lab).
8\.  **Develop the Frontend:** Build the UI and connect it to the backend APIs.

**Phase 4: AI Integration & Deployment (Weeks 11-12)**
9\.  **Integrate AI Tailoring Assistant:** Build the chat interface (FR-05). This involves careful prompt engineering to feed the user's resume + the lab's data to the LLM to get high-quality, personalized drafts.
10\. **Beta Testing & Deployment:** Deploy to a test server. Ask students to upload their real-world resumes to check the quality of the matches and the usefulness of the AI-drafted emails. Refine and launch.

-----

### 📊 Step-by-Step: How to Find Labs & Meta-Info (The Scraper Plan)

This is the detailed technical plan for **Phase 1 (Steps 2 & 3)**.

**1. The "Top-Down" University Scraper (e.g., Harvard)**
This model works for large, decentralized universities.

  * **Step 1:** Go to the "seed" page (e.g., `https://hms.harvard.edu/research/research-departments-centers-initiatives-more`).
  * **Step 2:** Scrape the list of all `Department` links (e.g., "Cell Biology," "Genetics").
  * **Step 3:** For each `Department` link, navigate to that page and find the link for "Faculty" or "Labs."
  * **Step 4:** On the "Faculty" page, scrape the list of all `PI_Names` and their `Profile_Page_URL`.
  * **Step 5:** Visit each `Profile_Page_URL`. On this final page, scrape the "Research Description" or "Lab Focus" text.
  * **Step 6:** Save this raw text, the PI's name, and the URL to your database for the AI Summarizer (Step 4 in the project plan) to process.

**2. The "Hub-Based" Institute Scraper (e.g., Broad, Ragon, Koch)**
This model works for self-contained research institutes. It's usually easier.

  * **Step 1:** Go to the "seed" page (e.g., `https://www.broadinstitute.org/scientific-community/core-faculty` or `https://imes.mit.edu/people/faculty`).
  * **Step 2:** This page is often the *actual directory*. Scrape the list of all faculty members directly from this page.
  * **Step 3:** The page will often have a short "research snippet" next to the name. Scrape this snippet *and* the link to their full profile/lab page.
  * **Step 4:** Visit the full lab page to get the more detailed "Research Description" text.
  * **Step 5:** Save this data to your database for processing.

**3. The "Topic-Based" Scraper (e.g., BU PiBS)**
This is a clever alternative for finding labs by subject.

  * **Step 1:** Go to the "seed" page (e.g., `https://www.bumc.bu.edu/gms/pibs/faculty-research-areas/`).
  * **Step 2:** Scrape the list of all *topics* (e.g., "Neurodegenerative disorders," "Cancer biology").
  * **Step 3:** For each *topic*, get the list of `PI_Names` associated with it. This automatically pre-tags the lab with a keyword.
  * **Step 4:** Find the main faculty directory to get the `Profile_Page_URL` for each PI.
  * **Step 5:** Visit the profile page, get the detailed description, and save it all to your database.

