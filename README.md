Spotify Indicator
=================

Spotify Indicator replacement for Pantheon Desktop Environment.

[Related bug report](https://bugs.launchpad.net/wingpanel/+bug/1170998)


Screenshot
----------
![spotify-indicator](http://i.imgur.com/CoNbq2p.png)

Installing
----------

First you need to disable Spotify's indicator. Spotify is using `sni-qt` package to show indicator. Removing that package will disable indicator but this solution will affect other Qt based applications like Skype.

But we got another option to do that. after some research i discovered that this task can be done using AppArmor.

I wrote an experimental AppArmor profile, copy this profile and reload AppArmor.

```
sudo cp spotify /etc/apparmor.d/spotify
```
```
sudo service apparmor reload
```

Then copy status icon,
```
sudo cp spotify16x16.png /opt/spotify/spotify-client/spotify16x16.png
```

Final step. just replace ```/usr/bin/spotify``` symbolic link with ```spotify-indicator.py```
```
sudo rm /usr/bin/spotify
```
```
sudo cp spotify-indicator.py /usr/bin/spotify
```
```
sudo chmod +x /usr/bin/spotify
```

TO DO
-----
Shuffle and Repeat menu items not working and commented out in code because those Dbus functions not working properly.

Copyright
---------
Spotify and Spotify logo are registered trademarks of [Spotify](https://www.spotify.com)
