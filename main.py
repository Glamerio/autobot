import requests
from bs4 import BeautifulSoup
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

# Last check time (initially set to None)
last_check_time = datetime.now()
new_item_found = False  # Flag to indicate if a new item is found

def parse_time(updated_time_str):
    try:
        # Convert time format information to datetime object
        return datetime.strptime(updated_time_str, '%H:%M:%S').time()
    except ValueError:
        return None

def check_updates():
    global last_check_time, new_item_found
    
    url = "https://bugzilla.mozilla.org/buglist.cgi?quicksearch=webgl&list_id=17021492"

    # Fetch data from the web page
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Process the page source using the BeautifulSoup library
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find all <tr> tags
        tr_tags = soup.find_all('tr', class_='bz_bugitem')
        
        # Iterate over each <tr> tag
        for tr_tag in tr_tags:
            # Check the updated time
            updated_time_elem = tr_tag.find('td', class_='bz_changeddate_column')
            if updated_time_elem:
                updated_time_str = updated_time_elem.text.strip()
                updated_time = parse_time(updated_time_str)
                
                if updated_time is not None and updated_time > last_check_time.time():
                    # Extract necessary data from each tag
                    bug_id = tr_tag.find('td', class_='bz_id_column').text.strip()
                    summary_elem = tr_tag.find('td', class_='bz_short_desc_column')
                    summary = summary_elem.text.strip()
                    summary_href = summary_elem.a['href']
                    status = tr_tag.find('td', class_='bz_bug_status_column').text.strip()
                    
                    # Print the extracted data
                    print('ID:', bug_id)
                    print('Summary:', summary)
                    print('SummaryHref:', 'https://bugzilla.mozilla.org{}'.format(summary_href))
                    print('Status:', status)
                    print('Updated:', updated_time_str)
                    print('---')
                    
                    # Mark that a new item is found
                    new_item_found = True
    else:
        print("An error occurred while loading the page. Status code:", response.status_code)
    
    # If no new item is found, do nothing
    if not new_item_found:
        print("No new items found.")
    
    # Save the current time
    last_check_time = datetime.now()
    # Reset the flag
    new_item_found = False

if __name__ == "__main__":
    # Create a scheduler
    scheduler = BlockingScheduler()

    # Schedule the check_updates function to run at regular intervals
    scheduler.add_job(check_updates, 'interval', seconds=5)

    # Start the scheduler
    scheduler.start()