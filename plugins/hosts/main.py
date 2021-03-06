from ajenti.ui import *
from ajenti.app.helpers import *

import backend


class HostsPlugin(CategoryPlugin):
    text = 'Hosts'
    icon = '/dl/hosts/icon_small.png'
    folder = 'system'

    def on_init(self):
        be = backend.Config(self.app)
        self.hosts = be.read()
        self.hostname = be.gethostname()
         
    def on_session_start(self):
        self._log = ''
        self._editing = None
        self._editing_self = False
        
    def get_ui(self):
        panel = UI.PluginPanel(
                    UI.Label(text='The static lookup table for hostnames'), 
                    title='Hosts', 
                    icon='/dl/hosts/icon.png'
                )

        t = UI.DataTable(UI.DataTableRow(
            UI.Label(text='IP address'),
            UI.Label(text='Hostname'),
            UI.Label(text='Aliases'),
            UI.Label(),
            header = True
        ))
        for h in self.hosts:
            t.append(UI.DataTableRow(
                UI.Label(text=h.ip),
                UI.Label(text=h.name),
                UI.Label(text=h.aliases),
                UI.DataTableCell(
                    UI.HContainer(
                        UI.MiniButton(
                            id='edit/' + str(self.hosts.index(h)), 
                            text='Edit'
                        ),
                        UI.WarningMiniButton(
                            id='del/' + str(self.hosts.index(h)),
                            text='Delete', 
                            msg='Remove %s from hosts'%h.ip
                        )
                    ),
                    hidden=True
                )
            ))
        t = UI.VContainer(
                t, 
                UI.HContainer(
                    UI.Button(text='Add host', id='add'),
                    UI.Button(text='Change hostname', id='hostname')
                )
            )

        if self._editing is not None:
            try:
                h = self.hosts[self._editing]
            except:
                h = backend.Host()
            t.append(self.get_ui_edit(h))

        if self._editing_self:
            t.append(UI.InputBox(text='Hostname:', value=self.hostname, id='dlgSelf'))

        panel.append(t)
        return panel

    def get_ui_edit(self, h):
        dlg = UI.DialogBox(
            UI.VContainer(
                UI.LayoutTable(
                    UI.LayoutTableRow(
                        UI.Label(text='IP address:'), 
                        UI.TextInput(name='ip', value=h.ip)
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='Hostname:'), 
                        UI.TextInput(name='name', value=h.name)
                    ),
                    UI.LayoutTableRow(
                        UI.Label(text='Aliases:'), 
                        UI.TextInput(name='aliases', value=h.aliases)
                    )
            )),
            id = 'dlgEdit'
        )

        return dlg

    @event('minibutton/click')
    @event('button/click')
    @event('linklabel/click')
    def on_click(self, event, params, vars = None):
        if params[0] == 'add':
            self._editing = len(self.hosts)
        if params[0] == 'edit':
            self._editing = int(params[1])
        if params[0] == 'del':
            self.hosts.pop(int(params[1]))
            backend.Config(self.app).save(self.hosts)
        if params[0] == 'hostname':
            self._editing_self = True

    @event('dialog/submit')
    def on_submit(self, event, params, vars = None):
        if params[0] == 'dlgEdit':
            v = vars.getvalue('value', '')
            if vars.getvalue('action', '') == 'OK':
                h = backend.Host()
                h.ip = vars.getvalue('ip', 'none')
                h.name = vars.getvalue('name', 'none')
                h.aliases = vars.getvalue('aliases', '')
                try:
                    self.hosts[self._editing] = h
                except:
                    self.hosts.append(h)
                backend.Config(self.app).save(self.hosts)
            self._editing = None
        if params[0] == 'dlgSelf':
            v = vars.getvalue('value', '')
            if vars.getvalue('action', '') == 'OK':
                backend.Config(self.app).sethostname(v)
            self._editing_self = None


class HostsContent(ModuleContent):
    module = 'hosts'
    path = __file__
