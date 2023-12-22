import datetime
import requests
import threading
import urllib.parse
from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook, DiscordEmbed

base_Url = 'https://forum.gamer.com.tw/B.php?bsn=75993'
current_title = None
timer_interval = 600
webhook_links = ['https://discord.com/api/webhooks/1181785238905569311/eIEKMTjK0b54oHGqeFhwR3AeTuYz5NVaB8IHfJ4X1SoaIzee67GiEW40fAVfpgfgAQ9i']

# test
# https://discord.com/api/webhooks/1181525794376392706/H-b-y93qsastOUYkwzh4P0A1I1usSSmQDXhbTpzAXzKLinEkiUcCgHHv2AVzK9EDNw-w

# carry
# https://discord.com/api/webhooks/1181785238905569311/eIEKMTjK0b54oHGqeFhwR3AeTuYz5NVaB8IHfJ4X1SoaIzee67GiEW40fAVfpgfgAQ9i

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
}


def get_article_url_list(forum_url):
    """爬取文章列表"""
    r = requests.get(forum_url, headers=HEADERS)
    if r.status_code != requests.codes.ok:
        print('網頁載入失敗')
        return []
    
    # 爬取每一篇文章網址
    article_url_list = []
    soup = BeautifulSoup(r.text, 'html.parser')
    item_blocks = soup.select('table.b-list tr.b-list-item')
    for item_block in item_blocks:
        title_block = item_block.select_one('.b-list__main__title')
        article_url = f"https://forum.gamer.com.tw/{title_block.get('href')}"
        article_url_list.append(article_url)

    return article_url_list


def get_article_info(article_url):
    """爬取文章資訊(包含回覆)"""
    r = requests.get(article_url, headers=HEADERS)
    if r.status_code != requests.codes.ok:
        print('網頁載入失敗')
        return {}

    soup = BeautifulSoup(r.text, 'html.parser')
    article_title = soup.select_one('h1.c-post__header__title').text

    # 抓取回覆總頁數
    article_total_page = get_article_total_page(soup)

    # 爬取每一頁回覆
    reply_info_list = []
    for page in range(article_total_page):
        crawler_url = f"{article_url}&page={page + 1}"
        reply_list = get_reply_info_list(crawler_url)
        reply_info_list.extend(reply_list)

    article_info = {
        'title': article_title,
        'url': article_url,
        'reply': reply_info_list
    }
    return article_info


def get_reply_info_list(url):
    """爬取回覆列表"""
    r = requests.get(url, headers=HEADERS)
    if r.status_code != requests.codes.ok:
        print('網頁載入失敗')
        return {}

    reply_info_list = []
    soup = BeautifulSoup(r.text, 'html.parser')
    reply_blocks = soup.select('section[id^="post_"]')

    # 對每一則回覆解析資料
    for reply_block in reply_blocks:
        reply_info = {}

        reply_info['floor'] = int(reply_block.select_one('.floor').get('data-floor'))
        reply_info['user_name'] = reply_block.select_one('.username').text
        reply_info['user_id'] = reply_block.select_one('.userid').text

        publish_time = reply_block.select_one('.edittime').get('data-mtime')
        reply_info['content'] = reply_block.select_one('.c-article__content').text

        gp_count = reply_block.select_one('.postgp span').text
        if gp_count == '-':
            gp_count = 0
        elif gp_count == '爆':
            gp_count = 1000
        reply_info['gp_count'] = int(gp_count)

        bp_count = reply_block.select_one('.postbp span').text
        if bp_count == '-':
            bp_count = 0
        elif bp_count == 'X':
            bp_count = 500
        reply_info['bp_count'] = int(bp_count)

        reply_info_list.append(reply_info)

    return reply_info_list


def get_article_total_page(soup):
    """取得文章總頁數"""
    article_total_page = soup.select_one('.BH-pagebtnA > a:last-of-type').text
    return int(article_total_page)


if __name__ == "__main__":
    # File Input
    f = open('mog_titles.txt','r+', encoding="utf-8")
    readTitles = f.readlines()
    writeTitles = readTitles

    url = 'https://forum.gamer.com.tw/B.php?bsn=75993'
    # Crawler
    article_url_list = get_article_url_list(url)
    print(f"共爬取 {len(article_url_list)} 篇文章 \n")

    # count = 8
    for art in article_url_list:
        article_info = get_article_info(art)

        # file record for news
        current_title = article_info['title']
        print("BP00 current title : " , current_title)
        find_news = False
        isUpdated = False
        for line in readTitles:
            print("BP01 line : " , line)
            if current_title in line:
                find_news = True
                print("BP02 current_title : " , current_title)
                break

        if (find_news == False):
            writeTitles.insert(0, current_title + '\n')

            embed = DiscordEmbed()
            embed.set_author(
                name='我想成為影之強者！MOG',
                url='https://www.facebook.com/shadowSSGTW',
                icon_url=
                     'https://scontent.ftpe8-2.fna.fbcdn.net/v/t39.30808-6/218273058_348761943624386_779349091665511943_n.jpg?_nc_cat=103&ccb=1-7&_nc_sid=efb6e6&_nc_ohc=lW4AbFg4Pb8AX-u8Vie&_nc_ht=scontent.ftpe8-2.fna&oh=00_AfBHJPvMEObOQtZqKZGqA8Oqz1n3W_imf9Jsvi3Ko1JMpQ&oe=65756514'
            )

            # if(count != 0):
            #     count -= 1
            #     continue
            for link in webhook_links:
                embed.title = article_info['title']
                embed.url = article_info['url']
                webhook = DiscordWebhook(url=link)
                webhook.add_embed(embed)
                webhook.execute()
            isUpdated = True


        # while len(writeTitles) > 40:
        #     writeTitles.pop()

        if isUpdated:
            f.seek(0)
            f.truncate(0)
            f.writelines(writeTitles)
    f.close()

    print("已儲存檔案 ")
    
