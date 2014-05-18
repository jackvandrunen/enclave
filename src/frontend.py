# -*- coding: utf-8 -*-
'''
Add(self, item, tuple pos, tuple span=wx.DefaultSpan, integer flag=0, 
    integer border=0, userData=None)
'''

import wx


class Main(wx.Frame):
    'The application window'

    def __init__(self):
        super(Main, self).__init__(None, -1, title="Enclave", size=(600, 500))
        self.Bind(wx.EVT_IDLE, self.call_api)

        self.init_ui()
        self.Show()

    def init_ui(self):
        'Deals with setting up the GUI'
        panel = wx.Panel(self)

        grid = wx.GridBagSizer(5, 5)

        friendlist = wx.ListBox(panel)
        grid.Add(friendlist, (1, 1), span=(6, 2), flag=wx.EXPAND)

        button_ignore = wx.Button(panel, label="Ignore", size=(90, 28))
        button_add = wx.Button(panel, label="Add", size=(90, 28))
        grid.Add(button_ignore, pos=(7, 1), flag=wx.BOTTOM)
        grid.Add(button_add, pos=(7, 2))

        message = wx.TextCtrl(panel)
        grid.Add(message, pos=(7, 3), span=(1, 4), flag=wx.EXPAND | wx.RIGHT)

        log = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        grid.Add(log, pos=(3, 3), span=(4, 4), flag=wx.EXPAND)

        ipshow = wx.StaticText(panel, label='ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff')
        grid.Add(ipshow, pos=(1, 3), span=(1, 4), flag=wx.EXPAND)

        statusmenu = wx.ComboBox(panel, choices=['Available'], style=wx.CB_READONLY)
        grid.Add(statusmenu, pos=(2, 3), span=(1, 1))

        statusmsg = wx.TextCtrl(panel)
        grid.Add(statusmsg, pos=(2, 4), span=(1, 3), flag=wx.EXPAND)

        panel.SetSizerAndFit(grid)

    def call_api(self, event):
        'An idle event handler, handles calls to the backend'


if __name__ == '__main__':
    app = wx.App(False)
    Main()
    app.MainLoop()
