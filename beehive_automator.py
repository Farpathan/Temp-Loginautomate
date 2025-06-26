import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def setup_driver():
    """Sets up the Selenium ChromeDriver with maximum stability options."""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        # --- NEW STABILITY FLAGS ---
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--remote-debugging-port=9222")
        # ---
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.binary_location = "/usr/bin/chromium-browser"
        service = Service(executable_path='/usr/bin/chromedriver')
        
        print("INFO: Attempting to start ChromeDriver with new stability flags...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("INFO: ChromeDriver started successfully.")
        return driver
    except Exception as e:
        print(f"FATAL: Error setting up ChromeDriver: {e}")
        return None

def run_automation(driver, username, password, action, is_dry_run):
    """Handles the entire automation workflow."""
    try:
        driver.get("https://globalstephcm.beehivehcm.com/")
        wait = WebDriverWait(driver, 30)
        
        username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        username_field.send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, '#form0 button[type="submit"]').click()

        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "modal-dialog")))
        
        try:
            no_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@onclick, 'cancelattendance')]")))
            no_button.click()
        except TimeoutException:
            pass

        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn-me"))).click()
        
        button_id, action_text = ("btnTimeIn", "Time In") if action == "TimeIn" else ("btnTimeOut", "Time Out")
        action_button = wait.until(EC.element_to_be_clickable((By.ID, button_id)))

        if is_dry_run == 'True':
            print(f"SUCCESS (Dry Run): Found '{action_text}' button for {username}.")
            return True
        
        action_button.click()
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-bb-handler='ok']"))).click()
        print(f"SUCCESS: {action_text} was successful for user {username}.")
        return True
    except Exception as e:
        print(f"ERROR: An error occurred for user {username}: {e}")
        driver.save_screenshot(f'error_screenshot_{username}.png')
        return False

def main():
    if len(sys.argv) != 5:
        sys.exit(1)

    username, password, action, is_dry_run = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    
    driver = setup_driver()
    if driver:
        success = False
        try:
            success = run_automation(driver, username, password, action, is_dry_run)
        finally:
            driver.quit()
        sys.exit(0 if success else 1)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
