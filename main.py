import os
from flask import Flask, render_template, request, send_file
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import io
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# Get the current directory path
current_dir = os.path.dirname(os.path.abspath(__file__))
template_path = os.path.join(current_dir, 'index.html')

# Function to scrape the total number of albums from a given URL
def get_album_count(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        soup = BeautifulSoup(response.content, 'html.parser')
        total_div = soup.find('div', class_='categories__box-right-total')
        if total_div:
            numbers = re.findall(r'\d+', total_div.text)
            return numbers[0] if numbers else None
    except Exception as e:
        print(f'Failed to retrieve or parse the webpage {url}. Error: {e}')
        return None

# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Get the URLs from the submitted form
        urls = request.form['urls'].split('\n')
        urls = [url.strip() for url in urls]

        # Process the URLs and generate the Excel file
        with ThreadPoolExecutor() as executor:
            results = executor.map(get_album_count, urls)
            data = list(zip(urls, results))

        df = pd.DataFrame(data, columns=['URL', 'Number'])
        excel_file = io.BytesIO()
        df.to_excel(excel_file, index=False)
        excel_file.seek(0)

        # Send the Excel file for download
        return send_file(
            excel_file,
            as_attachment=True,
            download_name='album_counts.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    return render_template(template_path)

if __name__ == '__main__':
    # Use the PORT environment variable if available, otherwise default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
