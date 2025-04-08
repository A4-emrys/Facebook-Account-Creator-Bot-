import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests

# Updated path to chromedriver.exe
service = Service(r"C:\Users\emrys\Desktop\chromedriver-win64\chromedriver.exe")
options = Options()
options.add_argument("--headless")  # Optional: remove this line if you want to see the browser window

# Initialize the WebDriver
driver = webdriver.Chrome(service=service, options=options)

# Function to generate a random first name
def generate_random_first_name():
    return random.choice(["John", "Jane", "Michael", "Emily", "David", "Sarah"])

# Function to generate a random last name
def generate_random_last_name():
    return random.choice(["Doe", "Smith", "Johnson", "Williams", "Brown", "Jones"])

# Function to get a temporary email from ptct.net (using requests)
def get_temp_email():
    response = requests.get("https://www.ptct.net/api/email")
    if response.status_code == 200:
        email_data = response.json()
        email = email_data["email"]
        password = email_data["password"]
        return email, password
    else:
        print("Error getting temporary email")
        return None, None

# Function to get the OTP from the temp email inbox
def get_otp_from_email(email, password):
    # Log in to the ptct.net email service and fetch OTP
    login_data = {
        "email": email,
        "password": password
    }
    login_response = requests.post("https://www.ptct.net/api/login", data=login_data)
    if login_response.status_code == 200:
        inbox_response = requests.get("https://www.ptct.net/api/inbox", params={"email": email})
        if inbox_response.status_code == 200:
            inbox_data = inbox_response.json()
            for email in inbox_data:
                if "Facebook" in email["subject"]:
                    # Extract OTP from the email body
                    otp = extract_otp_from_email_body(email["body"])
                    return otp
    return None

# Function to extract OTP from email body (simple regex or string search)
def extract_otp_from_email_body(body):
    # Assuming OTP is a 6-digit number in the email body
    import re
    match = re.search(r"\b\d{6}\b", body)
    if match:
        return match.group(0)
    return None

# Function to register a Facebook account using generated info
def register_facebook_account(email, password):
    driver.get("https://www.facebook.com/r.php")

    # Fill in the registration form
    first_name = generate_random_first_name()
    last_name = generate_random_last_name()
    driver.find_element(By.NAME, "firstname").send_keys(first_name)
    driver.find_element(By.NAME, "lastname").send_keys(last_name)
    driver.find_element(By.NAME, "reg_email__").send_keys(email)
    driver.find_element(By.NAME, "reg_passwd__").send_keys(password)

    # Select the birthdate (using random values)
    driver.find_element(By.NAME, "birthday_day").send_keys(str(random.randint(1, 28)))  # Day
    driver.find_element(By.NAME, "birthday_month").send_keys(str(random.randint(1, 12)))  # Month
    driver.find_element(By.NAME, "birthday_year").send_keys(str(random.randint(1990, 2005)))  # Year

    # Select gender (randomly choose Male or Female)
    gender = random.choice(["2", "1"])  # 1 = Female, 2 = Male
    driver.find_element(By.NAME, "sex").click()

    # Submit the form
    driver.find_element(By.NAME, "websubmit").click()

    # Wait for the OTP to arrive
    time.sleep(5)

    # Get OTP from the temp email
    otp = get_otp_from_email(email, password)
    if otp:
        # Enter the OTP
        driver.find_element(By.NAME, "confirm").send_keys(otp)
        driver.find_element(By.NAME, "confirm").send_keys(Keys.RETURN)
        print(f"Account registered successfully with email: {email}")
    else:
        print("OTP not found. Registration failed.")

# Main script execution
if __name__ == "__main__":
    # Get a temporary email and password
    email, password = get_temp_email()

    if email and password:
        print(f"Using email: {email} for registration.")
        register_facebook_account(email, password)
    else:
        print("Failed to obtain a temporary email.")

    # Close the browser
    driver.quit()

