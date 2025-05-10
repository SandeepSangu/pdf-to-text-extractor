import boto3
import time
import os

# Initialize Textract client
textract = boto3.client('textract')

# Define input and output paths
input_folder = "input-pdfs"
output_folder = "output-texts"

# Make sure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Pick the first PDF file in the input folder
for file_name in os.listdir(input_folder):
    if file_name.endswith(".pdf"):
        input_path = os.path.join(input_folder, file_name)
        output_path = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}.txt")

        # Read file and call Textract
        with open(input_path, "rb") as document:
            response = textract.detect_document_text(Document={'Bytes': document.read()})

        # Extract lines of text
        lines = []
        for block in response['Blocks']:
            if block['BlockType'] == 'LINE':
                lines.append(block['Text'])

        # Write to output file
        with open(output_path, "w") as output_file:
            for line in lines:
                output_file.write(line + "\n")
                if line.strip().startswith("Next Visit:"):
                    output_file.write("\n")

        print(f"Processed '{file_name}' → Output saved to '{output_path}'")
        break  # Only process one file for now
