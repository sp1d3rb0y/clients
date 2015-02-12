## slack-history-retriever.py for Slack History Retriever in ~/slack-history
##
## Made by spiderboy
##
## Started on  Sun Feb  8 18:07:32 2015 spiderboy
## Last update Thu Feb 12 23:33:13 2015 spiderboy
##
#!/usr/bin/env python

import requests
import sys
import json
import time
import re
import io

# Full Unix Path to log folder
log_path = "~/slack-history/"
# Find your token @ https://api.slack.com/web
token = ""
# Your Slack URL
url = "https://lescoupains.slack.com/api/"

def get_method_result(method, args = ""):
    r = requests.get("%s%s?token=%s&%s" % (url, method, token, args))
    res = json.loads(r.text)
    return res

def get_channels():
    chans = {}
    res = get_method_result("channels.list")
    for chan in res['channels']:
        chans[chan['id']] = chan['name']
    return chans

def get_users():
    users = {}
    res = get_method_result("users.list")
    for user in res['members']:
        users[user["id"]] = user['name']
        users[user['name']] = user['id']
    return users

def replace_chans_and_users(line, users, chans):
    users_to_replace = re.findall('<@?(U[A-Z0-9]{8})>', line)
    for u in users_to_replace:
        if u in users:
            line = re.sub(u,users[u],line)
    chans_to_replace = re.findall('<#?(C[A-Z0-9]{8})>', line)
    for c in chans_to_replace:
        if c in chans:
            line = re.sub(c, chans[c], line)
    return line

def get_latest(channel):
    try:
        f = open('%s/.%s.latest' % (log_path, channel),'r')
        res = f.readlines()
        f.close()
        return res[0].replace("\n",'')
    except Exception,e:
        return None

def set_latest(channel, latest):
    f = open("%s/.%s.latest" % (log_path, channel), "w")
    f.write(latest)
    f.close()

def write_log(channel, lines):
    f = io.open("%s/%s.log" % (log_path, channel), "a", encoding='utf8')
    for l in lines:
        f.write(l + '\n')
    f.close()

def get_channel_history(id_channel, channel_name, verbose):
    args = "count=1000&channel=%s" % id_channel
    latest = get_latest(channel_name)
    if latest is not None:
        args += "&oldest=%s" % latest
    res = get_method_result("channels.history", args)
    if verbose:
        sys.stdout.write('.')
        sys.stdout.flush()
    if 'has_more' in res:
        hasmore = res['has_more']
        while hasmore:
            args = "count=1000&channel=%s" % id_channel
            args += "&latest=%s" % res['messages'][0]['ts']
            newres = get_method_result("channels.history", args)
            res['messages'] = newres['messages'] + res['messages']
            hasmore = newres['has_more']
            if verbose:
                sys.stdout.write('.')
                sys.stdout.flush()
    formatted = []
    if 'messages' in res and res['messages']:
        set_latest(channel_name, res['messages'][0]['ts'])
        for message in reversed(res['messages']):
            ts = time.strftime('%d/%m/%Y %H:%M:%S',  time.gmtime(int(message['ts'].split('.')[0])))
            if 'user' in message:
                formatted.append("[%s] <%s> %s" % (ts, message['user'], message['text']))
            else:
                formatted.append("[%s] %s" % (ts, message['text']))
        if verbose:
            print
        return formatted
    else:
        if verbose:
            print
        return ""

if __name__ == '__main__':
    channels = get_channels()
    users = get_users()

    verbose = (len(sys.argv) == 2) and (sys.argv[1] == '-v')

    for chan in channels:
        if verbose:
            print "[+] Retrieving history for channel %s" % (channels[chan]),
            sys.stdout.flush()
        lines = get_channel_history(chan, channels[chan], verbose)
        logs = []
        if verbose:
            print "[+] Writing logs for %s (%i lines)" % (channels[chan], len(lines))
        for l in lines:
            logs.append(replace_chans_and_users(l, users, channels))
        write_log(channels[chan], logs)
