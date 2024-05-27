from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import typer as tp
from datetime import date


BASE_URL = "https://www.twilio.com"
SMS_GUIDELINES_URL = "https://www.twilio.com/en-us/guidelines/sms"
VOICE_GUIDELINES_URL = "https://www.twilio.com/en-us/guidelines/voice"
app = tp.Typer() # create Typer app

def scrape_country_sms_detail(url):
    page = urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    info_tables = soup.find_all("div", class_="pricing-table")
    country = {}

    try:
        # table 1: Locale Summary
        locale_table = info_tables[0].table
        country_locale = extract_two_columns_table(locale_table)
        country.update(country_locale)

        # table 2: Guidelines
        guidelines_table = info_tables[1].table
        country_guidelines = extract_two_columns_table(guidelines_table)
        country.update(country_guidelines)

        # table 3: Sender ID
        senderid_table = info_tables[2].table
        country_senderid = extract_alphanumeric_table(senderid_table)
        country.update(country_senderid)

        # table 4: Long Codes and Short Codes
        pn_table = info_tables[3].table
        country_pn = extract_pn_table(pn_table)
        country.update(country_pn)
    except:
        print(f"Oh no! Something went terribly wrong! Something may have changed in {url}")

    return country

def scrape_country_voice_detail(url):
    page = urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    info_tables = soup.find_all("div", class_="pricing-table")
    country = {}

    try:
        # table 1: Locale Summary
        locale_table = info_tables[0].table
        country_locale = extract_two_columns_table(locale_table)
        country.update(country_locale)

        # table 2: Reachability
        reachability_table = info_tables[1].table
        reachability = extract_inbound_outbound_table(reachability_table, "Reachability" + " ")
        country.update(reachability)

        # table 3: Caller ID
        callerid_table = info_tables[2].table
        country_callerid = extract_inbound_outbound_table(callerid_table, "Caller ID" + " ")
        country.update(country_callerid)

        # table 4: DTMF
        dtmf_table = info_tables[3].table
        country_dtmf = extract_inbound_outbound_table(dtmf_table, "DTMF" + " ")
        country.update(country_dtmf)

        # table 5: Emergency Calling
        emergency_calling_table = info_tables[4].table
        country_emergency_calling = extract_two_columns_table(emergency_calling_table)
        country.update(country_emergency_calling)

    except:
        print(f"Oh no! Something went terribly wrong! Something may have changed in {url}")

    return country

def extract_two_columns_table(table):
    """Take <table> of 2 columns and dynamically extract info."""
    # For debug:
    # print(table.prettify())

    entry = {}
    table_rows = table.tbody.find_all("tr", recursive=False)
    for row in table_rows:
        cells = row.find_all("td", recursive=False)
        key = cells[0].div.div.p.b.get_text().strip()
        value = cells[1].div.div.get_text().strip()
        entry[key] = value
    return entry


def extract_alphanumeric_table(table):
    """Take <table> of alphanumeric and extract info. Assumption is the Pre-registration and Dynamic columns remain static."""
    # For debug:
    # print(table.prettify())

    entry = {}
    table_rows = table.tbody.find_all("tr", recursive=False)
    for row in table_rows:
        cells = row.find_all("td", recursive=False)
        key = cells[0].div.div.p.b.get_text().strip()
        prereg_value = cells[1].div.div.get_text().strip()
        dynamic_value = cells[2].div.div.get_text().strip()
        entry["Pre-registration " + key] = prereg_value
        entry["Dynamic " + key] = dynamic_value
    return entry

def extract_inbound_outbound_table(table, name=""):
    """Take <table> of alphanumeric and extract info. Assumption is the Pre-registration and Dynamic columns remain static."""
    # For debug:
    # print(table.prettify())

    entry = {}
    table_rows = table.tbody.find_all("tr", recursive=False)
    for row in table_rows:
        cells = row.find_all("td", recursive=False)
        key = cells[0].div.div.p.b.get_text().strip()
        inbound_value = cells[1].div.div.get_text().strip()
        outbound_value = cells[2].div.div.get_text().strip()
        entry[name + "Inbound " + key] = inbound_value
        entry[name + "Outbound " + key] = outbound_value
    return entry

def extract_pn_table(table):
    """Take <table> of phone number and extract info. Assumption is the Long Code (Domestic vs International) 
        and Short Code columns remain static."""
    # For debug:
    # print(table.prettify())

    entry = {}
    table_rows = table.tbody.find_all("tr", recursive=False)
    for row in table_rows:
        cells = row.find_all("td", recursive=False)
        key = cells[0].div.div.p.b.get_text().strip()
        domestic_lc_value = cells[1].div.div.get_text().strip()
        international_lc_value = cells[2].div.div.get_text().strip()
        sc_value = cells[3].div.div.get_text().strip()
        entry["Domestic LC " + key] = domestic_lc_value
        entry["Internation LC " + key] = international_lc_value
        entry["SC " + key] = sc_value
    return entry

@app.command()
def sms_guidelines():
    url = SMS_GUIDELINES_URL
    page = urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    country_guidelines_list = []

    try:
        country_list_section = soup.find(id="guidelineCountryList")
        country_cards = country_list_section.find_all("div", "grid-container-column")
        url_list = [ card.a["href"] for card in country_cards if card.a ]
    except:
        print(f"Oh no! Something has changed on {url}!")
    
    
    for suburl in url_list:
        iter_url = BASE_URL + suburl
        country_guidelines_list.append(scrape_country_sms_detail(iter_url))
        print(f"Current URL : {iter_url} \t[DONE]")
    
    print("No. of Country Processed:", len(country_guidelines_list))
    country_guidelines_df = pd.DataFrame(country_guidelines_list)

    today = date.today().strftime("%Y%m%d")
    extension = "xlsx"
    filename = "Twilio_SMS_Country_Guidelines"
    sheetname = "Country Guidelines"
    
    # output to Excel
    country_guidelines_df.to_excel(f'{filename}_{today}.{extension}', sheet_name=sheetname, index=False)

@app.command()
def voice_guidelines():
    url = VOICE_GUIDELINES_URL
    page = urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    country_guidelines_list = []

    try:
        country_list_section = soup.find(id="guidelineCountryList")
        country_cards = country_list_section.find_all("div", "grid-container-column")
        url_list = [ card.a["href"] for card in country_cards if card.a ]
    except:
        print(f"Oh no! Something has changed on {url}!")
    
    for url in url_list:
        iter_url = BASE_URL + url
        country_guidelines_list.append(scrape_country_voice_detail(iter_url))
        print(f"Current URL : {iter_url} \t[DONE]")
    
    print("No. of Country Processed:", len(country_guidelines_list))
    country_guidelines_df = pd.DataFrame(country_guidelines_list)

    today = date.today().strftime("%Y%m%d")
    extension = "xlsx"
    filename = "Twilio_Voice_Country_Guidelines"
    sheetname = "Country Guidelines"
    
    # output to Excel
    country_guidelines_df.to_excel(f'{filename}_{today}.{extension}', sheet_name=sheetname, index=False)

if __name__ == "__main__":
    app()