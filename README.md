Firefly
=======

## About
Firefly is QT based client application for [Nebula](https://github.com/opennx/nx.server).

## Installation

`local_settings.json` must be created in application directory and edited according your site settings.

```json
[
    {
        "site_name"  : "mysite",
        "hive_ssl"   : true,
        "hive_host"  : "192.168.0.1",
        "hive_port"  : 443,
        "media_host" : "192.168.0.1",
        "media_port" : "80"
    }
]
```
You can define multiple sites in settings file. You will be prompted which site you want to connect during
application start-up. In site definition, following parameters are available.

 - `site_name` (required)
 - `hive_host` (required)
 - `hive_port` (required)
 - `hive_ssl` (optional, default false) - Use ssl for hive requests
 - `hive_gzip` (optional, default false) - compress hive responses
 - `hive_timeout` (optional, default 3) - Max request timeout in seconds
 - `media_host` (optional) - Use another server for proxies and thumbs (ip or hostname)
 - `media_port` (optional) - Use another server for proxies and thumbs (port #)
 - `debug` (optional, default false) - debug mode (more verbose logging etc.)

### Windows
Latest windows binaries are available here:

http://repo.imm.cz/firefly-latest.zip

### Linux (Ubuntu 16.04)

```bash
sudo apt-get update
sudo apt-get install python3 python3-pyqt5 python3-pyqt5.qtmultimedia libqt5multimedia5-plugins
```


## Notes

 - Firefly saves it's state to file `state.HOSTNAME.SITENAME.nxsettings`. If you encounter problems with UI,
   it is possible to restore default state by deleting this file.




