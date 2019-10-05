import requests
from pymongo import MongoClient
from random import choice, uniform
from bs4 import BeautifulSoup
import time
import os
import traceback

myHeaders = ["Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
             "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
             "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
             "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
             "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
             "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
             "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
             "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
             "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
             "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
             "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
             "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
             "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
             "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
             "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52"]

params = {'User-Agent': choice(myHeaders)}

def get_jojo_collection(name):
    client = MongoClient()
    return client.jojo[name]

def get_html_text(url):
    global attributeErrorNum, httpErrorNum
    try:
        proxy = {'https:': '127.0.0.1:1080', 'http:': '127.0.0.1:1080'}
        r = requests.get(url, proxies=proxy)
        r.headers = params
        r.encoding = 'utf-8'
        status = r.status_code
        if status == 404:
            print('404', url)
            return ''
        return r.text
    # ['HTTPError', 'AttributeError', 'TypeError', 'InvalidIMDB']
    except:
        print(url)
        print(traceback.format_exc())

def get_pic_path(url):
    text = get_html_text(url)
    soup = BeautifulSoup(text, 'html.parser')
    try:
        path = soup.find(name='div', attrs={'class': "text-center pjax-container"}).img['src']
        return path
    except:
        print(traceback.format_exc())
        return None

def get_manga_pic_pages(root_url, total_pages, name):
    collection = get_jojo_collection(name)
    root_url = root_url.split('.html')[0]
    for page_num in range(1, total_pages+1):
        url = root_url + '_p' + str(page_num) + '.html'
        existed_pages = collection.distinct('page_url')
        if url in existed_pages:
            continue
        pic_url = get_pic_path(url)
        if pic_url != None:
            collection.insert_one({
                'page': page_num,
                'page_url': url,
                'pic_url': pic_url,
                'downloaded': False
            })
            time.sleep(uniform(0.1, 0.3))
            print(name + ' Progress: {:.2%}'.format(collection.count() / total_pages), end='\n')
    print(name + ' already in stock!')

def get_em_pics(name, root_dir):
    if not os.path.exists(root_dir + '/' + name):
        os.mkdir(root_dir + '/' + name)
    collection = get_jojo_collection(name)
    cursor = collection.find({'downloaded': False}, no_cursor_timeout=True)
    for item in cursor:
        pic_url = item['pic_url']
        page = item['page']
        path = root_dir + '/' + name + '/' + str(page).zfill(3) + '.jpg'
        download_pic(pic_url, path)
        time.sleep(uniform(0, 0.1))
        collection.update(
            {'pic_url': item['pic_url']},
            {'$set': {'downloaded': True}}
        )
        total_num = collection.count()
        downloaded_num = collection.count({'downloaded': True})
        print(name + ' Progress: {:.2%}'.format(downloaded_num / total_num), end='\n')
    print(name + 'finished downloading!')
    cursor.close()

def download_pic(url, path):
    html = requests.get(url, params=params)
    with open(path, 'wb') as file:
        file.write(html.content)

def season1_bundle():
    get_manga_pic_pages('https://www.manhuadb.com/manhua/116/3_7824.html', 191, 's1b1')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/116/3_7827.html', 189, 's1b2')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/116/3_7825.html', 199, 's1b3')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/116/3_7826.html', 205, 's1b4')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/116/3_7828.html', 203, 's1b5')
    print('Season 1 finished!')

def season2_bundle():
    get_manga_pic_pages('https://www.manhuadb.com/manhua/118/6_7911.html', 203, 's2b6')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/118/6_7913.html', 205, 's2b7')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/118/6_7910.html', 205, 's2b8')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/118/6_7915.html', 189, 's2b9')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/118/6_7908.html', 189, 's2b10')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/118/6_7912.html', 189, 's2b11')
    print('Season 2 finished!')

def season3_bundle():
    get_manga_pic_pages('https://www.manhuadb.com/manhua/119/5_7837.html', 209, 's3b12')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/119/5_7839.html', 195, 's3b13')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/119/5_7836.html', 191, 's3b14')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/119/5_7835.html', 205, 's3b15')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/119/5_7831.html', 208, 's3b16')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/119/5_7833.html', 203, 's3b17')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/119/5_7841.html', 190, 's3b18')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/119/5_7845.html', 202, 's3b19')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/119/5_7830.html', 204, 's3b20')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/119/5_7834.html', 206, 's3b21')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/119/5_7842.html', 190, 's3b22')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/119/5_7829.html', 188, 's3b23')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/119/5_7844.html', 192, 's3b24')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/119/5_7832.html', 188, 's3b25')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/119/5_7843.html', 188, 's3b26')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/119/5_7840.html', 204, 's3b27')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/119/5_7838.html', 190, 's3b28')
    print('Season 3 finished!')

