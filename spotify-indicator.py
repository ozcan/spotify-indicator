#!/usr/bin/env python
# -*- coding: utf-8; -*-
"""
Copyright (C) 2013 - Özcan ESEN <ozcanesen@gmail.com>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>

"""

import appindicator
import gtk
import dbus
import threading
import gobject
import time
import subprocess
import os

bus = dbus.SessionBus()

try:
    spotify = bus.get_object('com.spotify.qt', '/')
    player = dbus.Interface(spotify, 'org.freedesktop.MediaPlayer2')
    properties_manager = dbus.Interface(spotify, 'org.freedesktop.DBus.Properties')
    player.OpenUri('')
except:
    proc = subprocess.Popen(['/opt/spotify/spotify-client/spotify'], stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'))
    wait_for_spotify = True
    while wait_for_spotify:
        try:
            spotify = bus.get_object('com.spotify.qt', '/')
            player = dbus.Interface(spotify, 'org.freedesktop.MediaPlayer2')

            proxy = bus.get_object('com.spotify.qt', '/org/mpris/MediaPlayer2')
            properties_manager = dbus.Interface(proxy, 'org.freedesktop.DBus.Properties')
            info = player.GetMetadata()
            wait_for_spotify = False
        except:
            time.sleep(0.1)


indicator = appindicator.Indicator('spotify-indicator', '/opt/spotify/spotify-client/spotify16x16.png', appindicator.CATEGORY_APPLICATION_STATUS)
indicator.set_status(appindicator.STATUS_ACTIVE)

# build menu
menu = gtk.Menu()

song_info = gtk.MenuItem('')
song_info.set_sensitive(False)
menu.append(song_info)

menu.append(gtk.MenuItem())

menu_hide = gtk.MenuItem('Hide Spotify')
menu_hide.hide()
menu.append(menu_hide)

menu_open = gtk.MenuItem('Open Spotify')
menu.append(menu_open)

menu.append(gtk.MenuItem())

play = gtk.MenuItem('Play')
play_seperator = gtk.MenuItem()
menu.append(play)
menu.append(play_seperator)

pause = gtk.MenuItem('Pause')
menu.append(pause)

next = gtk.MenuItem('Next')
menu.append(next)

prev = gtk.MenuItem('Previous')
menu.append(prev)

menu.append(gtk.MenuItem())

shuffle = gtk.CheckMenuItem('Shuffle')
menu.append(shuffle)

repeat = gtk.CheckMenuItem('Repeat')
menu.append(repeat)

menu.append(gtk.MenuItem())

quit = gtk.MenuItem( 'Quit' )
menu.append(quit)

indicator.set_menu(menu)
menu.show_all()
menu_open.hide()

def quit_callback(item):
    spotify.Quit()
    indicator.set_status(appindicator.STATUS_PASSIVE)
    gtk.main_quit()

def hide_callback(item):
    main_window = bus.get_object('com.spotify.qt', '/MainWindow')
    main_window.closeAllWindows()

    menu_hide.hide()
    menu_open.show()

def open_callback(item):
    player.OpenUri('')

    if player.CanRaise():
        player.Raise()

    menu_hide.show()
    menu_open.hide()
    
def next_callback(item):
    player.Next()

def prev_callback(item):
    player.Previous()

def play_callback(item):
    spotify.PlayPause()

def pause_callback(item):
    spotify.Pause()


quit.connect('activate', quit_callback)
menu_hide.connect('activate', hide_callback)
menu_open.connect('activate', open_callback)
next.connect('activate', next_callback)
prev.connect('activate', prev_callback)
play.connect('activate', play_callback)
pause.connect('activate', pause_callback)

gobject.threads_init()

class update(threading.Thread):
    def __init__(self, m1, m2, m3, m4, m5, m6):
        super(update, self).__init__()
        self.song_info = m1
        self.menu_open = m2
        self.menu_hide = m3
        self.play = m4
        self.play_seperator = m5
        self.pause = m6

        self.playback_status = properties_manager.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')
        self.quit = False

    def update(self):
        try:
            if self.playback_status != properties_manager.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus'):
                self.playback_status = properties_manager.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')
                if self.playback_status == 'Playing':
                    self.play.hide()
                    self.play_seperator.hide()
                    self.pause.show()
                else:
                    self.play.show()
                    self.play_seperator.show()
                    self.pause.hide()

            try:
                info = player.GetMetadata()
                self.song_info.set_label(str(info['xesam:artist'][0]) + " - " + str(info['xesam:title']))
            except:
                self.song_info.set_label("No tracks playing")

        except dbus.exceptions.DBusException:
            gtk.main_quit()

        #print properties_manager.Get('org.mpris.MediaPlayer2.Player', 'LoopStatus')
        #print properties_manager.Get('org.mpris.MediaPlayer2.Player', 'Shuffle')

        return False

    def run(self):
        while not self.quit:
            gobject.idle_add(self.update)
            time.sleep(0.1)

t = update(song_info, menu_open, menu_hide, play, play_seperator, pause)
t.start()

try:
    gtk.main()
    t.quit = True
except KeyboardInterrupt:
    t.quit = True
