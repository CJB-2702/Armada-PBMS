
# Projects Completed

## Requisition Application:

### Goal: Send automated Purchase Order Transactions to ELMS
#### Constraints:
Automated Transactions must be sent through Defense Logistics Agency,  Defense Automated Addressing System  in predetermined XML format

### Project Summary:
12x classes 100 -300 lines each 

Create periodic querying application to get raw data
	 -  Initial requirement 2x a day on weekdays only
	 -  updated requirement Use Python to Query database every minute
	 -  created python classes to manage multi phase time schedules 
 Format data into xml:
	- read and understand DLA 511R transaction rules by reading 100 pg pdf document
	- read and understand DLA XMR Transaction rules by reading raw XMR document
	- Prototype workable template
		- Work with business stakeholders to understand various transaction codes
		- Transform queries into valid XML
			- Understand business rules
				- NSN vs SCN vs PN transaction structures change logic and structure
				- Source Vs Destination rules
				- download part unit of measure codes, translate into dictionary, convert to DAAS safe codes
			- understand DAAS transmission rules
				- grouping rules date time adjustments etc
		-  Render using Jinja2 template
Use SFTP to transmit files to DAAS:
- File paperwork to get a DLA outbox and inbox
- Work with DISA and N6 to open up server connections
- Create SFTP management class
	- Troubleshoot DLA, DISA, N6 specific connection rules software requirements and setup
-  Understand how DAAS automatic adressing system makes modifications to XML in transit
-  Understand How RIC's and DODACCS interact with DLA and ELMS 
-  Work with stakeholders to get new RIC's and DODACCS

Work with NSW stakeholders to visualize transactions:
- Create manual transaction monitoring and transmission User interface using python and flask
- display all transactions within a designated time frame
- Verify transmissions were sent and update FASuite database so application has feedback

Process in status updates:
 -  Write code to read in DAAS 87s status updates
	 -  Negotiate with elms to send transactions back
 - find solutions to get status back without ELMS
 - use one touch as a source of information
	 - write scripts to generate micro batches of document numbers to get status back
	 - Upload documents to elms
	 - Get emails back 
	 - Translate and process in all status updates from multiple excel documents
 - Work with joint forces Logistics data group to centralize data


## FASuite Data Loader Application
### Goal: Create a Front End Application to Import Data
### Constraints:
Asset works has a command line tool that takes a path to an XML document to automatically process in data based off of a series of number codes loosely related to tables screens within the application and hits a series of endpoints to simulate work done in app. 
### Project Summary:

Read documentation for application:
 - setup FASuite to configure with the dataloader executable
 - understand command line rules
Use python to construct command line strings and execute:

Create multiple forms for generating an xml template using Flask HTMX and vanilla JS:
	- create login form
		- basic storage in memory html
		- test login success by submitting blank transmission and reading back response
	- screen selection form
		- query database, create jinja template listing all potential elements on the screen 
	- element form
		- highlight required fields and recommended fields
	- output form 
		- use javascript so that selected fields create a simple table interface
		- paste in data
		- convert html table into xml table
	- display errors back to user
		- read file system to detect errors and display back to user

### NIPR to SIPR DB Transmit Tool:
### Goal: Convert Tables into XML and Back From NIPR to SIPR

- Write Python to query every table in a list for changes within a given time period
- Convert to XML
- Generate an XML Schema
	- Work with NSW to get exceptions
- FTP transmit
- Parse Back in XML to SIPR sister database
- make above steps generic and extendable to any database


# Dashboards

The dashboards detailed below leverage a dedicated query repository developed to extract and visualize data from the FA Suite application.

Dispatch Management Dashboard

- **Track Number of Open Dispatches:** Provide an immediate view of the current workload and backlog. 
- **Late Dispatches:** Highlights dispatches that have exceeded the defined service level agreements (SLAs) or target completion times.
- **Dispatch Time:** Measures the average, minimum, and maximum time taken from dispatch creation to resolution. (e.g., assignment time vs. travel time vs. repair time).
- **Review Against Different Orgs:** Benchmarking key metrics (open dispatches, late rates, average times) across various organizational units, locations, or teams. 

Financial and Performance Dashboard

This dashboard analyzes costs and employee performance to optimize resource expenditure and efficiency.

- **Track Labor and Part Costs:** Comprehensive monitoring of expenses associated with maintenance and repairs.
    - **Against Vehicle Class, Model, Equipment:** Detailed breakdown of costs by asset type to identify maintenance-heavy equipment or models that are inefficient to repair. This data informs procurement and lifecycle management decisions.
    - **Track Employee Performance:** Evaluation of individual or team efficiency metrics, such as hours worked per job, job completion rates, employee utilization.

Labor and Maintenance Dashboard
labor types, tasks, and maintenance cycles.

- **Track Labor Types:** Analysis of how labor hours are categorized (e.g., preventive maintenance, corrective maintenance, warranty work).
    - **Tasks, Cost, Identify Outliers:** Deep dive into specific task costs to identify inefficient procedures or unexpected high expenses. 
    - **Number of Times Each Piece of Equipment Goes Through a Piece of Maintenance:** Tracks maintenance frequency to evaluate equipment reliability, effectiveness of preventive maintenance schedules, and warranty claims.

Parts Management Dashboard

This dashboard visualizes data related to inventory management and part usage.

- **Part Types:** Analysis of which part categories are most frequently used or costly.
    - **Number of Times Each Piece is Issued Each Equipment:**
    - Identifies models and equipment consuming most parts


---

Customer Support

Customer support activities encompass general user assistance, system administration, and high-level leadership support and analysis.

User and System Administration

General user demands and application administration tasks are a core function of the support role.

- **Add Users:** Provisioning new user accounts, assigning roles, and ensuring proper access controls are in place.
- **Update User Information:** Managing changes to existing user profiles, such as name changes, organizational moves, or permission updates.
- **Add Parts:** Managing the addition of new inventory items into the system.
    - **Work with Cross-Functional Teams to Ensure SCNS and NSNs Match and Are Updated:** Collaboration with supply chain and logistics teams to ensure standardized cataloging of parts using appropriate Stock Control Numbers (SCNS) and National Stock Numbers (NSNs)
- **Add Maintenance Tasks:** Defining and updating the catalog of available maintenance procedures and job plans within the FA Suite.
- **Work with Teams to Fix Errors and Clean Data:** working with end-users to correct entry errors and maintaining system hygiene.
- **Deal with Supply and Part Issues:** Acting as a liaison between users and the supply chain, troubleshooting inventory discrepancies, and addressing part availability challenges.
- **Lots of Small Admin Tasks That Take Time:** General, recurring administrative tasks that ensure smooth system operation (e.g., generating ad-hoc reports, unlocking accounts

Technical Scripting

- **Password Reset Email Forwarding Script:** Development and maintenance of scripts (e.g., PowerShell, Python) to automate or manage password reset requests



General N49 Leadership Support and Analysis
Providing direct support and data analysis to key leadership (Winston and Tom).

- **Review Spending and Labor:** High-level analysis of financial data, summarizing trends and identifying areas for cost savings or optimization.
- **Review Excel Documents and Make Charts on Historic Spending:** Data visualization and reporting using historical financial data in Excel, transforming raw data into actionable intelligence and presentations.
- **Any Random Task to Support Winston and Tom:** 




