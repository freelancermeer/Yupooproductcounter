# netlify/functions/scrape_albums.py
import requests
from bs4 import BeautifulSoup
import re
import json

def handler(event, context):
    # Function to scrape the total number of albums from a given URL
    def get_album_count(url):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Check for HTTPError
            soup = BeautifulSoup(response.content, 'html.parser')
            total_div = soup.find('div', class_='categories__box-right-total')
            if total_div:
                numbers = re.findall(r'\d+', total_div.text)
                return numbers[0] if numbers else None
        except Exception as e:
            return f'Failed to retrieve or parse the webpage {url}. Error: {e}'

    # Extract data from the event body
    try:
        urls = json.loads(event['body'])  # Assuming URLs are sent in the request body
    except:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Bad request'})
        }

    data = []
    for url in urls:
        number = get_album_count(url)
        data.append({'URL': url, 'Number': number})

    # Return the scraped data
    return {
        'statusCode': 200,
        'body': json.dumps(data)
    }
