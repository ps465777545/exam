# author:潘松
# datetime: 2020年08月06日17:02:39
import sys
import getopt
import os
import requests
import time
import signal
import datetime
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

base_dir = os.path.split(os.path.realpath(__file__))[0]
base_header = {
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Mobile Safari/537.36'
}
thread_pool = ThreadPoolExecutor(max_workers=20)


def signal_handler(signal, frame):
    """
    监听信号机制
    :param signal:
    :param frame:
    :return:
    """
    print('进程结束')
    sys.exit(2)


signal.signal(signal.SIGINT, signal_handler)


def get_static_request(url: str):
    if url.startswith('//'):
        url = 'http:' + url
    res = requests.get(url=url, headers=base_header).content
    return res, url


def download_file(file_list: list, save_path: str):
    """
    下载静态文件文件
    :param file_list: 文件列表
    :param save_path: 保存目录
    :return:
    """
    file_list = set(file_list)
    all_task = [thread_pool.submit(get_static_request, (i)) for i in file_list]
    for future in as_completed(all_task):
        content, url = future.result()
        file_name = url.split('/')[-1]
        with open(os.path.join(save_path, file_name), 'wb+') as f:
            f.write(content)


def get_all_js_url(html: str):
    # 提取js路径
    js_list_1 = re.findall('<link rel="preload" href="(.*?)" as="script">', html)
    js_list_2 = re.findall('<script src="(.*?)"', html)
    all_js_list = js_list_1 + js_list_2
    return all_js_list


def get_all_css_url(html: str):
    # 提取css路径
    css_list_1 = re.findall('<link rel="preload" href="(.*?)" as="style">', html)
    css_list_2 = re.findall('<link rel="stylesheet" href="(.*?)">', html)
    all_css_list = css_list_1 + css_list_2
    return all_css_list


def get_all_image_url(html: str):
    # 提取图片路径
    image_list_1 = re.findall("""background: url\('(.*?)'\) no-repeat center center;""", html)
    image_list_2 = re.findall(""""focus":"(.*?)",""", html)
    image_list_3 = re.findall('''<img src="(.*?)"''', html)
    image_list_4 = re.findall('''"icon":"(.*?)"''', html)
    all_image_list = image_list_1 + image_list_2 + image_list_3 + image_list_4
    return all_image_list


def save_page(time_sleep: int, url: str, full_path: str):
    """
    保存页面
    :param time_sleep: 时间间隔
    :param url: 抓取的url
    :param full_path: 存储路径
    :return:
    """
    print('任务开始，输入Ctrl+C结束进程。')
    while True:
        # 生成该时间点对应的目录及文件
        pack = os.path.join(full_path, datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
        image_path = os.path.join(pack, 'image')
        css_path = os.path.join(pack, 'css')
        js_path = os.path.join(pack, 'js')
        os.mkdir(pack)
        os.mkdir(css_path)
        os.mkdir(js_path)
        os.mkdir(image_path)

        # 获取网页源码
        html = requests.get(url=url, headers=base_header).text
        # 提取js
        js_list = get_all_js_url(html=html)
        for i in js_list:
            html = html.replace(i, os.path.join('./js/', i.split('/')[-1]))
        download_file(js_list, js_path)
        # 提取css路径
        css_list = get_all_css_url(html=html)
        for x in css_list:
            html = html.replace(x, os.path.join('./css/', x.split('/')[-1]))
        download_file(css_list, css_path)
        # 提取 image 路径
        image_list = get_all_image_url(html=html)
        for j in image_list:
            html = html.replace(j, os.path.join('./image/', j.split('/')[-1]))
        download_file(image_list, image_path)

        with open(os.path.join(pack, 'index.html'), 'w+') as f:

            f.write(html)
        time.sleep(time_sleep)

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "d:u:o:")
    except getopt.GetoptError:
        print('main.py -d <time> -u <url> -o <save_path>')
        sys.exit(2)

    full_path = 'tmp/backup'
    time_sleep = 60
    url = 'http://m.sohu.com'
    for opt, arg in opts:
        if opt == '-u':
            url = arg
            if not url.startswith('http://') or url.startswith('https://'):
                print('url 不符合规则！请以http:// 或 https:// 开头')
                sys.exit(2)
        elif opt in ("-d"):
            time_sleep = arg
            try:
                time_sleep = int(time_sleep)
            except:
                print('-d 必须是int类型')
                sys.exit(2)
            if time_sleep < 60:
                print('-d 时间间隔默认不能小于60s')
                time_sleep = 60
        elif opt in ("-o"):
            save_path = arg
            if not save_path:
                save_path = '/tmp/backup'
            full_path = os.path.join(base_dir, save_path)
            if not os.path.exists(full_path):
                os.mkdir(full_path)
    save_page(time_sleep=time_sleep, url=url, full_path=full_path)
    print(full_path, time_sleep, url)


if __name__ == "__main__":
    main(sys.argv[1:])