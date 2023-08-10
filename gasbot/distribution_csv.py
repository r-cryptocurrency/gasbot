import os
import csv
import requests
from datetime import datetime, timedelta
from gasbot.constants import START_SNAPSHOT_DATE, START_SNAPSHOT_ROUND


def calculate_snapshot_date():
    now = datetime.utcnow()
    snapshot_date = datetime.fromisoformat(START_SNAPSHOT_DATE)
    while now >= snapshot_date:  
        snapshot_date += timedelta(days=28)
    return snapshot_date


def calculate_round_number():
    """
    Calculate the round number based on the start_date and 
    how many 28-day intervals have passed since then.
    """
    now = datetime.utcnow()
    start_date = datetime.fromisoformat(START_SNAPSHOT_DATE)
    elapsed_time = now - start_date
    elapsed_rounds = elapsed_time // timedelta(days=28) 
    return START_SNAPSHOT_ROUND + elapsed_rounds


def download_and_save_csv():
    print("***********Downloading distribution CSV data from reddit************")
    round_number = calculate_round_number()
    csv_url_1 = f"https://reddit-meta-production.s3.amazonaws.com/distribution/publish/CryptoCurrency/round_{round_number}_finalized.csv"
    csv_url_2 = f"https://reddit-meta-production.s3.amazonaws.com/distribution/publish/CryptoCurrency/round_{round_number - 1}_finalized.csv"
    response_1 = requests.get(csv_url_1)
    response_2 = requests.get(csv_url_2)

    if response_1.status_code == 200:
        filepath = os.path.join("data", "distribution_current.csv")
        with open(filepath, 'wb') as file:
            file.write(response_1.content)
        print(f"CSV saved to {filepath}")
    else:
        print(f"Failed to download CSV for round {round_number}")

    if response_2.status_code == 200:
        filepath = os.path.join("data", "distribution_previous.csv")
        with open(filepath, 'wb') as file:
            file.write(response_2.content)
        print(f"CSV saved to {filepath}")
    else:
        print(f"Failed to download CSV for round {round_number - 1}")

    print(f"*******Next update scheduled for {calculate_snapshot_date()} UTC*******")


def check_address_in_csvs(vault_address):
    """
    Checks if the address is present in the distribution CSVs with at least 5 karma.
    
    Args:
        address (str): The address to verify.
        
    Returns:
        tuple: (karma_in_current_csv, karma_in_previous_csv)
    """
    def check_address(file_path):
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["blockchain_address"].lower() == vault_address.lower():
                    return int(row["karma"])
        return 0
    
    karma_in_current_csv = check_address("data/distribution_current.csv")
    karma_in_previous_csv = check_address("data/distribution_previous.csv")
    
    return karma_in_current_csv, karma_in_previous_csv