def season4_bundle():
    get_manga_pic_pages('https://www.manhuadb.com/manhua/124/10_7894.html', 194, 's4b29')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/124/10_7900.html', 186, 's4b30')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/124/10_7898.html', 206, 's4b31')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/124/10_7887.html', 188, 's4b32')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/124/10_7892.html', 202, 's4b33')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/124/10_7883.html', 188, 's4b34')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/124/10_7893.html', 204, 's4b35')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/124/10_7885.html', 206, 's4b36')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/124/10_7901.html', 186, 's4b37')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/124/10_7899.html', 187, 's4b38')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/124/10_7895.html', 208, 's4n39')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/124/10_7891.html', 206, 's4b40')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/124/10_7896.html', 206, 's4b41')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/124/10_7889.html', 189, 's4b42')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/124/10_7897.html', 188, 's4b43')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/124/10_7890.html', 206, 's4b44')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/124/10_7884.html', 206, 's4b45')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/124/10_7888.html', 188, 's4b46')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/124/10_7886.html', 192, 's4b47')
    print('Season 4 finished!')

def season5_bundle():
    get_manga_pic_pages('https://www.manhuadb.com/manhua/128/7_7936.html', 190, 's5b48')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/128/7_7934.html', 194, 's5b49')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/128/7_7938.html', 188, 's5b50')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/128/7_7926.html', 190, 's5b51')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/128/7_7924.html', 188, 's5b52')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/128/7_7932.html', 188, 's5b53')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/128/7_7937.html', 192, 's5b54')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/128/7_7925.html', 188, 's5b55')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/128/7_7933.html', 194, 's5b56')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/128/7_7935.html', 188, 's5b57')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/128/7_7930.html', 190, 's5b58')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/128/7_7931.html', 190, 's5b59')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/128/7_7922.html', 188, 's5b60')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/128/7_7927.html', 188, 's5b61')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/128/7_7928.html', 230, 's5b62')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/128/7_7929.html', 228, 's5b63')
    print('Season 5 finished!')

def season6_bundle():
    get_manga_pic_pages('https://www.manhuadb.com/manhua/139/9_7969.html', 202, 's6b1')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/139/1328_13255.html', 196, 's6b2')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/139/1328_13264.html', 210, 's6b3')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/139/1328_13261.html', 192, 's6b4')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/139/1328_13263.html', 194, 's6b5')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/139/1328_13253.html', 194, 's6b6')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/139/1328_13252.html', 192, 's6b7')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/139/1328_13258.html', 196, 's6b8')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/139/1328_13256.html', 188, 's6b9')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/139/1328_13257.html', 190, 's6b10')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/139/1328_13265.html', 190, 's6b11')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/139/1328_13262.html', 194, 's6b12')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/139/1328_13250.html', 192, 's6b13')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/139/1328_13266.html', 188, 's6b14')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/139/1328_13259.html', 188, 's6b15')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/139/1328_13251.html', 232, 's6b16')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/139/1328_13254.html', 264, 's6b17')
    print('Season 6 finished!')

def season7_bundle():
    get_manga_pic_pages('https://www.manhuadb.com/manhua/147/4_311.html', 193, 's7b1')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/147/4_309.html', 211, 's7b2')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/147/4_302.html', 209, 's7b3')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/147/4_292.html', 225, 's7b4')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/147/4_313.html', 225, 's7b5')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/147/4_307.html', 193, 's7b6')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/147/4_297.html', 193, 's7b7')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/147/4_293.html', 199, 's7b8')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/147/4_314.html', 201, 's7b9')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/147/4_296.html', 193, 's7b10')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/147/4_308.html', 199, 's7b11')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/147/4_298.html', 193, 's7b12')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/147/4_312.html', 197, 's7b13')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/147/4_295.html', 203, 's7b14')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/147/4_315.html', 225, 's7b15')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/147/4_304.html', 193, 's7b16')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/147/4_305.html', 225, 's7b17')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/147/4_301.html', 195, 's7b18')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/147/4_303.html', 195, 's7b19')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/147/4_299.html', 195, 's7b20')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/147/4_310.html', 195, 's7b21')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/147/4_306.html', 195, 's7b22')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/147/4_294.html', 163, 's7b23')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/147/4_300.html', 179, 's7b24')
    print('Season 7 finished!')

def download_ignite():
    orders = [1, 6, 12, 29, 48, 64]
    for s in range(5):
        for b in range(orders[s], orders[s+1]):
            get_em_pics('s' + str(s+1) + 'b' + str(b), 'E:/JoJoManga/')

if __name__ == '__main__':
    # season7_bundle()

    download_ignite()


