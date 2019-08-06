# -*- coding: utf-8 -*-
"""
Created on Sun Aug  4 23:09:58 2019

@author: HouLw
"""

from selenium import webdriver
import time
import json
import requests
import re
import random


#设置要爬取的公众号列表
gzlist=['人民日报']

#登录微信公众号，获取登录之后的cookies信息，并保存到本地文本中
def weChat_login():
    #定义一个空的字典，存放cookies内容
    post = {}
    driver_path = r"C:\chromedriver\chromedriver.exe"
    driver = webdriver.Chrome(executable_path=driver_path)
    driver.get('https://mp.weixin.qq.com')
    time.sleep(2)
    
    driver.find_element_by_name('account').clear()
    driver.find_element_by_name('account').send_keys('xxxxxxxxxxx@qq.com')
    driver.find_element_by_name('password').clear()
    driver.find_element_by_name('password').send_keys('xxxxxxx')
    
    # 自动输入密码后点击记住密码
    time.sleep(5)
    driver.find_element_by_xpath("./*//a[@class='btn_login']").click()
    # 扫码
    time.sleep(20)
    driver.get('https://mp.weixin.qq.com')
    cookie_items = driver.get_cookies()
    for cookie_item in cookie_items:
        post[cookie_item['name']] = cookie_item['value']
    cookie_str = json.dumps(post)
    with open('cookie.txt', 'w+', encoding='utf-8') as f:
        f.write(cookie_str)
        print('cookie write ok ...')

#爬取微信公众号文章，并存在本地文本中
def get_content(query):
    #query为要爬取的公众号名称
    #公众号主页
    url = 'https://mp.weixin.qq.com'
    #设置headers
    header = {
        "HOST": "mp.weixin.qq.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0"
        }

    #读取上一步获取到的cookies 
    with open('cookie.txt', 'r', encoding='utf-8') as f:
        cookie = f.read()
    cookies = json.loads(cookie)

    #登录之后的微信公众号首页url变化为：https://mp.weixin.qq.com/cgi-bin/home?t=home/index&lang=zh_CN&token=1849751598，从这里获取token信息
    response = requests.get(url=url, cookies=cookies)
    token = re.findall(r'token=(\d+)', str(response.url))[0]

    #搜索微信公众号的接口地址
    search_url = 'https://mp.weixin.qq.com/cgi-bin/searchbiz?'
    #搜索微信公众号接口需要传入的参数，有三个变量：微信公众号token、随机数random、搜索的微信公众号名字
    query_id = {
        'action': 'search_biz',
        'token' : token,
        'lang': 'zh_CN',
        'f': 'json',
        'ajax': '1',
        'random': random.random(),
        'query': query,
        'begin': '0',
        'count': '5'
        }  
    #打开搜索微信公众号接口地址，需要传入相关参数信息如：cookies、params、headers
    search_response = requests.get(search_url, cookies=cookies, headers=header, params=query_id)
    #取搜索结果中的第一个公众号
    lists = search_response.json().get('list')[0]
    #获取这个公众号的fakeid，后面爬取公众号文章需要此字段
    fakeid = lists.get('fakeid')

    #微信公众号文章接口地址
    appmsg_url = 'https://mp.weixin.qq.com/cgi-bin/appmsg?'
    #搜索文章需要传入几个参数：登录的公众号token、要爬取文章的公众号fakeid、随机数random
    query_id_data = {
        'token': token,
        'lang': 'zh_CN',
        'f': 'json',
        'ajax': '1',
        'random': random.random(),
        'action': 'list_ex',
        'begin': '0',#不同页，此参数变化，变化规则为每页加5
        'count': '5',
        'query': '',
        'fakeid': fakeid,
        'type': '9'
        }
    #打开搜索的微信公众号文章列表页
    appmsg_response = requests.get(appmsg_url, cookies=cookies, headers=header, params=query_id_data)
    #获取文章总数
    max_num = appmsg_response.json().get('app_msg_cnt')
    #每页至少有5条，获取文章总的页数，爬取时需要分页爬
    num = int(int(max_num) / 5)
    #起始页begin参数，往后每页加5
    begin = 0
    while num + 1 > 0 :
        query_id_data = {
            'token': token,
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': '1',
            'random': random.random(),
            'action': 'list_ex',
            'begin': '{}'.format(str(begin)),
            'count': '5',
            'query': '',
            'fakeid': fakeid,
            'type': '9'
            }
        print('正在翻页：--------------',begin)
        print(query_id_data)
        print(cookies)
        #获取每一页文章的标题和链接地址，并写入本地文本中
        query_fakeid_response = requests.get(appmsg_url, cookies=cookies, headers=header, params=query_id_data)
        fakeid_list = query_fakeid_response.json().get('app_msg_list')
        for item in fakeid_list:
            content_link=item.get('link')
            content_title=item.get('title')
            print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
            print(content_link)
            print(content_title)
            print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
            
#            fileName=query+'.txt'
#            with open(fileName,'a',encoding='utf-8') as fh:
#                fh.write(content_title+":\n"+content_link+"\n")
        num -= 1
        begin = int(begin)
        begin+=5
        time.sleep(2)
        break

if __name__=='__main__':

#登录微信公众号，获取登录之后的cookies信息，并保存到本地文本中
    weChat_login()
#登录之后，通过微信公众号后台提供的微信公众号文章接口爬取文章
    for query in gzlist:
        #爬取微信公众号文章，并存在本地文本中
        print("开始爬取公众号："+query)
        get_content(query)
        print("爬取完成")
#    except Exception as e:
#        print(str(e))

    
