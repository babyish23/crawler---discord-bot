import datetime
import requests
import threading
import urllib.parse
from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook, DiscordEmbed

base_Url = 'https://www.shadow-garden-mog.jp/tw/tw-information/?from=ingame'
current_title = None
timer_interval = 600
webhook_links = ['your webhook link']

def get_mog_news():
    # File Input
    f = open('mog_news.txt','r+', encoding="utf-8")
    readTitles = f.readlines()
    writeTitles = readTitles

    # Crawler
    r = requests.get(base_Url)
    soup = BeautifulSoup(r.text, 'html.parser')
    divObjects = soup.find_all("article", class_="information-the-post")  # Find all articles with the specified class

    for article in divObjects:
        relative_url = article.find('a')['href'] # Extract URL from the 'href' attribute of the 'a' tag
        linkURL = urllib.parse.urljoin(base_Url, relative_url) 
        content = article.find('div', class_='the-post-content').text.strip()  # Extract content from the 'div' tag with the specified class

        find_news = False
        isUpdated = False


        current_content = content
        for line in readTitles:
            if current_content in line:
                find_news = True
                break

        if (find_news == False):
            writeTitles.insert(0, current_content + '\n')
            embed = DiscordEmbed()
            embed.set_author(
                name='我想成為影之強者！MOG',
                url='https://www.facebook.com/shadowSSGTW',
                icon_url=
                     'https://scontent.ftpe8-2.fna.fbcdn.net/v/t39.30808-6/218273058_348761943624386_779349091665511943_n.jpg?_nc_cat=103&ccb=1-7&_nc_sid=efb6e6&_nc_ohc=lW4AbFg4Pb8AX-u8Vie&_nc_ht=scontent.ftpe8-2.fna&oh=00_AfBHJPvMEObOQtZqKZGqA8Oqz1n3W_imf9Jsvi3Ko1JMpQ&oe=65756514'
            )
            for link in webhook_links:
                embed.title = current_content
                embed.url = linkURL + "?from=ingame"
                webhook = DiscordWebhook(url=link)
                webhook.add_embed(embed)
                webhook.execute()
            isUpdated = True
        
        # while len(writeTitles) > 10:
        #     writeTitles.pop()
    
        if isUpdated:
            f.seek(0)
            f.truncate(0)
            f.writelines(writeTitles)
    f.close()

if __name__ == '__main__':
    get_mog_news()
    print("finish!")
