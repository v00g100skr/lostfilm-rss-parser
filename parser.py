__author__ = 'crow'

import feedparser
import urllib2
import transmissionrpc
import base64
import os
import logging
import settings

def main():

    tc = transmissionrpc.Client(
        settings.TRANSMISSION_HOST,
        port=settings.TRANSMISSION_PORT,
        user=settings.TRANSMISSION_USER,
        password=settings.TRANSMISSION_PASS)

    feed = feedparser.parse('http://www.lostfilm.tv/rssdd.xml')
    logging.basicConfig(format='%(asctime)s %(message)s',filename='example.log',level=logging.INFO, datefmt='%m-%d-%Y %H:%M:%S')

    for entry in feed.entries:
        for serie_info in settings.SERIES:

            title = serie_info['title']
            regexp = serie_info.get('regexp', title)
            quality = serie_info.get('quality','')
            download_path = serie_info.get('download_path', title)
            download_dir = settings.TORRENTS_PATH + download_path
            torrent_filename = entry.link.split("&")[1]

            if all([regexp in entry.title, quality in entry.link]):
                request = urllib2.Request(
                    entry.link,
                    headers={
                        "Cookie": " uid={}; pass={}; usess={}".format(settings.UID,settings.PASS,settings.USESS),
                        "User-Agent": settings.USER_AGENT
                    })
                torrent = urllib2.urlopen(request)
                buffer = torrent.read()
                if len(buffer) > 0:
                    #output = open(torrent_filename, 'wb')
                    #output.write(buffer)
                    #output.close()
                    if not os.path.exists(download_dir):
                        os.makedirs(download_dir)
                    tc.add_torrent(base64.b64encode(buffer), download_dir=download_dir)
                    logging.info(torrent_filename)

if __name__ == "__main__":
    main()