__author__ = 'crow'

import feedparser
import urllib2
import transmissionrpc
import base64
import os
import logging.config
import settings
import yaml

from transmissionrpc import TransmissionError

def main():

    feed = feedparser.parse('http://www.lostfilm.tv/rssdd.xml')

    logging.config.dictConfig(yaml.load(open('logging.yaml', 'r')))

    log_process = logging.getLogger('process')
    log_error = logging.getLogger('error')
    log_download = logging.getLogger('download')

    downloaded_torrents = []

    file=open("download.log",'r')
    row = file.readlines()
    for line in row:
        items = line.split(" ")
        downloaded_torrents.append(items[1].replace("\n",''))
    file.close()

    try:
        tc = transmissionrpc.Client(
            address=settings.TRANSMISSION_HOST,
            port=settings.TRANSMISSION_PORT,
            user=settings.TRANSMISSION_USER,
            password=settings.TRANSMISSION_PASS)
        log_process.info('connected to transmission ({}:{})'.format(settings.TRANSMISSION_HOST,settings.TRANSMISSION_PORT))
    except TransmissionError as e:
        log_error.error('{} : {}'.format('TransmissionError',e.message))
        tc = False

    for entry in feed.entries:

        torrent_filename = entry.link.split("&")[1]
        log_process.info('processing entry "{}"'.format(torrent_filename))

        for serie_info in settings.SERIES:

            title = serie_info['title']
            regexp = serie_info.get('regexp', title)
            quality = serie_info.get('quality','')
            download_path = serie_info.get('download_path', title)
            download_dir = settings.TORRENTS_PATH + download_path

            if all([regexp in entry.title, quality in entry.link]):
                if torrent_filename in downloaded_torrents:
                    log_process.info('{} already in transmission - skipping'.format(torrent_filename))
                    continue
                log_process.info('{} matched'.format(torrent_filename))
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
                        log_process.info('creating dir "{}"'.format(download_dir))
                    if tc:
                        tc.add_torrent(base64.b64encode(buffer), download_dir=download_dir)
                        log_download.info(torrent_filename)
                        log_process.info('{} added to transmission'.format(torrent_filename))
                    else:
                        log_error.error('no connection  to transmission - skipping')
                else:
                    log_process.warning('{} has zero size'.format(torrent_filename))

if __name__ == "__main__":
    main()