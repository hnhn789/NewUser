from kivy.app import App

from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.network.urlrequest import UrlRequest
import urllib
import requests

class TutorialApp(App):
    def build(self):
        b = BoxLayout()

        f = FloatLayout()
        s = Scatter()

        self.MyRequest()
        self.l = Label(text='text', font_size=15)
        f.add_widget(s)
        s.add_widget(self.l)

        b.add_widget(f)
        return b

    # def MyRequest(self):
    #     content = {"name": "Read a book","price":"20","remain":"30"}
    #     request = requests.post("http://127.0.0.1:8000/storypoints/8/", json=content)
    #     print (request.text)

    def MyRequest(self):
        req = UrlRequest(
            'http://127.0.0.1:8000/shop/update/',

            on_success=self.success, on_failure=self.fail)

        # req = UrlRequest(
        #     'http://hnhn789.pythonanywhere.com/email_confirmation/resend/b04202048/',
        #     # 'http://127.0.0.1:8000/accounts/login/',
        #     on_success=self.success, on_failure=self.fail,
        #     on_error=self.error, on_redirect=self.redirected)

        # params = urllib.parse.urlencode({'username': 'hanson', 'password':'hnhn123456','realname':'郭郭','department':'物理二'})
        # headers = {'Content-type': 'application/x-www-form-urlencoded'}
        # req = UrlRequest('http://127.0.0.1:8000/accounts/login/', on_success=self.success, on_failure=self.fail,
        #                  req_body=params,
        #                  req_headers=headers)



    def error(self, reqest, results):
        print("error")
        print(results)

    def success(self, request, results):
        print("success")
        print(results)

    def redirected(self, reqest, results):
        print("redirect")
        print(results)

    def fail(self, reqest, results):
        print("fail")
        print(results)



if __name__ == "__main__":
    TutorialApp().run()