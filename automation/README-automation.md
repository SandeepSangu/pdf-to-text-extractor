# 🧭 Introduction

In [Part 1](https://dev.to/aws-builders/local-pdf-parsing-with-aws-textract-python-part-1-2iei), I walked through a local-first approach to extract text from patient PDFs using `AWS Textract` and `Python`. The flow was straightforward place a PDF into a folder, run a script, and save the extracted content to a `.txt` file. It helped validate Textract’s capabilities and gave a hands-on feel for the API — but everything was manual.

> This project wasn’t built for perfection, but for practice, learning, and getting real with `AWS` services.

In this second part, I wanted to push it a step further, simulating how such a process might work in a real backend environment by introducing automation, triggers, and storage. The goal: **automate the entire PDF parsing flow using serverless AWS services**.

> 📌 **Note**: The **PDF upload step is still manual** in this setup. In real-world applications, scanned PDFs are usually sent to cloud storage (like `S3`) automatically — through connected devices, backend apps, or scheduled jobs. For this hands-on practice, I’ve intentionally kept the upload step manual. But once a PDF lands in the bucket, everything else — processing, extraction, and storage — is fully automated.

## ⚙️ What This Part Covers

In this article, I’ll walk through how I used the following `AWS` services to automate the document extraction pipeline:

* **Amazon S3** — to hold the uploaded PDFs and trigger the processing flow
* **AWS Lambda** — to extract content from PDFs using Textract
* **Amazon DynamoDB** — to store structured patient records in a NoSQL format
* **CloudWatch Logs** — to track execution flow and debug when needed

The result is a working example of a **lightweight, event-driven backend** that reacts to PDF uploads and processes them automatically — no scripts to run, no manual parsing.

## 🏥 Real-World Scenario: Why Automating PDF Processing Matters

In industries like `healthcare`, `insurance`, and `legal`, documents often arrive in the form of scanned PDFs — visit summaries, claim forms, contracts — all packed with valuable information that needs to be extracted, stored, and used downstream.

Take hospitals for example: they deal with dozens or hundreds of patient summaries daily. Manually opening each file, reading the content, and entering it into a database isn’t just tedious — it’s error-prone and impossible to scale.

That’s where `automation` comes in.

Instead of treating PDFs as static files, the idea is to turn them into `event-driven inputs`. As soon as a document is uploaded, a backend system takes over — extracting key fields, storing them in structured formats like `DynamoDB`, and making them available for future use (like reporting, analysis, or alerts).

> 📌 This project simulates exactly that — using `AWS` services to mimic how such a backend might work. It's a hands-on demonstration of how automation bridges the gap between unstructured input and structured output.

By the end of this flow, what would’ve taken minutes per file happens in seconds, without manual intervention (aside from the initial upload, which we kept manual here for simplicity).

## 🗺️ Architecture Overview

To automate the document extraction flow, I used a combination of `AWS` services that work together in an event-driven pipeline.

Here's how it works at a high level:

1. **Amazon S3** acts as the dropzone — when a new PDF is uploaded, it automatically triggers the next step.
2. **AWS Lambda** is triggered by the S3 event and uses **Amazon Textract** to extract text from the PDF.
3. The extracted text is then parsed into structured fields (like `patient ID`, `diagnosis`, etc.).
4. These records are stored in **Amazon DynamoDB** — one item per patient.
5. **Amazon CloudWatch Logs** captures logs throughout the flow to help monitor and debug.
6. **IAM roles** are used to allow services to communicate securely and perform their actions.

## 🛠️ Step-by-Step Implementation

Here’s a quick walkthrough of how I set things up, in the order I tackled each piece. Nothing overly complex — just enough to get a fully working flow from upload to database entry.

### 📁 1. S3 Setup — Upload as a Trigger

I started by creating an S3 bucket to act as the dropzone for incoming PDFs. Every time a file is uploaded, it automatically triggers the next step.

To do that, I added an **S3 event trigger** to my Lambda function — specifically, an event of type `ObjectCreated`. No folder structure or file filters for now, just a basic setup to keep it simple.

> ⚠️ FYI: In production, you'd usually narrow this to a folder (prefix) or file type filter. For now, keeping it wide open helped test faster.

### ⚙️ 2. Lambda Function — Extract and Parse on the Fly

Once a new PDF lands in the bucket, `Lambda` takes over.

The function:

* Pulls the PDF from `S3`
* Sends it to **Amazon Textract**
* Parses the returned lines into structured fields
* Stores each parsed record into **DynamoDB**

> `Amazon Textract` offers different operations depending on your document type.
> In this case, I used the [`detect_document_text`](https://docs.aws.amazon.com/textract/latest/dg/how-it-works-detecting.html) API — it’s fast, synchronous, and works well for clean printed documents like summaries or forms.
>
> For other use cases (like extracting forms or tables), you can explore [Textract’s available operations here](https://docs.aws.amazon.com/textract/latest/dg/how-it-works.html).

### 🧾 3. Textract Output Processing — Turning Lines Into Records

`Textract` returns blocks of text as separate lines. I looped through each line and looked for patterns like `Patient Name:`, `Diagnosis:`, `Next Visit:` etc.

Whenever a new `Patient Name` appeared, I considered that the start of a new record.

This basic parsing logic worked well for my structured PDFs — and it gave me clean, key-value entries ready to store.

> ✍️ The format of your source PDF matters. If you're working with messy scans or inconsistent layouts, you’ll likely need a smarter parser or post-processing.

### 🗂️ 4. DynamoDB Storage — Saving Each Record

Each parsed patient record is stored as a new item in my `DynamoDB` table called `PatientRecords`.

I used `PatientID` as the partition key. So before inserting each item, I made sure to normalize the field (`Patient ID` → `PatientID`) and skip any record that didn't include it.

This way, only valid patient records are saved.

### 📜 5. Monitoring with CloudWatch Logs

Every step — from event trigger to Textract response to final record insert — is logged automatically in `CloudWatch Logs`.

This was super helpful during testing. For example, I could easily see:

* If Textract succeeded
* What records were parsed
* If anything failed validation (like missing a Patient ID)

Just head to the `Lambda` > `Monitor` tab to view the logs in context.

### 🔐 6. IAM Roles — Permissions That Make It Work

To connect all these services securely, I created an **IAM role for the Lambda function**.

This role had the following policies attached:

* `AmazonS3ReadOnlyAccess`
* `AmazonTextractFullAccess`
* `AmazonDynamoDBFullAccess`
* `AWSLambdaBasicExecutionRole`

> ⚠️ For this project, I also used an IAM user with broad access to set things up.
> But in real-world scenarios, always follow the **principle of least privilege** — give only the permissions that are needed for the task, and nothing more.

### 📸 Demo Output & Screenshots

Let’s walk through what happens when the workflow runs end-to-end.

Once a PDF is uploaded, the automation kicks in — `AWS Lambda` gets triggered, calls `Textract` to extract text, parses the extracted lines, and writes structured patient records into `DynamoDB`.

Here’s the **architecture diagram** that visually represents this flow:

![Image description](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/yjzq107g3ykjfw1jue1q.png)

Below, you’ll see a sample view of the `PatientRecords` DynamoDB table — confirming that our extracted fields like patient name, ID, diagnosis, and next visit date have been stored properly:

![Image description](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/tj2obbma9wq6f966mge8.png)

You can also view the detailed execution logs in **CloudWatch**, which helps confirm the flow — from trigger to text extraction and database insertion. This is especially useful during debugging or validation in real-time scenarios.

![Image description](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/q6rchvkpkargpqiv4u7a.png)

Finally, here’s the raw output file that was extracted and stored locally during testing:

![Image description](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/bmo8f0ytvc7hy0jsep6y.png)

### 🧠 Lessons Learned Along the Way

Like most hands-on projects, this one came with a few surprises and learning moments.

* **Lambda Timeouts:**
  Initially, the `Lambda` function timed out while waiting for `Textract` to finish. Increasing the timeout duration solved it, but it reminded me to always plan for longer-running tasks when calling asynchronous services.

* **Parsing Gotchas:**
  While `Textract` extracted text just fine, breaking it into structured records required some tweaking — especially for lines that didn’t follow a perfect format (like a missing `Patient ID`). Adding logic to skip incomplete entries helped keep things clean.

* **IAM Permissions:**
  The setup was smoother by assigning full access policies to the `IAM` user and `Lambda` role, but in real-world scenarios, we’d follow the **least privilege** principle to secure each component properly.

### ✅ Final Thoughts

This project helped me explore how to bring automation into document parsing using AWS's serverless services. By combining `S3`, `Lambda`, `Textract`, and `DynamoDB`, I was able to simulate a lightweight backend workflow — one that reflects how real-world systems might handle scanned documents, such as patient summaries.

While the initial PDF upload and script execution were still done manually for simplicity, everything that followed — from text extraction to structured storage — was `event-driven` and fully automated.

This setup lays the groundwork for more advanced ideas, like:

* Adding search or filter capabilities on top of DynamoDB
* Integrating analytics dashboards
* Using generative AI to summarize or classify extracted content

Thanks for following along! 🙌
I hope this gives you a practical feel for how serverless workflows can streamline everyday processes.

**Feel free to share your thoughts, ask questions, or [fork the repo](https://github.com/SandeepSangu/pdf-to-text-extractor) to try it out yourself!**
