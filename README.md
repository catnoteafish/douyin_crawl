# douyin_crawl

### 简介
一个简洁的抖音作品批量下载命令行工具

### 使用说明
nodejs >= 16
python >= 3.8.6
git

```bash
git clone https://github.com/catnoteafish/douyin_crawl.git --depth 1
sudo apt install pipx # or pip3 install pipx
pipx install pdm
pdm install
pdm run python3 crawl_home.py
```

```text
用户主页链接粘贴示例(支持模糊),以下两种链接均支持

1.分享格式
长按复制此条消息，打开抖音搜索，查看TA的更多作品。 https://v.douyin.com/iJLb8V4y/

2.电脑端的浏览器url
https://www.douyin.com/user/MS4wLjABAAAAK8yyhMzdNAtyWqupVvVBXB_4bmr6DMAZ0zpGn91qlJU?vid=7124859220079561995
https://www.douyin.com/user/MS4wLjABAAAAK8yyhMzdNAtyWqupVvVBXB_4bmr6DMAZ0zpGn91qlJU
```

## 配置和运行截图
* 网页F12随便复制一个登陆后的http数据包，很长的一般就是
![img_1.png](运行截图/img_1.png)
* 粘贴到config.ini文件里面
![img_2.png](运行截图/img_2.png)
* 运行截图
![img.png](运行截图/img.png)

许可 
根据GPL-v3授予许可