# -*- coding: utf-8 -*-


import wx


class Main(wx.Frame):
    'The application window'

    def __init__(self):
        super(Main, self).__init__(None, -1, title="Enclave", size=(550, 500))
        self.Bind(wx.EVT_IDLE, self.call_api)

        self.init_ui()
        self.Show()

    def init_ui(self):
        'Deals with setting up the GUI'

    def call_api(self, event):
        'An idle event handler, handles calls to the backend'


if __name__ == '__main__':
    app = wx.App(False)
    Main()
    app.MainLoop()
