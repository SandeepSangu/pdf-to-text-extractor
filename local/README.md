# ✍️ Introduction

Throughout my experience working with clients from domains like `healthcare`, `insurance`, and `legal`, I often found myself curious about how certain backend document workflows functioned, especially in healthcare. While supporting these systems, I’d often get paged for incidents related to PDF pipelines: upload failures, script errors, or extraction gaps. At that stage, like many in support roles, we’re limited to handling outcomes rather than building or understanding the full solution.

Over time, as we gain more experience, build trust, and make people feel confident in our abilities, we gradually get the opportunity to be part of architecture discussions and solution design conversations. But that curiosity about how these pipelines actually work — from PDF upload to raw text extraction — always stayed with me.

So I decided to finally explore this from scratch, hands-on, and document it as a small weekend project. This repository reflects that journey — one that started with a question and ended with deeper insights, hands-on practice, and a working prototype. My hope is that others who share this curiosity will find this just as helpful.

## 🔍 What This Project Is

This project focuses on extracting structured data from scanned or uploaded PDFs using `AWS Textract`, starting with a local Python-based flow.

It simulates real-world use cases commonly seen in **healthcare**, **legal**, and **insurance** sectors — where physical documents like visit summaries or forms need to be digitized and stored in structured formats like databases.

The goal?
To break down what typically happens behind the scenes — from raw scanned input to clean, queryable output — using AWS-native services.

## 📄 Why Document Parsing Matters

In many industries, large volumes of information are still locked inside unstructured files, like PDFs or images.

For example:

* A **hospital** stores patient visit summaries scanned from handwritten or printed forms.
* An **insurance company** receives thousands of claim forms uploaded as PDFs every week.
* A **legal team** scans documents, contracts, and evidence that need to be searchable.

Without parsing, this data remains buried and unusable.

Document parsing — especially automated parsing — allows organizations to:

* Extract critical fields (like patient name, ID, diagnosis)
* Store them in structured systems (like `DynamoDB`)
* Enable downstream use (dashboards, alerts, summaries, etc.)

This project is a hands-on way to explore how that all comes together.

## 🧪 Local First: Why I Didn’t Start with Automation

While it’s tempting to jump straight into Lambda functions and triggers, I deliberately started with a **local-first mindset**.

Why?

* It helps build intuition: you understand exactly what Textract returns and how the parsing logic works.
* Easier to test and debug before handing things off to automation.
* You stay in control, tweaking and improving the logic before putting it behind an event trigger.

This mirrors how real-world teams prototype internally before scaling.

In my case:

* Took a sample patient visit summary in PDF format.
* Wrote a simple `Python` script to call `AWS Textract`.
* Parsed the returned lines into structured fields.
* The script automatically saved the extracted text as a `.txt` file inside `output-texts/`. I opened it to manually check if Textract returned the expected content.

That local foundation made automation smoother and more predictable.

## 🧱 Prerequisites

To follow along or replicate this project, ensure the following are in place:

* An `AWS` account (root access only used for visual verification)
* A dedicated IAM user with the following permissions:
  * `AmazonTextractFullAccess`
* `AWS CLI` installed and configured with the IAM user credentials
* `Python` 3.9+ installed
* `virtualenv` installed
* `VS Code` (or any preferred IDE)

You should also:

* Create a virtual environment (`python -m venv venv`) and activate it.
* Install boto3 (`pip install boto3`) and freeze dependencies into requirements.txt

## 📂 Project Structure

```bash
pdf-to-text-extractor/
├── input-pdfs/                # Local test PDFs
├── output-texts/              # Extracted raw text output
├── scripts/                   # Python scripts
│   └── extract_textract.py
├── venv/                      # Virtual environment (ignored in git)
├── requirements.txt
├── .gitignore
└── README.md                  # Project Documentation
```

Why `venv` and `requirements.txt` matter:

* Using a `venv/` keeps dependencies isolated — it’s a clean, repeatable habit in Python workflows.
* The `requirements.txt` file lists all the packages I used, so anyone can recreate the same environment instantly.

## 🧾 How the Script Works

The core script (`extract_textract.py`) does three things:

* **Reads** a PDF file placed in `input-pdfs/`
* **Sends** it to AWS Textract for text detection using Boto3
* **Writes** the returned content line-by-line to a new `.txt` file in `output-texts/`

It also introduces a small enhancement: whenever it encounters a line that starts with `Next Visit:`, it inserts an **extra line break** to separate patient records visually.

This makes the output easier to read and closer to a real-world segmentation.

## ▶️ Running the Script

From the root of the project, run the following:

```bash
source venv/Scripts/activate     # Activate virtual environment
python scripts/extract_textract.py  # Run the script
```

If successful, you’ll see messages like:

```bash
Processed 'patient-batch-2.pdf' → Output saved to 'output-texts/patient-batch-2.txt'
```

You can then open the `.txt` file to confirm everything was extracted correctly and that records are cleanly separated.

## ✅ Outcome and What’s Next

By the end of this phase, I had a working local prototype that:

* Pulled a PDF from `input-pdfs/`
* Extracted raw text using `AWS Textract`
* Saved it to `output-texts/`
* Gave me a chance to test and fine-tune the logic manually

This local-first phase gave me the space to deeply understand what each piece does before scaling up.

## 🔗 References

* [Python `boto3` Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
* [Amazon Textract Documentation](https://docs.aws.amazon.com/textract/latest/dg/what-is.html)
* [Setting up a Python Virtual Environment](https://docs.python.org/3/library/venv.html)
* [What is `requirements.txt`](https://pip.pypa.io/en/stable/user_guide/#requirements-files)

### 🔜 Coming Up in Part 2

We’ll build on this by:

* Triggering Textract via **AWS Lambda**
* Parsing and storing results in **DynamoDB**
* We’ll automate everything after the upload — using **AWS services** to handle extraction, parsing, and storage — just like a real-world backend system would.

📘 *Stay tuned for Part 2: “Building a Serverless PDF Ingestion Flow”*
