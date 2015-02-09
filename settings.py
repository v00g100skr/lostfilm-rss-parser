__author__ = 'crow'

SERIES = [
    {
        'title': 'Helix'
    }, {
        'title': 'Forever',
        'download_path': 'Forever',
        'quality': '1080p'
    }
]

TORRENTS_PATH = '*****'

UID = "*****"
PASS = "*****"
USESS = "*****"

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:34.0) Gecko/20100101 Firefox/34.0"

TRANSMISSION_HOST = "localhost"
TRANSMISSION_PORT = 9091
TRANSMISSION_USER = "admin"
TRANSMISSION_PASS = "admin"

try:
    import local
    UID = local.UID
    PASS = local.PASS
    USESS = local.USESS
    TORRENTS_PATH = local.TORRENTS_PATH
except:
    pass
