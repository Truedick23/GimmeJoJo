import requests
from pymongo import MongoClient
from random import choice, uniform
from bs4 import BeautifulSoup
import time
import ssl
import os
import base64
import traceback
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
import urllib
import urllib.request as req
from requests.auth import HTTPProxyAuth
from urllib3.util.ssl_ import create_urllib3_context

CIPHERS = (
    'ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:'
    'DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES:!aNULL:'
    '!eNULL:!MD5'
)

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
hdr = {'Accept-Language':'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4', 'Cache-Control':'max-age=0', 'Connection':'keep-alive', 'Proxy-Connection':'keep-alive', #'Cache-Control':'no-cache', 'Connection':'close',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'Accept-Encoding':'gzip,deflate,sdch','Accept':'*/*'}

class DESAdapter(HTTPAdapter):
    """
    A TransportAdapter that re-enables 3DES support in Requests.
    """
    def create_ssl_context(self):
        #ctx = create_urllib3_context(ciphers=FORCED_CIPHERS)
        ctx = ssl.create_default_context()
        # allow TLS 1.0 and TLS 1.2 and later (disable SSLv3 and SSLv2)
        ctx.options |= ssl.OP_NO_SSLv2
        ctx.options |= ssl.OP_NO_SSLv3
        ctx.options |= ssl.OP_NO_TLSv1
        ctx.options |= ssl.OP_NO_TLSv1_2
        ctx.options |= ssl.OP_NO_TLSv1_1
        #ctx.options |= ssl.OP_NO_TLSv1_3
        ctx.set_ciphers( CIPHERS )
        ctx.set_alpn_protocols(['http/1.1', 'spdy/2'])
        return ctx

    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=CIPHERS)
        kwargs['ssl_context'] = self.create_ssl_context()
        return super(DESAdapter, self).init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=CIPHERS)
        kwargs['ssl_context'] = self.create_ssl_context()
        return super(DESAdapter, self).proxy_manager_for(*args, **kwargs)

def get_jojo_collection(name):
    client = MongoClient()
    return client.jojo[name]

def get_proxy():
    proxyHost = '119.3.37.101'
    proxyPort = '54238'

    proxyUser = "dingzhx@vip.qq.com"
    proxyPass = "josephlive199823"

    proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
      "host" : proxyHost,
      "port" : proxyPort,
      "user" : proxyUser,
      "pass" : proxyPass,
    }

    proxies = {
        "http"  : proxyMeta,
        "https" : proxyMeta
    }

    return proxies

def get_html_text(url):
    # proxy = get_proxy()
    headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
    try:
        r = requests.get(url, headers=headers)
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
            time.sleep(uniform(0.1, 0.2))
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
        try:
            status = download_pic(pic_url, path)
            if status == 200:
                # time.sleep(uniform(0.3, 0.6))
                collection.update(
                    {'pic_url': item['pic_url']},
                    {'$set': {'downloaded': True}}
                )
            else:
                print(status)
        except:
            print(traceback.format_exc())
            print(page)
            print(item['page_url'])
        total_num = collection.count()
        downloaded_num = collection.count({'downloaded': True})
        print(name + ' Progress: {:.2%}'.format(downloaded_num / total_num), end='\n')
    print(name + 'finished downloading!')
    cursor.close()

def download_pic(url, path):
    appKey = "NzMwTmVFV25FM2t3Q3pyMTpyY2FodURsek1DaXpRRVJq"
    ip_port = 'transfer.moguproxy.com:9001'

    proxy = {"http": "http://" + ip_port, "https": "https://" + ip_port}
    headers_with_proxy = {"Proxy-Authorization": 'Basic ' + appKey, 'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
    headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
    '''
    proxy = req.ProxyHandler({'https': address, 'http': address})
    auth = req.HTTPBasicAuthHandler()
    opener = req.build_opener(proxy, auth, req.HTTPHandler)
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    opener.addheaders = [('User-Agent', choice(myHeaders))]
    req.install_opener(opener)
    conn = req.urlopen(url)
    '''

    proxies = get_proxy()
    ses = requests.session()
    ses.trust_env = False
    ses.mount(url , DESAdapter())
    user = '730NeEWnE3kwCzr1'
    password = 'rcahuDlzMCizQERj'
    # response = requests.get(url, timeout=10, verify=False, allow_redirects=False)
    auth = HTTPProxyAuth(user, password)
    response = requests.get(url, headers=headers)
    # esponse = requests.get(url , headers=headers_with_proxy, proxies=proxy, verify=False, allow_redirects=False)
    if response.status_code == 200:
        with open(path, 'wb') as file:
            file.write(response.content)
    return response.status_code

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

def gimme_tomorrow_joe():
    get_manga_pic_pages('https://www.manhuadb.com/manhua/257/239_2927.html', 381, 'j1')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/257/239_2926.html', 395, 'j2')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/257/239_2924.html', 391, 'j3')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/257/239_2920.html', 379, 'j4')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/257/239_2928.html', 383, 'j5')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/257/239_2929.html', 389, 'j6')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/257/239_2930.html', 393, 'j7')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/257/239_2922.html', 387, 'j8')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/257/239_2923.html', 387, 'j9')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/257/239_2925.html', 383, 'j10')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/257/239_2931.html', 377, 'j11')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/257/239_2921.html', 383, 'j12')

