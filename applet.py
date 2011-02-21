#!/usr/bin/python

import gnomeapplet
import gobject
import gtk
import gtk.gdk
import pygtk
import datetime
import settings

from odesk import oDesk

pygtk.require('2.0')

def factory(applet, iid):
    oDeskApplet(applet, iid)
    return gtk.TRUE

class oDeskApplet:
    def __init__(self, applet, iid):
        self.iid = iid
        self.applet = applet
        self.settings = settings.settings()
        self.refresh_timeout = int(self.settings.refreshTimeout) * 60
        self.odesk = oDesk(self.settings)
        self.prevDate = None
        self.chart = gtk.Image()

        self.todayLabel = gtk.Label(' - ')
        self.weekLabel = gtk.Label(' - ')

        self.ev_box = gtk.EventBox()
        self.ev_box.connect("button-press-event", self.showMenu)

        ev_hbox = gtk.HBox()
        self.ev_box.add(ev_hbox)

        label = gtk.Label()
        label.set_markup('<b>Today:</b> ')
        ev_hbox.add(label)
        ev_hbox.add(self.todayLabel)
        
        label = gtk.Label()
        label.set_markup('  <b>Week:</b> ')
        ev_hbox.add(label)
        ev_hbox.add(self.weekLabel)

        self.hbox = gtk.HBox()
        applet.add(self.hbox)
        
        self.hbox.add(self.ev_box)
        label = gtk.Label()
        label.set_markup('   <b>Chart:</b>  ')
        ev_hbox.add(label)
        ev_hbox.add(self.chart)

        applet.connect("destroy", self.cleanup)
        applet.show_all()

        gobject.timeout_add_seconds(self.refresh_timeout, self.refreshHoursTimeout)
        gobject.timeout_add_seconds(30, self.refreshHours)

    def refreshHoursTimeout(self):
        gobject.timeout_add_seconds(self.refresh_timeout, self.refreshHoursTimeout)
        self.refreshHours()

    def refreshHours(self):
        date = datetime.date.today()
        dayHours = self.odesk.dayHours(date)
        self.todayLabel.set_text(dayHours)

        if self.prevDate != date:
            gobject.timeout_add(100, self.refreshWeekHours, date)
        else:
            self.refreshWeekHours(date)

    def refreshWeekHours(self, date):
        gobject.timeout_add(100, self.refreshChart)
        weekHours = self.odesk.weekHours(date)
        self.weekLabel.set_text(weekHours)
        self.prevDate = date

    def refreshChart(self):
        self.odesk.downloadChart()
        self.chart.set_from_file("/tmp/chart.png")

    def showMenu(self, widget, event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            widget.emit_stop_by_name("button_press_event")
            self.setupMenu()
            
    def setupMenu(self):
        propXml = """
            <popup name="button3">
                <menuitem name="Refresh" verb="Refresh" label="_Refresh"
                        pixtype="stock" pixname="gtk-about"/>
            </popup>"""

        verbs = [("Refresh", self.refresh)]
        self.applet.setup_menu(propXml, verbs, None)

    def refresh(self, *arguments, **keywords):
        gobject.timeout_add(100, self.refreshHours)

    def cleanup(self, widget):
        pass

if __name__ == '__main__':
    gnomeapplet.bonobo_factory("OAFIID:Gnome_odesk_Factory",
                               gnomeapplet.Applet.__gtype__,
                               "Show odesk hours", "1.0", factory)

    #if len(sys.argv) == 2 and sys.argv[1] == "run-in-window":
    #    main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    #    main_window.set_title("Python Applet")
    #    main_window.connect("destroy", gtk.mainquit)
    #    app = gnomeapplet.Applet()
    #    factory(app, None)
    #    app.reparent(main_window)
    #    main_window.show_all()
    #    gtk.main()
    #    sys.exit()