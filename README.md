# JIRA Failure Intelligence Pipeline

An AI-agent-driven workflow designed to turn firmware test failure HTML reports into structured JIRA bug drafts.

## 🚀 Overview

This repository provides a lean, modular system for engineers to automate the triage of firmware failures. It uses a combination of a Python-based HTML parser and specialized AI instructions to extract test steps, log evidence, and failure context directly from pytest-style reports.

## 📂 Project Structure

```text
jira_failure/
├── skill.md               # Master AI Agent workflow (follow this)
├── helpers.py             # Python CLI for structured HTML parsing
├── configs/
│   └── config.yaml        # Pipeline and JIRA default configurations
├── prompts/
│   ├── html_extraction.md # Instructions for parsing banners and logs
│   ├── log_extraction.md  # How to handle linked log files
│   ├── draft_generation.md# JIRA markdown and JSON schema rules
│   └── examples.md        # Reference input/output examples
└── sample_1.html          # Sample report for testing the pipeline
```

## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/computiphy/jira_failure.git
   cd jira_failure
   ```

2. Install dependencies:
   ```bash
   pip install beautifulsoup4 lxml requests
   ```

## 📖 How to Use

### 1. Using an AI Agent (Cursor, Antigravity, Claude Code)
Simply provide an HTML report and ask the agent to follow the workflow:
> *"Follow the workflow in skill.md to analyze [your_report.html] and generate a JIRA draft."*

The agent will automatically:
- Execute the parser (`helpers.py`)
- Locate errors and relevant log snippets
- Draft a formatted `jira_draft.md` for your review

### 2. Using the CLI Directly
You can use the helper script to extract data manually:
```bash
# Extract everything as JSON
python helpers.py parse report.html

# Extract only failed test cases
python helpers.py failed report.html

# List linked log file paths
python helpers.py logs report.html
```

## 🤖 JIRA Integration
The pipeline generates a `jira_draft.json` file designed to be consumed by a JIRA MCP server. While the MCP harness is included in the workflow, final ticket creation currently requires engineer approval of the markdown draft.

## 📄 License
This project is for firmware engineering assistance and internal triage automation.
