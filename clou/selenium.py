pip install selenium google-cloud-storage webdriver-manager

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from google.cloud import storage
import shutil

# Google Cloud Storage bucket name
BUCKET_NAME = 'your-gcs-bucket-name'  # Replace with your bucket name
GCS_UPLOAD_PATH = 'drug_shortages.csv'  # File path in the GCS bucket

# Set Chrome options for headless browser
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")

# Set up the ChromeDriver with Service and ChromeOptions
driver_service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=driver_service, options=chrome_options)

# Set the path for the file to be downloaded locally
download_dir = "/tmp"  # Using /tmp directory, Cloud Run's writable space

if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# Set download preferences to save the file in the specified directory
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

# Initialize the browser again with updated options
driver = webdriver.Chrome(service=driver_service, options=chrome_options)

# Navigate to the FDA Drug Shortages page
url = 'https://dps.fda.gov/drugshortages'
driver.get(url)

# Wait for the page to load completely
time.sleep(5)

try:
    # Find the "Download Current Drug Shortages" button by its text
    download_button = driver.find_element(By.PARTIAL_LINK_TEXT, 'Download Current Drug Shortages')
    
    # Click the download button
    download_button.click()

    # Wait for the file to download (adjust the time based on your file size)
    time.sleep(10)
    print(f"File downloaded successfully to {download_dir}.")
    
except Exception as e:
    print(f"Error: {e}")

# Close the browser
driver.quit()

# After downloading, upload the file to Google Cloud Storage
def upload_to_gcs():
    # Initialize the GCS client
    client = storage.Client()

    # Specify the bucket and file
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(GCS_UPLOAD_PATH)

    # Upload the file
    local_file_path = os.path.join(download_dir, 'drug_shortages.csv')  # Specify the downloaded file path
    blob.upload_from_filename(local_file_path)
    print(f"File uploaded successfully to GCS bucket: {BUCKET_NAME}/{GCS_UPLOAD_PATH}")

# Call the upload function
upload_to_gcs()
