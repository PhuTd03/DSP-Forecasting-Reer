import os
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta
import pandas as pd

###-------------- Craw forex data -----------------###

def get_exchange_rates(date):
    url = f"https://www.x-rates.com/historical/?from=USD&amount=1&date={date}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table containing exchange rates
    table = soup.find('table', {'class': 'tablesorter ratesTable'})
    rates = {}

    if table:
        rows = table.find_all('tr')
        for row in rows[1:]:  # Skip the header row
            cols = row.find_all('td')
            currency = cols[0].text.strip()
            rate = cols[1].text.strip()
            rates[currency] = rate
    
    return rates

def forex_main():
    start_date = datetime(2020, 8, 22)
    end_date = datetime(2024, 6, 15)
    delta = timedelta(days=1)

    # Create folder to save data (csv)
    if not os.path.exists("raw_data"):
        os.makedirs("raw_data")
    
    # Define the path to the CSV file
    csv_file_path = os.path.join("raw_data", "craw_exchange_rates.csv")
    
    all_data = {}
    all_currencies = set()
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        print(f"Fetching data for {date_str}")
        rates = get_exchange_rates(date_str)
        all_data[date_str] = rates
        all_currencies.update(rates.keys())
        current_date += delta

    all_currencies = sorted(all_currencies)
    
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        # Write header
        header = ['Date'] + all_currencies
        writer.writerow(header)
        
        # Write data
        for date_str, rates in all_data.items():
            row = [date_str] + [rates.get(currency, 'N/A') for currency in all_currencies]
            writer.writerow(row)

###-------------- Craw libor of USA and GBP -----------------###

def get_libor(year):
    # URL of the webpage
    url = f"https://www.global-rates.com/en/interest-rates/libor/american-dollar/historical/{year}/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # find all tables on the page
    tables = soup.find_all("table", {"class": "table"})

    if len(tables) < 2:
        print(f"Second table not found for year {year}.")
        return []

    # Select the second table
    table = tables[1]

    # Prepare to collect the data
    libor_data = []

    # Parse the table rows
    for row in table.find_all("tr")[1:]:  # Skip the header row
        cells = row.find_all("td")
        if len(cells) == 6:  # Ensure that the row has 6 columns
            month = cells[0].text.strip()
            first = cells[1].text.strip()
            last = cells[2].text.strip()
            highest = cells[3].text.strip()
            lowest = cells[4].text.strip()
            average = cells[5].text.strip()
            libor_data.append([year, month, first, last, highest, lowest, average])

    return libor_data

def libor_main():
    start_year = 2000
    end_year = 2024

    all_data = []

    for year in range(start_year, end_year + 1):
        print(f"Scraping data for the year {year}...")
        year_data = get_libor(year)
        if year_data:  # Only extend if data is found
            all_data.extend(year_data)

    if all_data:
        # Create a DataFrame
        columns = ["Year", "Month", "First", "Last", "Highest", "Lowest", "Average"]
        df = pd.DataFrame(all_data, columns=columns)

        # Save the DataFrame to a CSV file
        df.to_csv("raw_data/libor_data_USD.csv", index=False)
        print("Data has been successfully scraped and saved to libor_usd_ts.csv")
    else:
        print("No data was scraped.")

if __name__ == "__main__":
    forex_main()
    # libor_main()
