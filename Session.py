# jacked this from https://github.com/billvb/openokc-api

import BeautifulSoup
import requests


class OKCSession(object):

    def __init__(self, username=None, password=None):
        import requests
        self.session = requests.Session()
        self.username = username
        self.password = password
        self.logged_in = False
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/'
                          '537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 '
                          'Safari/537.36',
            'content-type': 'application/json'}
        self.credentials = {
            'username': self.username,
            'password': self.password}

    def __str__(self):
        return '<openokc.Session: %s>' % self.username

    def _request_page(self, page='/', method='GET', data=None):
        """All page requests MUST use this wrapper function"""

        if '://' in page:
            url = page
        else:
            url = 'https://www.okcupid.com' + page

        print 'Requesting %s %s' % (method, url)

        if method == 'GET':
            response = self.session.get(url,
                                        headers=self.headers,
                                        data=data)
        elif method == 'POST':
            response = self.session.post(url,
                                         headers=self.headers,
                                         data=data)
        else:
            raise AssertionError('Invalid HTTP request method')

        print 'Status %d' % response.status_code
        log_file = open('request-%d.html' % response.status_code, 'w')
        log_file.write(self._render_html(response.text.encode('utf8')))
        return self._render_html(response.text.encode('utf8'))

    def _request_photo(self, photo_url):
        print 'Requesting image: %s' % photo_url
        response = self.session.get(photo_url)
        if response.status_code == 200:
            return response.content
        else:
            raise Exception('Cannot request image %s (status = %d)' %
                            (photo_url, response.status_code))

    def _render_html(self, utf8_content):
        #return BeautifulSoup.BeautifulSoup(utf8_content).prettify()
        return utf8_content

    def _render_pretty_html(self, utf8_content):
        """Does HTML indenting and line breaking - makes it human readable"""
        return BeautifulSoup.BeautifulSoup(utf8_content).prettify()

    def login(self):
        r = self._request_page('/login', method='POST', data=self.credentials)
        try:
            self.session.cookies['session']
            self.logged_in = True
        except:
            raise Exception('login failed')

    def logout(self):
        r = self._request_page('/logout', method='GET')
