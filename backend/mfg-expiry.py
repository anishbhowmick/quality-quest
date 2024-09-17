from google.cloud import vision
import re
import csv
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json

# Set the path to your service account key file (JSON)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'C:\Users\Anish\Desktop\OCR\ocr-detection-435811-ab00322e2932.json'

# Initialize Google Cloud Vision client
client = vision.ImageAnnotatorClient()

# Extract text from image using Google Cloud Vision API
def extract_text_google(image_path):
    with open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if response.error.message:
        raise Exception(f'{response.error.message}')
    
    if texts:
        return texts[0].description  # Full text from the image
    else:
        return ''

# Extract manufacturing and expiry dates using regex
def extract_dates(text):
    # Match dates in various formats including month names
    date_pattern = r'(\d{2}/\d{4})|(\d{2}/\d{2}/\d{4})|(\d{4}-\d{2}-\d{2})|(\d{2}/\d{2}/\d{2})|(\d{2}-\d{4})|(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\b \d{4})|(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\b \d{2})'
    matches = re.findall(date_pattern, text, re.IGNORECASE)
    
    # Convert month names to numerical values
    month_conversion = {
        'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05', 'jun': '06',
        'jul': '07', 'aug': '08', 'sep': '09', 'sept': '09', 'oct': '10', 'nov': '11', 'dec': '12',
        'january': '01', 'february': '02', 'march': '03', 'april': '04', 'june': '06',
        'july': '07', 'august': '08', 'september': '09', 'october': '10', 'november': '11', 'december': '12'
    }
    
    converted_dates = set()
    for match in matches:
        date = next(filter(None, match))
        if re.match(r'\d{2}/\d{2}/\d{2}', date):
            day, month, year = date.split('/')
            year = '20' + year  # Assuming the year is in the 2000s
            converted_dates.add(f'{day}/{month}/{year}')
        elif re.match(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\b \d{4}', date, re.IGNORECASE):
            month, year = date.split()
            month = month_conversion[month.lower()]
            converted_dates.add(f'{month}/{year}')
        elif re.match(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\b \d{2}', date, re.IGNORECASE):
            month, day = date.split()
            month = month_conversion[month.lower()]
            year = '20' + day  # Assuming the year is in the 2000s
            converted_dates.add(f'{day}/{month}/{year}')
        else:
            converted_dates.add(date)
    
    # Validate dates
    valid_dates = []
    for date in converted_dates:
        try:
            if re.match(r'\d{2}/\d{4}', date) or re.match(r'\d{2}-\d{4}', date):
                month, year = re.split(r'[-/]', date)
                datetime(int(year), int(month), 1)  # Validate month and year
            elif re.match(r'\d{2}/\d{2}/\d{4}', date):
                day, month, year = date.split('/')
                datetime(int(year), int(month), int(day))  # Validate day, month, and year
            elif re.match(r'\d{4}-\d{2}-\d{2}', date):
                year, month, day = date.split('-')
                datetime(int(year), int(month), int(day))  # Validate year, month, and day
            
            # Check if the year is 2000 or later
            if int(year) >= 2000:
                valid_dates.append(date)
        except ValueError:
            continue  # Skip invalid dates
    
    return valid_dates

# Extract additional months information
def extract_months_info(text):
    # Regular expression to match phrases like "best before 24 months" or "use before 24 months"
    months_pattern = r'\b(?:best before|use before|before|Best before|Use before) (\d{1,2}) months?\b'
    matches = re.findall(months_pattern, text, re.IGNORECASE)
    
    if matches:
        # Convert matched months to integers
        months = [int(match) for match in matches]
        print(f"Detected expiry Months Info: {months}")
        return months
    else:
        # print("No valid months info found.")
        return None

# Store dates in a CSV file
# def store_to_csv(data, file_name='dates.csv'):
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Manufacturing Date", "Expiry Date"])
        writer.writerows(data)

# Main function to scan image, extract dates, and save to CSV
def scan_and_store_dates(image_path):
    extracted_text = extract_text_google(image_path)
    dates = extract_dates(extracted_text)
    months_info = extract_months_info(extracted_text)
    
    result = {
        "dates": [],
        "months_info": months_info
    }

    if dates:
        dates.sort(key=lambda date: int(re.search(r'\d{4}', date).group()))
        
        if len(dates) == 1:
            manufacturing_date = dates[0]
            expiry_date = ''
            
            if months_info:
                month, year = map(int, manufacturing_date.split('/'))
                expiry_date = (datetime(year, month, 1) + relativedelta(months=months_info[0])).strftime('%m/%Y')
            
            date_pairs = [(manufacturing_date, expiry_date)]
        else:
            date_pairs = [(dates[i], dates[i+1]) for i in range(0, len(dates), 2) if i+1 < len(dates)]
        
        result["dates"] = date_pairs
        
        for manufacturing_date, expiry_date in date_pairs:
            print(f"Manufacturing Date: {manufacturing_date} , Expiry Date: {expiry_date}")
    else:
        print("No dates found in the image.")

    return result

if __name__ == "__main__":
    import sys
    image_path = sys.argv[1]  # Get image path from the command-line arguments

    date_extraction_result = scan_and_store_dates(image_path)

    # Print the result as JSON so that it can be captured by the server
    # print(json.dumps(date_extraction_result))
