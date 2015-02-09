__author__ = 'crow'

import feedparser
import urllib2
import transmissionrpc
import base64
import os
import logging

series = [
    {
        'title': 'Helix'
    }
]

torrents_path = '/Volumes/home/crow/Downloads/'

def main():

    tc = transmissionrpc.Client('localhost', port=9091,user='admin',password='admin')
    feed = feedparser.parse('http://www.lostfilm.tv/rssdd.xml')
    logging.basicConfig(format='%(asctime)s %(message)s',filename='example.log',level=logging.INFO, datefmt='%m-%d-%Y %H:%M:%S')

    for entry in feed.entries:
        for serie_info in series:

            title = serie_info['title']
            regexp = serie_info.get('regexp', title)
            quality = serie_info.get('quality','')
            download_path = serie_info.get('download_path', title)
            download_dir = torrents_path + download_path
            torrent_filename = entry.link.split("&")[1]

            if all([regexp in entry.title, quality in entry.link]):
                request = urllib2.Request(
                    entry.link,
                    headers={
                        "Cookie": " uid=****; pass=****; usess=****",
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:34.0) Gecko/20100101 Firefox/34.0"
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
                    pass
                pass

if __name__ == "__main__":
    main()