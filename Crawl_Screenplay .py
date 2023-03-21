#!/usr/bin/env python
import time

import requests
from lxml import html
import json
from urllib.parse import quote
import os
import re
from tqdm import tqdm

'''
分析:
    1.歌曲下载分析:
        (1)前部分固定:https://linkyoulimited-my.sharepoint.com/personal/piano_bi_bi/_layouts/15/download.aspx
        (2)参数:
            SourceUrl: 
                /personal/piano_bi_bi/Documents/Bi.Bi/Audio/FLAC/Unreleased/Silu Wang - Passacaglia(只有这部分是动态的，是歌曲的名字) - BiBiPiano.flac
                /personal/piano_bi_bi/Documents/Bi.Bi/Audio/FLAC/Unreleased
        (3)是GET请求
        (4)需要登录后，回去cookie
        Passacaglia ：aff32f05-a787-4c71-94d7-95ab375cb64c bb1d5eb5-6f8e-4662-b5c0-598905fa5003  request-id   sprequestguid
        雪之梦（Snowdreams）：2cf5bf88-e6bb-4781-b636-334349e64325
        
        (5)歌曲名称所在的地方<div role="none" class="ms-OverflowSet ms-CommandBar-middleCommand middleSet-48">
                            <div class="ms-OverflowSet-item item-46">
                                <button type="button" role="text" name="Silu Wang - 雪之梦 - BiB....flac" title="Silu Wang - 雪之梦 - BiBiPiano.flac" 
    2.登录:
        (1)POST请求
        (2)https://bi.bi/membership-login/
        (3)参数: swpm_user_name: 账号
                swpm_password: 密码
                swpm-login: 登陆
                获取cookie教程:(https://blog.csdn.net/qq_15028721/article/details/119853805)
    3.下载的地址:
        (1)下载的页面:href="https://bi.bi/download/"
        (2)每首歌曲播放和下载的地址:
            href="https://linkyoulimited-my.sharepoint.com/:u:/g/personal/piano_bi_bi/ESlbq-TVrY9Fo7xMs8VfEIoBuonIYnYAMx-26l5Ep6ZsWg?e=pg96y8"
            href="https://linkyoulimited-my.sharepoint.com/:u:/g/personal/piano_bi_bi/EaR0QZd57HFBpLi8jW9MT5MBtESPiU5XG1XMHY0NB6ewkA?e=dLY2QV"
'''

"""
    登录函数
        参数:
        BiBiPiano_Login_enail=登录账号,
        BiBiPiano_Login_pass=登录密码,
        BiBiPiano_Login_address=登录地址,
        session=session登录,
        headers_login=headers伪装
"""
def login_BiBIPiano(BiBiPiano_Login_enail,BiBiPiano_Login_pass,BiBiPiano_Login_address,session,headers_login):
    # 入参
    data_login={
        'swpm_user_name':BiBiPiano_Login_enail,
        'swpm_password':BiBiPiano_Login_pass,
        'swpm-login':'登陆'
    }
    # 登录请求
    session.post(url=BiBiPiano_Login_address, data=data_login, headers=headers_login)

"""
    获取钢琴曲HTML内容函数
        参数:
        BiBiPiano_content_address=获取钢琴曲HTML内容地址
        session=session登录,
        headers_download=headers伪装
"""
def Content_BiBIPiano(BiBiPiano_content_address,session,headers_download):
    try:
        # 获取钢琴曲界面的HTML文件内容
        response = session.get(url=BiBiPiano_content_address, headers=headers_download)
        # 返回HTML内容
        return response
    except:
        print(BiBiPiano_content_address,'....链接无效!!!')


"""
    解析每一首钢琴曲下载地址的函数
        入参:
            HTML_ConTent：HTML网页内容
"""
def Analysis_BiBiPiano(HTML_ConTent):
    # 初始化
    HTML_ConTent_etree= html.etree.HTML(HTML_ConTent.text)
    # 解析获取内容,钢琴曲下载地址的集合
    BiBiPiano = HTML_ConTent_etree.xpath('//div[@class="post-inner thin "]/div[@class="entry-content"]//li/a/@href')
    # 返回集合
    return BiBiPiano

"""
    下载歌曲并处理保存
"""
def BiBiPiano_DownLoadANDSave(BiBiPiano_DownLoad_Address, BiBiPiano_DownLoad_Reference_data, session, headers_download,Piano_Name):
    # 判断是否存在这个文件夹
    if not os.path.exists("BiBiPiano"):
        # 创建文件夹
        os.mkdir("BiBiPiano")
    # 处理歌曲的名称
    # Piano_file_txt = BiBiPiano_DownLoad_Reference_data['SourceUrl'].split("/"[-1])[-1].split("-")[1].strip()

    print(Piano_Name + '...下载中!!!=======================>',end='')
    # 文件类型和名称
    path = "./BiBiPiano/" + Piano_Name
    print(path)
    # 下载歌曲
    Piano = session.get(url=BiBiPiano_DownLoad_Address,params = BiBiPiano_DownLoad_Reference_data,headers=headers_download)
    time.sleep(3)
    # 保存歌曲
    with open(path,"wb") as f:
        f.write(Piano.content)  # 把数据写入缓冲区文件
        print('...下载成功!!!')


"""
    使用正则表达式剪切字符串
    入参:
        Rules：规则
        ConText_Shear：内容
"""
def Regex_BiBiPiano(Rules,ConText_Shear):
    # 提取返回
    return re.findall(Rules, ConText_Shear)

