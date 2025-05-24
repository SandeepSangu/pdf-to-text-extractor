import json
import boto3

textract = boto3.client('textract')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('PatientRecords')

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    bucket = event['Records'][0]['s3']['bucket']['name']
    document = event['Records'][0]['s3']['object']['key']
    print(f"Processing file: {document} from bucket: {bucket}")

    # Start Textract sync job
    response = textract.detect_document_text(
        Document={'S3Object': {'Bucket': bucket, 'Name': document}}
    )

    print("Textract response received.")
    lines = [block['Text'] for block in response['Blocks'] if block['BlockType'] == 'LINE']
    print(f"Extracted {len(lines)} lines from Textract.")

    # Parse patient records (no --- separator, look for 'Patient Name' to start a new record)
    records = []
    current = {}

    for line in lines:
        if line.startswith("Patient Name"):
            if current:
                records.append(current)
                current = {}
        if ':' in line:
            key, value = line.split(':', 1)
            current[key.strip()] = value.strip()
    
    if current:
        records.append(current)

    print(f"Parsed {len(records)} patient records.")

    for record in records:
        print("Storing record:", record)
        if 'Patient ID' in record:
            record['PatientID'] = record.pop('Patient ID')
            table.put_item(Item=record)
        else:
            print("Skipped record without Patient ID:", record)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f"{len(records)} records inserted into DynamoDB from {document}"
        })
    }