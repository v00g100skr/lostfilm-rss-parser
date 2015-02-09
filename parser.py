__author__ = 'crow'

import feedparser
import urllib2
import transmissionrpc
import base64
import os
import logging.config
import yaml

from transmissionrpc import TransmissionError

def main():

    config = yaml.load(open('config.yml', 'r'))

    path = {}
    regexp = {}
    quality = {}

    for quality_id, series in config['series'].iteritems():
        for serie in series:
            if type(serie) is dict:
                for serie_name,serie_data in serie.iteritems():
                    path[serie_name] = serie_data.get('path',serie_name)
                    regexp[serie_name] = serie_data.get('alternate_name',serie_name)
                    quality[serie_name] = quality_id
            else:
                path[serie] = serie
                regexp[serie] = serie
                quality[serie] = quality_id

    feed = feedparser.parse(config['lostfilm']['feed'])

    logging.config.dictConfig(yaml.load(open('logging.yml', 'r')))

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
            address=config['transmission']['address'],
            port=config['transmission']['port'],
            user=config['transmission']['user'],
            password=config['transmission']['password'])
        log_process.info('connected to transmission ({}:{})'.format(config['transmission']['address'], config['transmission']['port']))
    except TransmissionError as e:
        log_error.error('{} : {}'.format('TransmissionError',e.message))
        tc = False

    for entry in feed.entries:

        torrent_filename = entry.link.split("&")[1]
        log_process.info('processing entry "{}"'.format(torrent_filename))

        matched = False

        for serie_id, regexp_data in regexp.iteritems():
            if regexp_data in entry.title and quality[serie_id] in entry.title:
                matched = True
                break

        if not matched:
            continue

        download_dir = config['torrents-path'] + path[serie_id]

        if torrent_filename in downloaded_torrents:
            log_process.info('{} already in transmission - skipping'.format(torrent_filename))
            continue
        log_process.info('{} matched'.format(torrent_filename))
        request = urllib2.Request(
            entry.link,
            headers={
                "Cookie": config['lostfilm']['cookie'],
                "User-Agent": config['user-agent']
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