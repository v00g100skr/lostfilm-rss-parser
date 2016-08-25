# coding: utf=8
__author__ = 'crow'

import feedparser
import urllib2
import transmissionrpc
import base64
import os
import logging.config
import yaml
import smtplib

from transmissionrpc import TransmissionError
from email.mime.text import MIMEText


def main():

    try:
        config = yaml.load(open('local.yml', 'r'))
    except:
        config = yaml.load(open('config.yml', 'r'))

    path = {}
    regexp = {}
    quality = {}

    for quality_id, series in config['series'].iteritems():
        for serie in series:
            if isinstance(serie, dict):
                for serie_name, serie_data in serie.iteritems():
                    path[serie_name] = serie_data.get('path', serie_name)
                    regexp[serie_name] = serie_data.get(
                        'alternate_name',
                        serie_name)
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
    email_torrents = []

    file = open("download.log", 'r')
    row = file.readlines()
    for line in row:
        items = line.split(" ")
        downloaded_torrents.append(items[1].replace("\n", ''))
    file.close()

    tc = False

    if config['use_transmission'] is True:
        try:
            tc = transmissionrpc.Client(
                address=config['transmission']['address'],
                port=config['transmission']['port'],
                user=config['transmission']['user'],
                password=config['transmission']['password'])
            log_process.info(
                'connected to transmission ({}:{})'.format(
                    config['transmission']['address'],
                    config['transmission']['port']))
        except TransmissionError as e:
            log_error.error('{} : {}'.format('TransmissionError', e.message))

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

        download_dir = config['downloads-path'] + path[serie_id]
        torrent_dir = config['torrents-path']

        if torrent_filename in downloaded_torrents:
            log_process.info(
                '{} already processed - skipping'.format(torrent_filename))
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
            processed = False
            if config['store_torrent_files'] is True and not os.path.isfile(
                    torrent_dir + torrent_filename):
                output = open(torrent_dir + torrent_filename, 'wb')
                output.write(buffer)
                output.close()
                log_process.info(
                    '{} stored to "{}"'.format(
                        torrent_filename,
                        torrent_dir))
                processed = True
            if tc:
                if not os.path.exists(download_dir):
                    os.makedirs(download_dir)
                    log_process.info('creating dir "{}"'.format(download_dir))
                tc.add_torrent(
                    base64.b64encode(buffer),
                    download_dir=download_dir)
                log_process.info(
                    '{} added to transmission'.format(torrent_filename))
                email_torrents.append(entry.title)
                processed = True
            else:
                log_error.error('no connection  to transmission - skipping')

            if processed:
                log_download.info(torrent_filename)

        else:
            log_process.warning('{} has zero size'.format(torrent_filename))

    if len(email_torrents) > 0 and config['send_email'] is True:
        status = send_email(config, email_torrents)
        if status:
            log_process.info(
                'email sended to {}'.format(
                    config['email']['to']))
        else:
            log_error.error('email sending failed')


def send_email(config, torrents_list):

    mail_user = config['email']['smtp_username']
    mail_pwd = config['email']['smtp_password']
    text = '\n'.join(torrents_list)

    msg = MIMEText(text, "plain", "utf-8")
    msg['Subject'] = config['email']['subject']
    msg['From'] = config['email']['from']
    msg['To'] = config['email']['to']

    try:
        server = smtplib.SMTP(
            config['email']['smtp_host'],
            config['email']['smtp_port'])
        server.ehlo()
        server.starttls()
        server.login(mail_user, mail_pwd)
        server.sendmail(
            config['email']['from'],
            config['email']['to'],
            msg.as_string())
        server.close()
        return True
    except Exception:
        return False

if __name__ == "__main__":
    main()
