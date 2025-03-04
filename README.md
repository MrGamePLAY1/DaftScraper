# DaftScraper
## _Property Search Made Easy_
DaftScraper is an automated tool that monitors Daft.ie for new property listings that match your criteria and sends notifications directly to Discord.


### Features

- **Real-time Monitoring:** Automatically checks for new properties within your price range
- **Smart Filtering:** Ignores sites and focuses on actual properties
- **Discord Integration:** Sends detailed notifications with images directly to Discord
- **Duplicate Prevention:** Tracks which properties you've already seen
- **Detailed Information:** Includes address, price, property details, and Eircode

### How It Works
- Periodically scrapes Daft.ie for properties matching your criteria
- Filters out previously seen properties
- Formats property information with images and descriptions
- Sends notifications via Discord webhook or bot

### Setup
##### Prerequisites
- Python 3.8+
- Packages: ```requests```, ``beautifulsoup4``, ``discord.py``, ``python-dotenv``


##### Installation

```sh
git clone https://github.com/yourusername/daftscraper.git
cd daftscraper
pip install -r requirements.txt
```

##### Configuration
1. Create a  ```.env``` file with the following:
```
WEBHOOK_URL=your_discord_webhook_url
DISCORD_TOKEN=your_bot_token
MY_ID=your_discord_user_id
CHANNEL_ID=target_channel_id
```
2. Customise the seach parameter in ``main.py``
```sh 
base_url = "https://www.daft.ie/property-for-sale/mapArea?terms=&adState=published&salePrice_to=215000&pageSize=100..."
```

##### Usage
Run ``main.py``

```sh 
python main.py
```


## License

MIT

## Disclaimer
This tool is for personal use, Please respect Daft.ie's TOS and rate limits.

