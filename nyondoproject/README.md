# NyondoStock: Hardware Inventory, Credit Scheme & Sales Management System

A centralized, web-based Django enterprise application developed for NYONDO General Hardware LTD to digitize manual stock tracking, tiered sales, distance-based transport calculations, supplier credit tracking, and a specialized salary-earner deposit scheme.

## Live Application & Repository
1. Live Deployment Link: https://shadia.pythonanywhere.com
2. GitHub Repository: https://github.com/shadia-nalubega/nyondo4.git

---

## Technical Project Features & Workflows

### 1. Store Manager Module & Stock Registration Session Flow
1. Multi-Step Stock Intake: Handles incoming hardware stock registrations dynamically.
2. Session-Based Data Handling: Built a custom data pipeline where stock data session states are successfully preserved and transferred seamlessly from one form to another, then securely brought back into the main view upon completion.
3. Cost & Predetermined Pricing: Allows managers to view current product prices, set the baseline cost configurations, track inventory volumes, and generate stock reports.

### 2. Sales Attendant Module & Automated Billing
1. Dynamic Price Fetching: Implemented automatic price fetching. When a product is selected, the system pulls its exact pre-determined price automatically from the Fixed Prices database page—preventing human manual retyping errors.
2. Three-Tier Customer Pricing Architecture: Built database models to handle three distinct customer types with distinct pricing margins:
  * Wholesalers
  * Retailers
  * Normal/Individual Buyers
3. Automated Distance-Based Transport Logic: Calculates client logistics instantly based on customer profile rules. It dynamically processes the distance value inputted by the user to automatically compute whether free transport applies or if a standard delivery charge must be appended.

### 3. Administrator & Accounts Management
1. Centralized Customer Deposits Ledger: Serves as the primary collector for tracking the Salary-Earner Deposit Scheme interface, allowing verified salary earners to register under the 50% system threshold.
2. Supplier Operations Management: Handles the backend pipeline to register suppliers, log raw stock arrivals on credit, and track credit repayments over time.
3. Global Cross-User Reporting: Provides administrators full visibility to read consolidated activity, stock, and financial reports generated across all active user sessions.

---

## Verified Validation Mechanisms
The system implements strict frontend and backend validation rules to ensure business rule compliance:
* Pricing Restrictions: Enforces financial system rules ensuring the selling price is strictly greater than the baseline purchase unit cost.
* Structural Identifiers: Mandates clean structural parameters for valid Ugandan phone numbers and National Identification Numbers (NIN) during client enrollment.
* Complete Form Enforcement: Validates all incoming forms to guarantee zero empty or null values slip into the underlying database tables.

---

## System Technology Stack
* Frontend Architecture: HTML5, CSS3, Bootstrap Framework, and a light integration of custom JavaScript interactivity.
* Backend Framework: Python, Django MVC.
* Database Engine: SQLite.
* Environment Host: PythonAnywhere Web Platform.

---

## Verification & Deployment Guidelines

### Local Setup Instructions
To host and evaluate the source code repository locally:

1. Clone the project code repository:
```bash
   git clone [https://github.com/shadia-nalubega/nyondo4.git](https://github.com/shadia-nalubega/nyondo4.git)
   cd nyondoproject


---

## Evaluator Testing Credentials
To review the various Role-Based Access Control levels across the application interface:

* Administrator / Accounts View Access
  * Username/Email: shirat
  * Password: 1914

* Sales Attendant View Access
  * Username/Email: hanifa@gmail.com
  * Password: 2026

* Store Manager View Access
  * Username/Email: erick@gmail.com
  * Password: 2023