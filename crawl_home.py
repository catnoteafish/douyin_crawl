import configparser
import os
import re
from functools import lru_cache

import requests
from loguru import logger
from requests.adapters import HTTPAdapter
from tqdm import tqdm

from utils import XBogusUtil
from utils import my_util


class DouYinCrawler:
    def __init__(self):
        self.session = self._initialize_session()
        self.video_list = []
        self.picture_list = []

    @staticmethod
    def _initialize_session():
        try:
            s = requests.Session()
            s.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
                'Referer': 'https://www.douyin.com/'
            })
            cookie = DouYinCrawler._read_cookie_from_file()
            if cookie:
                s.cookies.update({'Cookie': cookie})
            else:
                logger.warning("未能成功加载Cookie，继续初始化Session。")
            s.mount('http://', HTTPAdapter(max_retries=3))
            s.mount('https://', HTTPAdapter(max_retries=3))
            return s
        except Exception as e:
            logger.error(f"初始化全局Session时发生错误: {e}")
            raise RuntimeError("无法创建全局Session，请检查配置或网络环境。")

    @staticmethod
    def _read_cookie_from_file():
        try:
            config = configparser.RawConfigParser()
            if not os.path.exists('config.ini'):
                raise FileNotFoundError("配置文件 config.ini 不存在，请检查文件路径。")
            config.read('config.ini')
            con = dict(config.items('douyin'))
            if not con:
                raise ValueError("配置文件中未找到有效的 douyin 配置项。")
            cookie = con.get('cookie')
            if not cookie:
                logger.error('cookie值为空，请尝试手动填入cookie')
                raise ValueError("配置文件中的 cookie 值为空。")
        except configparser.NoSectionError:
            logger.error("配置文件中缺少 [douyin] 节，请检查配置文件。")
            exit("请检查当前目录下的 config.ini 文件配置。")
        except configparser.NoOptionError:
            logger.error("配置文件中缺少 cookie 选项，请检查配置文件。")
            exit("请检查当前目录下的 config.ini 文件配置。")
        except Exception as e:
            logger.error(f"读取 cookie 时发生错误: {e}")
            exit("请检查当前目录下的 config.ini 文件配置。")
        return cookie

    def analyze_user_input(self, user_in: str):
        try:
            match = re.search(r'user/([-\w]+)', user_in)
            if match:
                return match.group(1)
            match = re.search(r'https://v.douyin.com/(\w+)/', user_in)
            if match:
                short_url = match.group(0)
                try:
                    response = self.session.get(url=short_url, allow_redirects=True)
                    response.raise_for_status()
                    redirected_url = response.url
                    uid_match = re.search(r'user/([-\w]+)', redirected_url)
                    if uid_match:
                        return uid_match.group(1)
                    else:
                        logger.error("无法从重定向URL中提取用户ID")
                except requests.RequestException as e:
                    logger.error(f"网络请求失败: {e}")
                    return None
            logger.error("输入格式无效，无法提取用户ID")
            return None
        except Exception as e:
            logger.error(f"分析用户输入时发生未知错误: {e}")
            return None

    def crawl_media(self, user_in: str):
        os.environ['NO_PROXY'] = 'douyin.com'
        sec_uid = self.analyze_user_input(user_in)
        if sec_uid is None:
            exit("粘贴的用户主页地址格式错误")

        cursor = 0
        while True:
            home_url = f'https://www.douyin.com/aweme/v1/web/aweme/post/?aid=6383&sec_user_id={sec_uid}&count=18&max_cursor={cursor}&cookie_enabled=true&platform=PC&downlink=6.9'
            xbs = XBogusUtil.generate_url_with_xbs(home_url, self.session.headers.get('User-Agent'))
            url = home_url + '&X-Bogus=' + xbs
            json_str = self.session.get(url).json()

            cursor = json_str["max_cursor"]
            for i in json_str["aweme_list"]:
                if i["images"] is None:
                    description = i["desc"]
                    url = i["video"]["play_addr"]["url_list"][0]
                    self.video_list.append([description, url])
                else:
                    self.picture_list += list(map(lambda x: x["url_list"][-1], i["images"]))

            if json_str["has_more"] == 0:
                break
            my_util.random_sleep()

        print('视频数量: ' + str(len(self.video_list)))
        print('图片数量: ' + str(len(self.picture_list)))
        print(f'开始下载到本地文件 {sec_uid}...')
        self.download_media(sec_uid)

    def download_media(self, sec_uid):
        if not os.path.exists(sec_uid):
            os.mkdir(sec_uid)
        os.chdir(sec_uid)

        with tqdm(total=len(self.video_list) + len(self.picture_list), desc="下载进度", unit="文件") as pbar:
            for i in self.video_list:
                des = i[0]
                url = i[1]
                with self.session.get(url, stream=True) as response:
                    if response.status_code == 200:
                        file_name = my_util.sanitize_filename(des)
                        with open(f'{file_name}.mp4', "wb") as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                    else:
                        logger.error(f"网络异常 Status code: {response.status_code}")
                pbar.update(1)

            for i in self.picture_list:
                url = i
                with self.session.get(url, stream=True) as response:
                    if response.status_code == 200:
                        file_name = my_util.IDGenerator.generate_unique_id()
                        with open(f'{file_name}.jpg', "wb") as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                    else:
                        logger.error(f"网络异常 Status code: {response.status_code}")
                pbar.update(1)

        logger.info('用户视频图片已全部下载完成')
        os.chdir('..')


if __name__ == '__main__':
    crawler = DouYinCrawler()
    while True:
        user_input = input("请在此填入用户链接（输入exit退出）: \n")
        if user_input.lower() == "exit":
            break
        crawler.crawl_media(user_input)

    logger.info("程序已退出")
