# Twilio SMS Guidelines Scraper
Python script to scrape Country SMS Guidelines from Twilio site. As the site may change, there is no guarantee that this script would work with the new update on the site. This is tested working as of **March 2023**.

To execute the script, please follow the steps below:
1. Clone the repository to your local. Navigate to the ```sms_guidelines_scraper``` directory.
```
git clone https://github.com/seaiaw/sms-guidelines-scraper.git
cd sms-guidelines-scraper
```

2. Use ```pip``` to install required libraries from the requirements.txt. If you don't have ```pip``` installed, follow the steps in this [guide](https://docs.python-guide.org/starting/install3/osx/#pip).
```
pip install -r requirements.txt
```

3. Execute the script. It takes a while for the execution to complete.
```
python sms_guidelines_scraper.py
```

4. Check the output Excel in the same directory. The filename is in the format of **Twilio_SMS_Country_Guidelines_*YYYYMMDD*.xlsx**.