def gimme_eva():
    get_manga_pic_pages('https://www.manhuadb.com/manhua/598/613_6686.html', 178, 'eva1')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/598/613_6691.html', 181, 'eva2')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/598/613_6681.html', 173, 'eva3')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/598/613_6678.html', 185, 'eva4')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/598/613_6689.html', 189, 'eva5')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/598/613_6679.html', 185, 'eva6')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/598/613_6690.html', 188, 'eva7')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/598/613_6688.html', 181, 'eva8')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/598/613_6687.html', 181, 'eva9')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/598/613_6685.html', 179, 'eva10')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/598/613_6684.html', 173, 'eva11')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/598/613_6683.html', 181, 'eva12')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/598/613_6680.html', 184, 'eva13')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/598/613_6682.html', 204, 'eva14')

def gimme_astro():
    get_manga_pic_pages('https://www.manhuadb.com/manhua/486/493_5296.html', 217, 'ast01')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/486/493_5283.html', 210, 'ast02')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/486/493_5282.html', 215, 'ast03')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/486/493_5291.html', 234, 'ast04')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/486/493_5298.html', 236, 'ast05')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/486/493_5284.html', 228, 'ast06')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/486/493_5294.html', 241, 'ast07')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/486/493_5290.html', 225, 'ast08')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/486/493_5292.html', 206, 'ast09')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/486/493_5287.html', 214, 'ast10')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/486/493_5286.html', 204, 'ast11')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/486/493_5293.html', 214, 'ast12')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/486/493_5281.html', 186, 'ast13')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/486/493_5289.html', 218, 'ast14')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/486/493_5297.html', 202, 'ast15')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/486/493_5285.html', 215, 'ast16')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/486/493_5288.html', 216, 'ast17')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/486/493_5295.html', 235, 'ast18')

def gimme_uzumaki():
    get_manga_pic_pages('https://www.manhuadb.com/manhua/584/588_6467.html', 209, 'u1')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/584/588_6466.html', 201, 'u2')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/584/588_6465.html', 257, 'u3')

def gimme_gyo():
    get_manga_pic_pages('https://www.manhuadb.com/manhua/591/592_6475.html', 199, 'gyo1')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/591/592_6474.html', 204, 'gyo2')

def gimme_shiguri():
    get_manga_pic_pages('https://www.manhuadb.com/manhua/648/672_7258.html', 201, 'sh1')
    get_manga_pic_pages('https://www.manhuadb.com/manhua/648/672_7250.html', 190, 'sh2')

def jojo_download_ignite():
    orders = [1, 6, 12, 29, 48, 64]
    for s in range(5):
        for b in range(orders[s], orders[s+1]):
            get_em_pics('s' + str(s+1) + 'b' + str(b), 'E:/JoJoManga/')
    for i in range(17):
        get_em_pics('s6b' + str(i+1), 'E:/JoJoManga/')
    for i in range(24):
        get_em_pics('s7b' + str(i+1), 'E:/JoJoManga/')

def astro_download_ignite():
    for i in range(18):
        get_em_pics('ast' + str(i+1).zfill(2), 'E:/Astro/')

if __name__ == '__main__':
    '''
    proxies = get_proxy()
    targetUrl = "http://test.abuyun.com"
    resp = requests.get(targetUrl, proxies=proxies)
    print(resp.status_code)
    '''
    # gimme_tomorrow_joe()
    # gimme_astro()
    #jojo_download_ignite()
    astro_download_ignite()


