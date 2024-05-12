from bs4 import BeautifulSoup
import requests
from datetime import datetime
import asyncio
from telegram import Bot

# Bot token and target chat ID
bot_token = 'BOTs Token'  # Insert your bot's token here
chat_id = 'chat ID'   # Insert your target chat ID here

# Create Telegram bot
bot = Bot(token=bot_token)

# Storage for previously seen bug data (replace with your chosen method - timestamp or ID list)
seen_bugs = set()  # Example using a set for bug IDs

def parse_time(updated_time_str):
    try:
        # Convert time format information to datetime object
        return datetime.strptime(updated_time_str, '%H:%M:%S').time()
    except ValueError:
        return None

async def send_telegram_message(message):
    try:
        # Send the message
        await bot.send_message(chat_id=chat_id, text=message)
        print("Telegram message sent successfully.")
    except Exception as e:
        print("Error sending Telegram message:", e)

async def check_updates():
    global seen_bugs
    
    url = "https://bugzilla.mozilla.org/buglist.cgi?quicksearch=webgl&list_id=17021492"

    # Fetch data from the web page
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Process the page source using the BeautifulSoup library
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find all <tr> tags
        tr_tags = soup.find_all('tr', class_='bz_bugitem')
        
        # Flag to indicate if new bugs are found
        new_bugs_found = False
        
        # Iterate over each <tr> tag
        for tr_tag in tr_tags:
            # Check the updated time
            updated_time_elem = tr_tag.find('td', class_='bz_changeddate_column')
            if updated_time_elem:
                updated_time_str = updated_time_elem.text.strip()
                updated_time = parse_time(updated_time_str)
                
                # Extract necessary data from each tag
                bug_id = tr_tag.find('td', class_='bz_id_column').text.strip()
                
                # Check if the bug is new and has a time format update
                if updated_time is not None and ':' in updated_time_str and bug_id not in seen_bugs:
                    # New bug detected!
                    seen_bugs.add(bug_id)  # Add ID to seen list
                    summary_elem = tr_tag.find('td', class_='bz_short_desc_column')
                    summary = summary_elem.text.strip()
                    summary_href = summary_elem.a['href']
                    status = tr_tag.find('td', class_='bz_bug_status_column').text.strip()
                    
                    # Format message content (including bug details)
                    message_content = f"New Bug Detected:\nID: {bug_id}\nSummary: {summary}\nStatus: {status}\nUpdated: {updated_time_str}\nLink: https://bugzilla.mozilla.org{summary_href}"
                    
                    # Send Telegram message
                    await send_telegram_message(message_content)
                    
                    # Set flag to True indicating new bugs are found
                    new_bugs_found = True
        
        # If no new bugs found, print debug message
        if not new_bugs_found:
            print("No new bugs found.")
            
    else:
        print("An error occurred while loading the page. Status code:", response.status_code)

async def main():
    while True:
        await check_updates()
        await asyncio.sleep(600)  # 10 minutes waiting time

if __name__ == "__main__":
    asyncio.run(main())
