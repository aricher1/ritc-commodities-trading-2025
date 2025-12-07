# Commodities News Trading Script designed for the Refiner role in the Rotman Interactive Trading Competition (RITC) 2025.
# This script is designed to parse news articles related to heating oil and make trading decisions based on the information provided in the articles.
# Aidan Richer, 2025

import requests
import time
import re

# API requests
headers = {'X-API-key': 'J38GM6X0'}

def is_running(verbose=False):
    "This function checks if the case is running, and if so, returns True,"
    resp = requests.get("http://localhost:9999/v1/case", headers=headers)
    resp = resp.json()
    if resp["status"] == "ACTIVE":
        if verbose:
            print(resp["tick"])
        time.sleep(0.5)
        return True
    return False
def get_news():
    "This function gets the latest news article from the Rotman Interactive Trader"
    news = requests.get("http://localhost:9999/v1/news", headers=headers, params={"limit": 1})
    news = news.json()[0]
    return news
def parse_news(article):
    "This function parses the news article and makes a trading decision based off the equation provided by RITC"
    if "heating oil" not in article["headline"].lower():
        return
   
    body = article["body"]    

    # Extract key values used in equation
    temperature_change_pattern = r"expected average weekly temperature was ([-+]?\d*\.?\d+) degrees while the realized weekly temperature is ([-+]?\d*\.?\d+) degrees"
    standard_deviation_pattern = r"standard deviation of the weekly temperature is ([-+]?\d*\.?\d+) degrees"
    current_price_pattern = r"current price of HO is \$([-+]?\d*\.?\d+)"
    percentage_pattern = r"heating oil market is expected to respond with lower prices of approximately ([-+]?\d*\.?\d+)%"
    
    # Use regex to extract the values
    temp_match = re.search(temperature_change_pattern, body)
    std_dev_match = re.search(standard_deviation_pattern, body)
    current_price_match = re.search(current_price_pattern, body)
    percentage_match = re.search(percentage_pattern, body)
    
    # Trading logic
    if temp_match and std_dev_match and current_price_match:
        expected_temp_change = float(temp_match.group(1)) - float(temp_match.group(2))
        standard_deviation = float(std_dev_match.group(1))
        current_price = float(current_price_match.group(1))

        final_price = current_price + (expected_temp_change / standard_deviation)
        if percentage_match:
            percentage_change = float(percentage_match.group(1)) / 100
            final_price *= (1 + percentage_change)

        decision = "long" if current_price < final_price else "short"

        print(f"{decision.capitalize()} @ Expected Close-Out Price: ${final_price:.2f}")

previous_article = None

# Main loop 
running = is_running()
while running:
    news = get_news()

    if news == previous_article:
        time.sleep(0.5)
        continue
    
    parse_news(news)
    
    previous_article = news
    running = is_running(verbose=False)