"""
    存储已下载钢琴曲的函数
        入参:
            textName:钢琴曲名称
"""
def BiBiPiano_Information_storage(textName):
    fileName = "./BiBiPiano/BiBiPianoInformationstorage.txt" # +textName.split("."[0])[0] + '.txt'
    # 判断是否存在这个文件夹
    if os.path.exists(fileName):
        # 使用文件后自动关闭文件
        with open(fileName, "r") as f:
            # 判断文件是否有内容
            if len(f.readline()) > 0:
                textName = "<====>" + textName
    # 使用文件后自动关闭文件
    with open(fileName, "a") as f:
        f.write(textName)



'''
    主入口
'''
if __name__ == "__main__":
    # 登录账号
    BiBiPiano_Login_enail="账号"
    # 登录密码
    BiBiPiano_Login_pass = "密码"
    # 登录地址
    BiBiPiano_Login_address = "https://bi.bi/membership-login/"
    # 获取钢琴曲网页内容地址
    BiBiPiano_content_address = "https://bi.bi/download/"
    # 歌曲下载的固定地址
    BiBiPiano_DownLoad_Address = "https://linkyoulimited-my.sharepoint.com/personal/piano_bi_bi/_layouts/15/download.aspx"
    # 正则表达式的规则
    Piano_ex1 = '"rootFolder":"(.*?)"'
    CorrelationId_ex2 = '"CorrelationId":"(.*?)"'
    # 过滤的链接
    storage_list = ["https://www.amazon.co.uk/s?k=Silu+Wang&i=digital-music","https://open.spotify.com/artist/0iPptl9CoCTa5LJfTj18uw","https://play.google.com/store/music/artist?id=A52bxlgzbokn7wxlte6s3gmzpfu","https://www.youtube.com/c/bibipiano"]
    # session登录
    session = requests.session()
    # 登录伪装
    headers_login={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'cache-control': 'max-age=0',
        'content-length': '92',
        'content-type': 'application/x-www-form-urlencoded',
        'cookie': '_ga=GA1.2.221398830.1666672017; swpm_in_use=swpm_in_use; swpm_session=6a0d01a4cb0f7ceed1cac6d92afbbcde; _gid=GA1.2.1936078302.1666940059; _gat_gtag_UA_123433910_1=1',
        'origin': 'https://bi.bi',
        'referer': 'https://bi.bi/membership-login/',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
    }
    # 获取钢琴曲页面伪装
    headers_Piano = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    }
    # 下载歌曲的伪装
    headers_download = {
        "accept-language": "zh-CN,zh;q=0.9",
        "sec-ch-ua": '\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"101\", \"Google Chrome\";v=\"101\"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '\"Windows\"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "service-worker-navigation-preload": "true",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36",
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate',
        'If-None-Natch': '',
        'If-Modified-Since': ''
    }
    # 登录
    login_BiBIPiano(BiBiPiano_Login_enail,BiBiPiano_Login_pass,BiBiPiano_Login_address,session,headers_login)
    # 获取钢琴曲内容主页地址,返回HTML
    HTML_ConTent = Content_BiBIPiano(BiBiPiano_content_address, session, headers_Piano)
    # 解析每一首钢琴曲下载地址,返回地址的集合
    BiBiPiano_List = Analysis_BiBiPiano(HTML_ConTent)
    # 下载过的歌曲缓存
    textContent_List = []
    # 先判断是否已经存在文件
    if os.path.exists("./BiBiPiano/BiBiPianoInformationstorage.txt"):
        # 使用文件后自动关闭文件
        with open("./BiBiPiano/BiBiPianoInformationstorage.txt", "r") as f:
            # 读取存储已下载钢琴曲信息文件的内容
            textContent = f.readline()
            # 剪切内容
            textContent_List = textContent.split("<====>")
    # 循环处理字符串和下载歌曲
    for i in BiBiPiano_List:
        # 过滤多余的链接
        if storage_list.count(i) > 0:
            continue
        # 获取钢琴曲的名称内容,返回HTML
        Piano_HTML_ConTent = Content_BiBIPiano(i, session, headers_Piano)
        # 非空判断
        if not (Piano_HTML_ConTent is None):
            # 剪切钢琴曲的名称
            content = Regex_BiBiPiano(Piano_ex1, Piano_HTML_ConTent.text)
            # 非空判断
            if not (content is None):
                # 处理歌曲的名称
                Piano_Name = (content[0].split("/"[-1])[-1]).replace(" ", "")
                # 如果钢琴曲已下载则跳到下一个循环
                if textContent_List.count(Piano_Name):
                    print(Piano_Name+"....已下载到本地")
                    continue
                print(Piano_Name)
                # 剪切CorrelationId
                CorrelationId_content = Regex_BiBiPiano(CorrelationId_ex2, Piano_HTML_ConTent.text)
                # 下载歌曲的入参
                BiBiPiano_DownLoad_Reference_data = {
                    'SourceUrl': content[0],
                    'correlationid': CorrelationId_content[0],
                    'client': "streamvideoplayer"
                }
                text = r'https://linkyoulimited-my.sharepoint.com/personal/piano_bi_bi/_layouts/15/onedrive.aspx?id=' + quote(content[0]) + r'&parent=' + quote('/personal/piano_bi_bi/Documents/Bi.Bi/Audio/FLAC/Unreleased') + r'&ga=1'
                headers_download['referer'] = text
                # 下载歌曲
                BiBiPiano_DownLoadANDSave(BiBiPiano_DownLoad_Address, BiBiPiano_DownLoad_Reference_data, session, headers_download,Piano_Name)
                # 将歌曲名称存储，方便下次再次操作下载的时候，避免重复下载(注：分隔符合："<====>")
                BiBiPiano_Information_storage(Piano_Name)
            else:
                break
        else:
            break

    #关闭连接
    session.close()
    print("程序已结束!!!")

