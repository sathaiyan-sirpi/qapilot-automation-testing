🚀 QA Pilot Application - Automation Testing Framework

This project contains an end-to-end automation testing framework developed for the **QA Pilot Web Application** using **Python, Selenium WebDriver, Pytest, and Page Object Model (POM)** architecture.

📌 Project Overview

The framework automates critical login workflows and validates application behavior through positive, negative, UI, boundary, and security test scenarios.

🛠️ Tech Stack

* Python
* Selenium WebDriver
* Pytest
* Page Object Model (POM)
* WebDriver Manager
* Pytest HTML Reports

✅ Features

* Automated Login Functionality Testing
* Positive & Negative Test Scenarios
* UI Element Validation
* Security Testing (SQL Injection & XSS Inputs)
* Boundary Value Testing
* Screenshot Capture on Test Failure
* HTML Test Reports Generation
* Headless & Headed Browser Execution

📂 Framework Structure

text
├── pages/
│   └── login_page.py
├── utils/
│   └── helpers.py
├── tests/
├── screenshots/
├── reports/
├── conftest.py
├── pytest.ini
└── requirements.txt
```

🔍 Test Coverage

* Valid Login
* Invalid Login
* Empty Fields Validation
* Incorrect Password Validation
* Invalid User Validation
* SQL Injection Attempts
* Cross-Site Scripting (XSS) Attempts
* Long Input Validation
* Special Character Testing
* UI Component Verification

▶️ Run Tests

```bash
pytest
```

Run in Headless Mode

```bash
pytest --headless
```

Generate HTML Report

```bash
pytest --html=reports/test_report.html --self-contained-html


📊 Key Highlights

* Built using industry-standard Page Object Model (POM)
* Reusable utility functions and centralized test data
* Automatic screenshot capture for failed test cases
* Easy maintenance and scalability for future test suites
