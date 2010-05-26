# -*- coding: utf-8 -*-
#
# mixi.py
#
import httplib
import htmllib
import re
import urllib
#from BeautifulSoup import BeautifulSoup

class Mixi(object):
    HOST = "mixi.jp"
    GET = "GET"
    POST = "POST"

    REDIRECT = "&redirect=recent_echo"

    def __init__(self, user, password, use_ssl = False):
        self.user = user
        self.password = password
        self.use_ssl = use_ssl
        self.cookie = None

    # 文字列デコード
    def _decode(self, str):
        encodings = ["ascii", "utf-8", "shift-jis", "euc-jp"]
        for enc in encodings:
            try:
                unicode(str, enc)
                break
            except:
                enc = ""
        return str.decode(enc)

    # http request
    def _request(self, method, path, body = None):
        if self.use_ssl == True:
            http = httplib.HTTPSConnection(self.HOST)
        else:
            http = httplib.HTTPConnection(self.HOST)

        if self.cookie == None:
            http.request(method, path, body)
        else:
            headers = {'Cookie':self.cookie, 'Content-Type':'application/x-www-form-urlencoded'}
            http.request(method, path, body, headers)

        res = http.getresponse()

        return res

    # htmlからpost_keyを取り出す
    def _get_post_key(self):
        # 発言、削除時に必要なキー
        res = self._request(self.GET, "/recent_voice.pl")

        #パースに失敗してしまうので、別の方法にした
        #soup = BeautifulSoup(res.read().decode('euc-jp'))

        body = res.read().decode('euc-jp')
        input = re.compile('<input.*id="post_key".*?>').findall(body)[0]
        start = input.find('value="') + 7
        end = input.find('"', start)
        post_key = input[start:end]

        self.post_key = "&post_key=" + post_key

    # ログイン
    def login(self):
        path = "/login.pl"

        email = "email=" + self.user
        password = "&password=" + self.password
        next_url = "&next_url=/home.pl"

        body = email + password + next_url
        res = self._request(self.POST, path, body)

        # セッション情報
        cookie = res.getheader("set-cookie")
        bf_session = re.compile("BF_SESSION=.*?;").findall(cookie)[0]
        bf_stamp = re.compile("BF_STAMP=.*?;").findall(cookie)[0]
        self.cookie = bf_session + " " + bf_stamp

        # ログイン後、SSLが有効なままだと何故か動かないので無効にする(要調査)
        self.use_ssl = False

        # post_key取得
        self._get_post_key()

    # add echo (発言)
    def add_echo(self, message):
        path = "/add_voice.pl"

        if len(message) > 150:
            raise ValueError("Too long (>150)")

        # body
        body = "body=" + urllib.quote(self._decode(message).encode("euc-jp")) + self.post_key + self.REDIRECT

        self._request(self.POST, path, body)
