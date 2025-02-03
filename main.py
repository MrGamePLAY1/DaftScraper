import requests
import os
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import random
import logging
import time
import requests
from dataclasses import dataclass
from typing import List

load_dotenv()

web = os.getenv('WEBHOOK_URL')
if not web:
    raise ValueError("WEBHOOK_URL environment variable is not set.")

# Update logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()  # This ensures output goes to console
    ]
)

logger = logging.getLogger(__name__)

@dataclass
class Property:
    address: str
    price: str
    image_url: str  # Add image URL field
    details: List[str]  # Store all <span> texts as a list
    processed: bool = False  # Add a processed flag

# NEW SET OF PROPERTIES
known_properties = []

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
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to retrieve data: {e}")
        return []

    # Parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")
    

    # Find all property listings directly
    listings = soup.find_all("li", {"data-testid": lambda x: x and "result" in str(x)})

    # Check if no listing is found
    if not listings:
        logger.warning("No listings found on the page.")
        return []

    new_properties = []
    for listing in listings:
        try:
            # Extract Address
            address_div = listing.find("div", {"data-tracking": "srp_address"})
            address = address_div.find("p").get_text(strip=True) if address_div else "N/A"

            # Extract Price
            price_div = listing.find("div", {"data-tracking": "srp_price"})
            price = price_div.find("p").get_text(strip=True) if price_div else "N/A"
            
            # Extract features
            features = listing.find_all("div", {"data-tracking": "srp_meta"})
            details = [feature.get_text(strip=True) for feature in features]
            
            # Extract image URL
            img_div = listing.find_all("div", {"data-testid": "imageContainer"})
            if img_div:
                # Assuming there's one image per div, you can get the first image
                img_tag = img_div[0].find("img")  # Get the first img tag
                actual_img = img_tag["src"] if img_tag else "N/A"  # Extract the src attribute
            else:
                actual_img = "N/A"
            

            # Add to properties if new
            if address != "N/A" and address not in known_properties:
                new_properties.append(Property(address=address, price=price, image_url=actual_img, details=details))
                known_properties.append(address)

                # Print property details
                logger.info("\n=== New Property Found ===")
                logger.info(f"Address: {address}")
                logger.info(f"Price: {price}")
                logger.info(f"Features: {details}")
                logger.info(f"ImageURL: {actual_img}")
                logger.info("===========================")

        except Exception as e:
            logger.error(f"Error processing listing: {e}")
            continue

    return new_properties

def send_webhook_message(web, properties):
    """Send a message to Discord channel using webhook."""
    embeds = []
    
    for property in properties:
        embed = {
            "title": property.address,
            "description": f"**Price:** {property.price}",
            "color": 0x00ff00,  # Green color
            "image": {"url": property.image_url},  # Main image (larger size)
            "fields": [
                {"name": "Address", "value": property.address, "inline": True},
                {"name": "Price", "value": property.price, "inline": True},
                {"name": "URL", "value": f"[View Image]({property.image_url})", "inline": False}
            ]
        }
        embeds.append(embed)
    
    # Split embeds into chunks of 10
    for i in range(0, len(embeds), 10):
        chunk = embeds[i:i + 10]  # Get up to 10 embeds
        payload = {
            "username": "Daft Bot",  # The username displayed in Discord
            "embeds": chunk
        }
    # Send the message via POST request
    response = requests.post(web, json=payload)
    
    try:
        # Send the message via POST request
        response = requests.post(web, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        logger.info("Webhook message sent successfully!")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send message: {e}")
        logger.error(f"Response: {response.status_code} - {response.text}")



def main():
    while True:
        # Scrape the properties
        new_properties = scrape_properties()
        if new_properties:
            # Send a message to Discord
            send_webhook_message(web, new_properties)
        else:
            logger.info("No new properties found.")

        # Wait for 5 seconds to check again
        time.sleep(5)

if __name__ == "__main__":
    main()
    
