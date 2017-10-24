# -*- coding: utf-8 -*-
import scrapy
from WIFI.items import wifiItem
import re
import time
import json
import urllib.request, urllib.parse, urllib.error
import http.cookiejar


class wifiSpider(scrapy.Spider):
    name = "wifi"
    allowed_domains = ["192.168.10.1","172.168.11.1"]
    start_urls = [
        "http://192.168.10.1/",
        "http://172.168.11.1/",
    ]
    cookie = {'username':'admin%%admin','hash_key':'5937455636943147,session_id=3095605555140078'}


    def start_requests(self):
        for url in self.start_urls:
            login_url = url + "login.cgi"
            print(login_url)
            cookie = self.router_login(login_url)
            wlan_url = url + "wlan_sta.cgi"
            print(wlan_url)
            yield scrapy.Request(url=wlan_url,
                                 cookies=cookie,
                                 callback=self.parse_with_cookie,
                                 method='GET')




    def parse_with_cookie(self, response):
        print("===========")
        if response.status == 200:
            # print(response.body)
            cookie = {}
            reponseCookie = response.headers.getlist('Set-Cookie')
            cookie['Set-Cookie'] = str(reponseCookie[0],'utf-8')
            print(cookie)
            # self.save_cookis(self.cookie)

            trList = response.xpath("//form[@id='iform']/table[@class='table_01']").extract()
            pageUrl = response.xpath("//form[@id='iform']/table[@class='paging']//div[@class='quotes']/span[last()-1]").extract()
            macList = re.findall("[A-Z0-9:]{17}",trList[0])
            macList = list(set(macList))
            print(macList)
            print(pageUrl)
            itemList = self.mac_cmp(macList)
            print(itemList)
            if not itemList is None:
                for it in itemList:
                    item = wifiItem()
                    item['mac'] = it['mac']
                    item['date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(it['date']))
                    yield item


            isLast = re.findall(r"class=\"pageenabled\"", pageUrl[0])
            if len(isLast)>0:
                nextUrl = "http://"+self.allowed_domains[0] +"/"+ re.findall(r"href=\"(.+)\"",pageUrl[0])[0]
                nextUrl = nextUrl.replace("&amp;","&")
                print(nextUrl)
                yield scrapy.Request(url=nextUrl, cookies=cookie, callback=self.parse_with_cookie,
                                     method='GET')


    def mac_cmp(self,itemlist):
        addList = []
        delList = []
        dictList = self.get_mac_list()
        for it in itemlist:
            flag = False
            for user in dictList:
                if it == user['mac']:
                    user["date"] = time.time()
                    flag = True
            if not flag:
                item = {'mac': '', 'date': ''}
                item['mac'] = it
                item['date'] = time.time()
                addList.append(item)
                # yield item

        dictList.extend(addList)
        now = time.time()
        for user in dictList:
            last = user['date']
            if now - last > 60:
                delList.append(user)
                # yield item

        for user in delList:
            del dictList[dictList.index(user)]

        self.save_mac_list(dictList)
        resList = []
        resList.extend(addList)
        resList.extend(delList)
        return resList

    def get_mac_list(self):
        file = open('./result.txt')
        dictList = []
        try:
            text = file.read()
            if not (text is None or text == ''):
                list = json.loads(text)
                dictList.extend(list['list'])
        finally:
            file.close()
        return dictList

    def save_mac_list(self,dictlist):
        save = {'list': dictlist}
        file = open('./result.txt', "wb")
        try:
            jsontext = json.dumps(dict(save), ensure_ascii=False)
            file.write(jsontext.encode("utf-8"))
        finally:
            file.close()

    def router_login(self,login_url):
        body = {'username': 'admin', 'password': 'admin', 'selectLanguage': 'CH', 'OKBTN': '登录'}
        postdata = urllib.parse.urlencode(body).encode()
        user_agent = r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'
        headers = {'User-Agent': user_agent, 'Connection': 'keep-alive'}
        cookie = http.cookiejar.CookieJar()
        handler = urllib.request.HTTPCookieProcessor(cookie)
        opener = urllib.request.build_opener(handler)
        request = urllib.request.Request(login_url, postdata, headers)
        cookies = {}
        try:
            response = opener.open(request)
            # page = response.read().decode()
            # print(page)
            rsp_headers = response.headers.__str__().split('\n')
            if (len(rsp_headers) < 3):
                raise ValueError('Header ERROR')
            else:
                cookies_str = rsp_headers[2]
                cookies_arr = cookies_str.split(":")
                if (len(cookies_arr) < 2):
                    raise ValueError('Cookie ERROR')
                else:
                    key = cookies_arr[0].strip(' ')
                    value = cookies_arr[1].strip(' ')
                    cookies[key] = value
                    print("登录成功")
        except urllib.error.URLError as e:
            print(e.code, ':', e.reason)
        except http.client.RemoteDisconnected as ex:
            print('远程连接失败',':',ex)
        except ValueError as ve:
            print('取值不正确',':',ve)

        print("Cookies: " + str(cookies))
        return cookies


    #
    # def get_cookie(self):
    #     file = open("./cookie.txt")
    #     cookie = {}
    #     try:
    #         cookie = file.read()
    #         cookie = json.loads(cookie)
    #     finally:
    #         file.close()
    #
    #     print(cookie)
    #     return cookie
    #
    # def save_cookis(self,cookie):
    #     print(cookie)
    #     file = open("./cookie.txt","wb")
    #     try:
    #         jsontext = json.dumps(dict(cookie), ensure_ascii=False)
    #         file.write(jsontext.encode("utf-8"))
    #     finally:
    #         file.close()