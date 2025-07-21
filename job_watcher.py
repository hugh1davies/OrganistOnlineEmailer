import os
import time
import re
import smtplib
import schedule
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ==== CONFIGURATION ====
SEEN_JOBS_FILE = "seen_jobs.txt"
CHROMEDRIVER_PATH = r"/path/to/chromedriver"  # TODO: Replace with your actual path
MAX_RETRIES = 3

# ==== SEARCH SETTINGS ====
POSTCODE = ""  # TODO: Set your preferred postcode

# ==== EMAIL SETTINGS ====
SENDER_EMAIL = "your_email@example.com"
RECEIVER_EMAILS = ["recipient1@example.com", "recipient2@example.com"]
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
SMTP_USERNAME = "your_email@example.com"
SMTP_PASSWORD = "your_smtp_password"
# =========================


def init_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(CHROMEDRIVER_PATH)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"🚗 Starting WebDriver (Attempt {attempt})...")
            return webdriver.Chrome(service=service, options=options)
        except Exception as e:
            print(f"❌ WebDriver init failed: {e}")
            time.sleep(2)

    raise RuntimeError("Failed to initialize WebDriver.")


def fetch_jobs_text_based():
    driver = init_driver()
    wait = WebDriverWait(driver, 20)
    driver.get("https://organistsonline.org/required")

    try:
        close_ads = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "/html/body/form/div[3]/div[2]/div[2]/div[3]/p[2]/a")
        ))
        close_ads.click()
        time.sleep(1)
    except Exception:
        pass

    try:
        country_dropdown = driver.find_element(By.XPATH, "/html/body/form/div[3]/div[2]/div/div[1]/p[1]/select[1]")
        for option in country_dropdown.find_elements(By.TAG_NAME, "option"):
            if option.text.strip() == "United Kingdom":
                option.click()
                break

        postcode_input = driver.find_element(By.XPATH, "/html/body/form/div[3]/div[2]/div/div[1]/p[1]/input")
        postcode_input.clear()
        postcode_input.send_keys(POSTCODE)

        distance_dropdown = driver.find_element(By.XPATH, "/html/body/form/div[3]/div[2]/div/div[1]/p[1]/select[2]")
        for option in distance_dropdown.find_elements(By.TAG_NAME, "option"):
            if "10" in option.text:
                option.click()
                break

        hide_filled_checkbox = driver.find_element(By.XPATH, "/html/body/form/div[3]/div[2]/div/div[1]/p[2]/input")
        if not hide_filled_checkbox.is_selected():
            hide_filled_checkbox.click()

        search_button = driver.find_element(By.XPATH, "/html/body/form/div[3]/div[2]/div/div[1]/p[3]/a")
        search_button.click()
    except Exception as e:
        print("⚠️ Form interaction failed:", e)

    time.sleep(3)

    try:
        content_div = driver.find_element(By.XPATH, "/html/body/form/div[3]/div[2]/div/div[2]")
        job_text = content_div.text
    except Exception as e:
        print("❌ Failed to extract job listings:", e)
        driver.quit()
        return []

    driver.quit()

    lines = job_text.splitlines()
    job_blocks = []
    block = []
    seen = set()

    for line in lines:
        line = line.strip()
        if not line or line.upper() == "OPEN":
            continue
        block.append(line)
        if re.match(r"^£\s?\d+(\.\d+)?|£\s?NEG$", line, re.IGNORECASE):
            job_text_block = " | ".join(block)
            if "Sunday" in job_text_block and job_text_block not in seen:
                job_blocks.append(job_text_block)
                seen.add(job_text_block)
            block = []

    return job_blocks


def load_seen_jobs():
    if not os.path.exists(SEEN_JOBS_FILE):
        return set()
    with open(SEEN_JOBS_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())


def save_seen_jobs(jobs):
    with open(SEEN_JOBS_FILE, "w", encoding="utf-8") as f:
        for job in jobs:
            f.write(job + "\n")


def clean_title(raw_title):
    title = raw_title.strip().lower()
    if "eucharist" in title:
        return "Organist for Sunday Eucharist"
    elif "choir" in title:
        return "Organist with Choir"
    elif "morning" in title:
        return "Sunday Morning Service"
    elif "service" in title:
        return "Organist for Church Service"
    else:
        return "Sunday Organist"


def format_job(job_raw, is_new=False):
    parts = job_raw.split(" | ")
    if len(parts) < 6:
        return None

    raw_title, church, town, date, time_str, fee = parts[:6]
    cleaned_title = clean_title(raw_title)

    try:
        dt = datetime.strptime(date.strip(), "Sunday, %B %d, %Y")
        formatted_date = dt.strftime("%A, %d %B %Y")
    except ValueError:
        formatted_date = date.strip()

    new_flag = " 🔔 NEW!" if is_new else ""
    return f"""
🎵 *{cleaned_title}{new_flag}*  
📍 {church.strip()} - {town.strip()}  
📅 {formatted_date}  
🕒 {time_str.strip()}  
Fee: {fee.strip()}  
"""


def build_email_body(jobs, new_jobs_set):
    greeting = "Hello,"
    intro = "A new job listing has been posted. See details below:"
    outro = "Kind regards,\nAutomated Job Bot"

    body = f"{greeting}\n\n{intro}\n\n"
    for job in jobs:
        is_new = job in new_jobs_set
        formatted = format_job(job, is_new)
        if formatted:
            body += formatted + "\n"

    body += f"\n{outro}\n"
    return body


def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = ", ".join(RECEIVER_EMAILS)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("✅ Email sent.")
    except Exception as e:
        print("❌ Email sending failed:", e)


def check_for_new_listings():
    print("🔄 Checking for new jobs...")
    try:
        current_jobs = fetch_jobs_text_based()
        seen_jobs = load_seen_jobs()
        new_jobs = set(current_jobs) - seen_jobs

        if new_jobs:
            print(f"📬 New jobs found: {len(new_jobs)}")
            email_body = build_email_body(current_jobs, new_jobs)
            send_email(
                subject="🔔 New Organist Listing Posted!",
                body=email_body
            )
            save_seen_jobs(current_jobs)
        else:
            print("✅ No new listings.")
    except Exception as e:
        print("🚨 Error during check:", e)


if __name__ == "__main__":
    print("🔁 Job monitor started. Checking every 10 minutes.")
    schedule.every(10).minutes.do(check_for_new_listings)

    while True:
        schedule.run_pending()
        time.sleep(60)
