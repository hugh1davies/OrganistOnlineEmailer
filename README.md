# 🎹 OrganistOnlineEmailer 🎶

Takes Organist Online jobs within a specified radius of a postcode and emails any new listings. 📬

---

## 🚀 Overview

This script monitors [organistsonline.org](https://organistsonline.org/required) for new Sunday organist job listings within a specified postcode radius in the UK. It automatically detects new listings and sends email notifications to configured recipients. 📅✨

---

## 🎯 Features

- 🔍 Searches for Sunday organist jobs within a set radius of a UK postcode  
- 🚫 Automatically filters out previously seen jobs  
- 📧 Sends email alerts with detailed job information  
- ⏰ Runs continuously, checking every 10 minutes  

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository

```bash
git clone https://github.com/yourusername/OrganistOnlineEmailer.git
cd OrganistOnlineEmailer
```

### 2️⃣ Install dependencies

Make sure you have Python 3.7+ installed.

```bash
pip install -r requirements.txt
```

### 3️⃣ Download ChromeDriver

Download ChromeDriver matching your Chrome version from:  
https://chromedriver.chromium.org/downloads

Place the executable somewhere accessible on your system.

Update the `CHROMEDRIVER_PATH` variable in `job_watcher.py` with the full path to your ChromeDriver executable. 🖥️⚙️

### 4️⃣ Configure script variables

Edit the top of `job_watcher.py` and update the placeholders:

```python
POSTCODE = ""  # Your target postcode
SENDER_EMAIL = "your_email@example.com"
RECEIVER_EMAILS = ["recipient1@example.com", "recipient2@example.com"]
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
SMTP_USERNAME = "your_email@example.com"
SMTP_PASSWORD = "your_smtp_password"
CHROMEDRIVER_PATH = r"/full/path/to/chromedriver"
```

⚠️ **Important:**  
Use an app-specific password if your email provider requires two-factor authentication.

### 5️⃣ Run the script

```bash
python job_watcher.py
```

The script will check for new jobs every 10 minutes and send email notifications when new listings are found. 🔄📩

---

## 📧 Example Email Output

```
🎵 Organist for Sunday Eucharist 🔔 NEW!  
📍 St John's Church - London  
📅 Sunday, 11 August 2024  
🕒 10:30 AM  
Fee: £100  
```

---

## 📂 Files

- `job_watcher.py` — Main monitoring and emailing script
- `seen_jobs.txt` — Stores previously seen job listings (auto-generated)
- `requirements.txt` — Python dependencies
- `.gitignore` — Files to ignore in version control

---

## 🚫 .gitignore Recommendations

```bash
seen_jobs.txt
*.pyc
__pycache__/
.env
```

---

## 📦 Dependencies

- `selenium`
- `schedule`

Install all dependencies via:

```bash
pip install -r requirements.txt
```

---

## 🤝 License & Contributions

Contributions are welcome! Feel free to fork the repo and submit pull requests.  
Please open an issue if you encounter bugs or want to request features.

**Happy Organist Job Hunting!** 🎹✨
