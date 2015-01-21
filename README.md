Firefly
=======

## About
Firefly is QT based client application for nx.server (Nebula).

## Installation

`local_settings.json` must be created in application directory and edited according your site settings.

```json
[
    {
        "site_name"  : "mysite",
        "hive_ssl"   : true,
        "hive_host"  : "192.168.0.1",
        "hive_port"  : 443,
        "media_host" : "192.168.0.1",    // if not set, hive host will be used
        "media_port" : "80"              // if not set, hive port will be used
    }
]
```

### Windows
Latest windows binaries are available here:

http://repo.imm.cz/firefly-latest.zip

### Linux (Ubuntu 14.04)

```bash
sudo apt-get install python3
```

Firefly requires PyQT 5.3.2 or higher, which is unfortunately present in Ubuntu Trusty

Add Utopic repository to your /etc/apt/sources.list

```
deb http://cz.archive.ubuntu.com/ubuntu/ utopic main restricted
deb-src http://cz.archive.ubuntu.com/ubuntu/ utopic main restricted
```


Create file /etc/apt/preferences with following content
```
Package: *
Pin: release n=trusty
Pin-Priority: 501
```

Then you can install required packages from Utopic repository

```bash
sudo apt-get install -t utopic python3-pyqt5 python3-pyqt5.qtmultimedia libqt5multimedia5-plugins
```

For video playback, you will need gstreamer ffmpeg plugin
```bash
sudo add-apt-repository ppa:mc3man/trusty-media
sudo apt-get update
sudo apt-get install gstreamer0.10-ffmpeg
```