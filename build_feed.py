import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sys

url = 'https://www.realmadryt.pl/aktualnosci'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.content, 'html.parser')
except Exception as e:
    print(f"Błąd podczas pobierania strony: {e}")
    sys.exit(1)

# Nowy selektor głównego kontenera artykułu
news_items = soup.select('.news-tile')

rss_items = []

for item in news_items:
    try:
        title_element = item.select_one('h2.news-tile__title a')
        if not title_element:
            continue
        title = title_element.text.strip()
        
        description_element = item.select_one('p.news-tile__lead')
        description = description_element.text.strip() if description_element else ""
        
        link_path = item.get('data-article-url')
        link = 'https://www.realmadryt.pl' + link_path if link_path else 'https://www.realmadryt.pl'
        
        date_element = item.select_one('time')
        if date_element:
             date_text = date_element.text.strip()
             date_object = datetime.strptime(date_text, "%d.%m.%Y, %H:%M")
             pub_date = date_object.strftime('%a, %d %b %Y %H:%M:%S GMT')
        else:
            pub_date = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')

        rss_item = f"""
        <item>
            <title><![CDATA[{title}]]></title>
            <link>{link}</link>
            <pubDate>{pub_date}</pubDate>
            <description><![CDATA[{description}]]></description>
        </item>
        """
        rss_items.append(rss_item)
    except Exception as e:
        print(f"Pomijam element ze względu na błąd parsera: {e}")
        continue

if not rss_items:
    print("BŁĄD: Nie wyciągnięto żadnych artykułów. Zaktualizuj selektory CSS!")
    sys.exit(1)

rss_feed_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
    <title>RealMadryt.pl custom feed</title>
    <link>{url}</link>
    <description>Custom feed from realmadryt.pl</description>
    <lastBuildDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')}</lastBuildDate>
    {''.join(rss_items)}
</channel>
</rss>
"""

with open('custom_feed.xml', 'w', encoding='utf-8') as file:
    file.write(rss_feed_template)

print(f"Sukces! Wygenerowano plik custom_feed.xml z {len(rss_items)} artykułami.")
