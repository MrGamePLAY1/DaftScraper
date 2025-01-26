import requests
import pandas as pd
from bs4 import BeautifulSoup
import random
import logging
import time
from dataclasses import dataclass
from typing import List

# Add logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Property:
    address: str
    price: str
    image_url: str  # Add image URL field
    details: List[str]  # Store all <span> texts as a list
    


def scrape_properties():
    # Base URL for pagination
    base_url = "https://www.daft.ie/property-for-sale/ireland?terms=&adState=published&location=dublin&location=meath&salePrice_to=200000&salePrice_from=150000&pageSize=100&from=0"

    # User agents to rotate
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    ]

    # Set headers to mimic a real browser
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Connection": "keep-alive",
        "Referer": "https://www.daft.ie/",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "DNT": "1",
    }

    # Send a GET request
    response = requests.get(base_url, headers=headers)

    # Manually set the encoding (if needed)
    response.encoding = "utf-8"  # or "ISO-8859-1"

    # Parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")

    # Verify response
    logger.info(f"Response status: {response.status_code}")

    # Find all titles, prices, and property-style containers
    titles = soup.find_all("div", {"class": "sc-e4fdcbde-3 fkMRKT"})  # Update this selector
    prices = soup.find_all("div", {"class": "sc-e4fdcbde-3 ifZXft"})  # Update this selector
    property_styles = soup.find_all("div", {"class": "sc-5d364562-1 kzXTWf"})  # Update this selector
    image_containers = soup.find_all("div", {"class": "sc-7cfc0726-0 kTpJhs"})  # Update this selector

    # Initialize a list to store grouped properties
    properties = []

    # Loop through the elements and group them
    for title, price, style, image_container in zip(titles, prices, property_styles, image_containers):
        try:
            # Extract the text for each field
            address = title.find("p").get_text(strip=True)
        except AttributeError:
            address = "N/A"

        try:
            price = price.find("p").get_text(strip=True)
        except AttributeError:
            price = "N/A"
            
        try:
            # Extract the image URL
            img_tag = image_container.find("img")
            image_url = img_tag.get("src") if img_tag else "N/A"
        except AttributeError:
            image_url = "N/A"

        try:
            # Find all <span> tags within the property-style container
            spans = style.find_all("span")
            details = [span.get_text(strip=True) for span in spans]
        except AttributeError:
            details = []

        # Create a Property object
        property_data = Property(
            address=address,
            price=price,
            details=details,
            image_url=image_url
        )

        # Add the property to the list
        properties.append(property_data)

        # Log the property
        logger.info(f"Adding property: {property_data}")

    # Print all properties
    for property in properties:
        print(property)

    # Save the data to a CSV file
    df = pd.DataFrame([prop.__dict__ for prop in properties])
    df.to_csv("all_properties.csv", index=False)
    logger.info("Data saved to 'all_properties.csv'.")

    return properties


def main():
    while True:
        try:
            # Run the scraper
            properties = scrape_properties()
            print(f"Scraped {len(properties)} properties.")
            
            # Wait for a specified interval (e.g., 30 minutes)
            time.sleep(1800)  # 1800 seconds = 30 minutes
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(60)  # Wait 1 minute before retrying


if __name__ == "__main__":
    main()