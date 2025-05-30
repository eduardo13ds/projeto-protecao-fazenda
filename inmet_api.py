from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time

# Set up Chrome options for automatic downloads
chrome_options = Options()
prefs = {
    "download.default_directory": "/path/to/download/folder",  # Change this to your desired path
    "download.prompt_for_download": False,
    "directory_upgrade": True
}
chrome_options.add_experimental_option("prefs", prefs)

# Initialize the driver
driver = webdriver.Chrome(options=chrome_options)

try:
    # Open the webpage
    driver.get("https://tempo.inmet.gov.br/TabelaEstacoes/A807")  # Replace with the actual URL

    # Wait for the page to load
    time.sleep(3)

    # Find and click the button to download CSV
    download_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Baixar CSV')]")  # Adjust selector as needed
    ActionChains(driver).move_to_element(download_button).click().perform()

    # Wait for download to complete
    time.sleep(5)
finally:
    driver.quit()