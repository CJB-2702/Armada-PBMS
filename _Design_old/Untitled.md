Projects Completed

Requisition Application

**Goal:** Send automated Purchase Order Transactions to the ELMS system.

**Constraints:**  
Automated transactions must be transmitted through the Defense Logistics Agency (DLA) Defense Automated Addressing System (DAAS) in a predetermined XML format.

Project Summary

Developed a periodic querying application using Python, comprising 12 classes (100-300 lines each) to manage the end-to-end process.

**Key Activities:**

- **Data Retrieval:** Created Python classes to query the database periodically (initial requirement was twice daily, updated to every minute) and manage multi-phase schedules.
- **XML Formatting:**
    - Interpreted extensive DLA documentation (511R transaction rules, XMR documents) to understand transaction logic.
    - Collaborated with business stakeholders to define transaction codes and rules (e.g., handling NSN, SCN, PN structures, Source vs. Destination rules).
    - Translated part unit of measure codes to DAAS-safe codes.
    - Rendered the final XML using Jinja2 templates.
- **Secure Transmission (SFTP):**
    - Coordinated with DLA, DISA, and N6 to establish secure server connections and required paperwork.
    - Developed an SFTP management class to handle specific connection rules and software requirements.
    - Understood how the DAAS automatic addressing system modifies XML in transit and how RICs (Routing Identifier Codes) and DODACCS interact with DLA and ELMS.
- **Monitoring & Feedback:**
    - Created a manual transaction monitoring and transmission UI using Python and Flask.
    - Verified transmissions were sent and updated the FA Suite database with feedback.
- **Status Updates:**
    - Wrote code to read and process DAAS 87s status updates.
    - Negotiated solutions for status retrieval (using One Touch, generating micro-batches, processing Excel documents) and worked with joint forces logistics data groups to centralize data.

FA Suite Data Loader Application

**Goal:** Create a front-end application to import data into FA Suite.

**Constraints:**  
AssetWorks uses a command-line tool that takes an XML path to process data by simulating application screen interactions.

Project Summary

Read extensive application documentation to configure the FA Suite dataloader executable and understand command line rules.

**Key Activities:**

- **Application Logic:** Used Python to construct and execute necessary command line strings.
- **User Interface:** Created multiple forms for generating an XML template using Flask, HTMX, and vanilla JS:
    - Login form with in-memory storage for basic authentication testing.
    - Screen selection form to query the database and list available elements using a Jinja template.
    - Element form to highlight required/recommended fields.
    - Output form using JavaScript to create a table interface for data input and conversion to XML.
    - Error handling interface to read file system errors and display them to the user.

NIPR to SIPR DB Transmit Tool

**Goal:** Convert database tables into XML for transmission between NIPR and SIPR networks.

**Key Activities:**

- Wrote Python scripts to query specified tables for changes within a given time period.
- Converted data to XML format.
- Generated an XML schema and coordinated with NSW for exceptions.
- Used FTP for secure transmission.
- Parsed the XML back into a sister database on the SIPR network.
- Ensured the solution was generic and extendable to any database.

---

Dashboards

The dashboards detailed below leverage a dedicated query repository developed to extract and visualize data from the FA Suite application.

Dispatch Management Dashboard

Focuses on operational efficiency and performance metrics:

- **Track Number of Open Dispatches:** Immediate view of workload and backlog.
- **Late Dispatches:** Highlights tasks exceeding SLAs to identify bottlenecks.
- **Dispatch Time:** Measures average time from creation to resolution, breaking down assignment, travel, and repair times.
- **Review Against Different Orgs:** Benchmarking metrics across various organizational units to identify best practices.

Financial and Performance Dashboard

Analyzes costs and employee performance:

- **Track Labor and Part Costs:** Comprehensive monitoring of expenses.
    - **Against Vehicle Class, Model, Equipment:** Breakdown of costs by asset type to inform procurement and lifecycle management.
    - **Track Employee Performance:** Evaluation of efficiency metrics (hours per job, completion rates, utilization) to support performance reviews.

Labor and Maintenance Dashboard

Focuses on labor types, tasks, and maintenance cycles:

- **Track Labor Types:** Analysis of labor hours categorization (preventive, corrective, warranty).
    - **Tasks, Cost, Identify Outliers:** Deep dive into specific task costs to identify inefficient procedures or data errors.
    - **Number of Times Each Piece of Equipment Goes Through a Piece of Maintenance:** Tracks frequency to evaluate equipment reliability and effectiveness of schedules.

Parts Management Dashboard

Visualizes inventory management and part usage data:

- **Part Types:** Analysis of frequently used or costly part categories.
- **Number of Times Each Piece is Issued Each Equipment:** Identifies models and equipment consuming the most parts.

---

Customer Support

Encompasses user assistance, system administration, and high-level leadership support.

User and System Administration

Core functions supporting general user demands and application administration:

- **Add Users:** Provisioning accounts, roles, and access controls.
- **Update User Information:** Managing changes to profiles and permissions.
- **Add Parts:** Managing new inventory items into the system.
    - **Work with Cross-Functional Teams to Ensure SCNS and NSNs Match and Are Updated:** Collaboration to maintain data integrity using standardized Stock Control Numbers (SCNS) and National Stock Numbers (NSNs).
- **Add Maintenance Tasks:** Defining and updating maintenance procedures in the FA Suite.
- **Work with Teams to Fix Errors and Clean Data:** Proactive data governance and quality control.
- **Deal with Supply and Part Issues:** Liaison between users and supply chain for inventory and availability challenges.
- **Lots of Small Admin Tasks That Take Time:** Recurring administrative tasks such as ad-hoc reports and account management.

Technical Scripting

- **Password Reset Email Forwarding Script:** Developed scripts (e.g., PowerShell, Python) to automate password reset requests or notifications.

General N49 Leadership Support and Analysis

Direct data analysis for leadership:

- **Review Spending and Labor:** High-level financial analysis and trend summarization.
- **Review Excel Documents and Make Charts on Historic Spending:** Data visualization using historical data to create actionable intelligence.
- **Any Random Task to Support Winston and Tom:** Ad-hoc support demonstrating adaptability to high-priority requests.