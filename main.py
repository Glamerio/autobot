import requests
from bs4 import BeautifulSoup
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

# Storage for previously seen bug data (replace with your chosen method - timestamp or ID list)
seen_bugs = set()  # Example using a set for bug IDs

def parse_time(updated_time_str):
    try:
        # Convert time format information to datetime object
        return datetime.strptime(updated_time_str, '%H:%M:%S').time()
    except ValueError:
        return None

def send_signal_message(message_content):
    # Function to send Signal message (replace with actual sending logic)
    print("Sending Signal message:", message_content)

def check_updates():
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
                    
                    # Send Signal message
                    send_signal_message(message_content)
                    
                    # ---------
                    # FOR TESTING
                    # Set flag to True indicating new bugs are found
                    new_bugs_found = True
                    # ---------
        # -------
        # FOR TESTING
        # If no new bugs found, print debug message
        if not new_bugs_found:
            print("No new bugs found.")
        # -------
    else:
        print("An error occurred while loading the page. Status code:", response.status_code)

if __name__ == "__main__":
    # Create a scheduler
    scheduler = BlockingScheduler()

    # Schedule the check_updates function to run at regular intervals
    scheduler.add_job(check_updates, 'interval', seconds=300)  # 5 minutes interval

    # Start the scheduler
    scheduler.start()
