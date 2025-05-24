import boto3
import time
import os

# --- Configuration ---
AWS_REGION = "us-east-1"
S3_BUCKET = "pdf-to-text-demo-sandeep"  # Replace with your actual bucket name
PDF_FILE = "sample_patient_records.pdf"
S3_OBJECT_KEY = PDF_FILE
OUTPUT_FILE = "output-texts/extracted_text.txt"

# Initialize Textract and S3 clients
textract_client = boto3.client("textract", region_name=AWS_REGION)
s3_client = boto3.client("s3", region_name=AWS_REGION)

def upload_pdf_to_s3():
    """Upload local PDF to the configured S3 bucket."""
    file_path = os.path.join("input-pdfs", PDF_FILE)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    print(f"Uploading {PDF_FILE} to S3 bucket {S3_BUCKET}...")
    s3_client.upload_file(file_path, S3_BUCKET, S3_OBJECT_KEY)
    print("Upload complete.\n")

def start_textract_job():
    """Start an asynchronous Textract text detection job."""
    print(f"Starting Textract job for {S3_OBJECT_KEY}...")

    response = textract_client.start_document_text_detection(
        DocumentLocation={
            "S3Object": {
                "Bucket": S3_BUCKET,
                "Name": S3_OBJECT_KEY
            }
        }
    )

    job_id = response["JobId"]
    print(f"Textract job started. Job ID: {job_id}\n")
    return job_id

def poll_textract_job(job_id):
    """Poll the Textract job status until it's complete."""
    print("Waiting for Textract job to complete...\n")

    while True:
        response = textract_client.get_document_text_detection(JobId=job_id)
        status = response["JobStatus"]

        if status == "SUCCEEDED":
            print("Textract job completed successfully.\n")
            return response
        elif status == "FAILED":
            raise Exception("Textract job failed.")
        else:
            print(f"Job status: {status}... waiting...")
            time.sleep(3)

def extract_text_from_response(response):
    """Parse the Textract response and write detected text lines to a local file."""
    blocks = response.get("Blocks", [])
    lines = [block["Text"] for block in blocks if block["BlockType"] == "LINE"]

    if not lines:
        print("No text detected in document.")
        return

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")
            if "Next Visit" in line:
                f.write("\n")  # Add a blank line after each patient block

    print(f"Extracted text written to {OUTPUT_FILE}\n")

if __name__ == "__main__":
    upload_pdf_to_s3()
    job_id = start_textract_job()
    response = poll_textract_job(job_id)
    extract_text_from_response(response)
