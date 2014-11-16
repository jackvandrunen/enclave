# -*- coding: utf-8 -*-
'''
Add(self, item, tuple pos, tuple span=wx.DefaultSpan, integer flag=0,
    integer border=0, userData=None)
'''

import wx

import sys
import backend


class Main(wx.Frame):
    'The application window'

    status = {0: '[X]', 1: '', 2: '[-]', 3: '[!]'}
    newmsg = '*'

    def __init__(self):
        super(Main, self).__init__(None, -1, title="Enclave", size=(600, 500))
        self.Bind(wx.EVT_IDLE, self.call_api)

        self.init_ui()
        self.Show()

        self.init_backend()

    def init_ui(self):
        'Deals with setting up the GUI'
        self.panel = wx.Panel(self)

        self.grid = wx.GridBagSizer(5, 10)

        self.ipshow = wx.TextCtrl(self.panel,
            value='ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff',
            style=wx.TE_READONLY)
        self.grid.Add(self.ipshow, pos=(0, 0), span=(1, 2), flag=wx.EXPAND)

        self.friendlist = wx.ListBox(self.panel)
        self.grid.Add(self.friendlist, (1, 0), span=(5, 2), flag=wx.EXPAND)

        self.button_ignore = wx.Button(self.panel,
            label="Remove", size=(90, 28))
        self.button_add = wx.Button(self.panel, label="Add", size=(90, 28))
        self.grid.Add(self.button_ignore, pos=(6, 1), flag=wx.BOTTOM)
        self.grid.Add(self.button_add, pos=(6, 0))
        self.button_ignore.Bind(wx.EVT_BUTTON, self.ignore_selected)
        self.button_add.Bind(wx.EVT_BUTTON, self.add_new)

        self.message = wx.TextCtrl(self.panel)
        self.grid.Add(self.message, pos=(6, 2), span=(1, 4),
            flag=wx.EXPAND | wx.RIGHT)

        self.setalias = wx.TextCtrl(self.panel, value="Anon",
            style=wx.TE_PROCESS_ENTER)
        self.grid.Add(self.setalias, pos=(0, 2), span=(1, 4),
            flag=wx.EXPAND)
        self.setalias.Bind(wx.EVT_TEXT_ENTER, self.update_alias)

        self.log = wx.TextCtrl(self.panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.grid.Add(self.log, pos=(2, 2), span=(4, 4), flag=wx.EXPAND)

        self.statusmenu = wx.ComboBox(self.panel,
            choices=['Available', 'Away', 'Busy'], style=wx.CB_READONLY)
        self.grid.Add(self.statusmenu, pos=(1, 2), span=(1, 1))
        self.statusmenu.Bind(wx.EVT_COMBOBOX, self.update_status)

        self.statusmsg = wx.TextCtrl(self.panel, style=wx.TE_PROCESS_ENTER)
        self.grid.Add(self.statusmsg, pos=(1, 3), span=(1, 3), flag=wx.EXPAND)
        self.statusmsg.Bind(wx.EVT_TEXT_ENTER, self.update_statusmsg)

        self.grid.AddGrowableRow(2)
        self.grid.AddGrowableCol(3)

        self.panel.SetSizerAndFit(self.grid)

    def init_backend(self):
        try:
            address = backend.get_address()
            if address is None:
                raise Exception

        except Exception:
            wx.MessageBox('No cjdns interface detected!', 'Error',
                          wx.OK | wx.ICON_ERROR)
            sys.exit(1)

        self.ipshow.ChangeValue(address)

        backend.start()

        node = backend.get_node()
        self.setalias.SetValue(node['alias'])
        self.statusmsg.SetValue(node['status-message'])
        self.statusmenu.SetValue('Available')

        try:
            (self.friends_by_name,
                self.friends_by_obj) = zip(*backend.get_friends())
            self.friendlist.Set(self.friends_by_name)
        except ValueError:
            self.friends_by_name = []
            self.friends_by_obj = []

    def call_api(self, event):
        'An idle event handler, handles calls to the backend'
        friends = backend.get_friends()
        if len(friends) > len(self.friends_by_name):
            for name, peer in friends:
                if peer not in self.friends_by_obj:
                    self.friends_by_name.append(name)
                    self.friends_by_obj.append(peer)
                    self.friendlist.Insert(name, len(self.friends_by_name) - 1)

        for index, name in enumerate(self.friends_by_name):
            status = self.friends_by_obj[index].status
            display = '{0}{1}'.format(self.status[status], name)
            self.friendlist.SetString(index, display)

    def update_status(self, event):
        status = self.statusmenu.GetValue()
        backend.update_info(status=status)

    def update_alias(self, event):
        alias = self.setalias.GetValue()
        if len(alias):
            backend.update_info(alias=alias)
        else:
            self.setalias.SetValue(backend.get_node()['alias'])

    def update_statusmsg(self, event):
        statusmsg = self.statusmsg.GetValue()
        if len(statusmsg):
            backend.update_info(statusmsg=statusmsg)
        else:
            self.statusmsg.SetValue(backend.get_node()['status-message'])

    def ignore_selected(self, event):
        pass

    def add_new(self, event):
        which_function = wx.SingleChoiceDialog(self, 'What do you want to add?',
            'Add...', choices=['Friend', 'Group Chat'])
        which_function.ShowModal()

        if which_function.GetStringSelection() == 'Friend':
            name_prompt = wx.TextEntryDialog(self, "Enter friend's name...",
                caption='Add Friend...')
            name_prompt.ShowModal()
            name = name_prompt.GetValue()
            if name:
                address_prompt = wx.TextEntryDialog(self,
                    "Enter friend's cjdns address...", caption='Add Friend...')
                address_prompt.ShowModal()
                address = address_prompt.GetValue()

                name, peer = backend.add(address, name)
                if peer in self.friends_by_obj:
                    index = self.friends_by_obj.index(peer)
                    self.friends_by_name[index] = name

                else:
                    self.friends_by_name.append(name)
                    self.friends_by_obj.append(peer)
                    self.friendlist.Insert(name, len(self.friends_by_name) - 1)


if __name__ == '__main__':
    app = wx.App(False)
    Main()
    app.MainLoop()
    backend.save_config()
    backend.quit()
