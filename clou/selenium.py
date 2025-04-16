pip install selenium google-cloud-storage webdriver-manager

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import os
import shutil

# Set Chrome options (to avoid unnecessary browser popups)
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run browser in headless mode (without UI)
chrome_options.add_argument("--no-sandbox")  # Helps with running inside Docker

# Set up ChromeDriver with Service and ChromeOptions
driver_service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=driver_service, options=chrome_options)

# Create a directory to save the downloaded file
download_dir = "/path/to/your/directory"  # Specify the local directory where you want to save the file

if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# Set the download directory in Chrome options
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,  # Set the download folder
    "download.prompt_for_download": False,       # Avoid download prompt
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

# Initialize the browser again with the updated options
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

    # Wait for the file to download (this might need adjustment depending on the file size)
    time.sleep(10)  # You may want to adjust this time based on your file's download speed
    print(f"File downloaded successfully to {download_dir}.")
except Exception as e:
    print(f"Error: {e}")

# Close the browser
driver.quit()
