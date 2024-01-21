import toml
import logging
import requests
import pyndiff
import os
import time
import subprocess
import sys
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

logging.basicConfig(format='%(asctime)s - %(funcName)s - %(message)s', stream = sys.stdout, level=logging.DEBUG)

logging.info("Started...")

NEW_SCAN_FILE = "new.xml"
OLD_SCAN_FILE = "old.xml"

try:
    logging.info("Loading config")
    config = toml.load("config.toml")
    notification_url = config['notification_url']
    if notification_url:
        notify = True
    else:
        notify = False
    scan_opts = config['scan_opts'].split(" ")
    target_list = config['target_list']
    exclusion_list = config['exclusion_list']
    cron = config['cron']
    notify_on_no_change = config['notify_on_no_change']
except:
    logging.warning("config load error")
    exit()

def notifier(msg):
    try:
        logging.info("start")
        if msg == 'No scan diff detected between scans.':
            if notify_on_no_change:
                requests.post(notification_url, json={"msg":msg})
        else:
            requests.post(notification_url, json={"msg":msg})
        logging.info("end")
    except:
        logging.warning("error")
        return False

def cleandiff():
    try:
        logging.info("start")
        diff = pyndiff.generate_diff(OLD_SCAN_FILE, NEW_SCAN_FILE, ignore_udp_open_filtered=True)
        changes = diff.splitlines()[8:]
        logging.info("end")
        return changes
    except:
        logging.warning("error")
        return False

def nmapscan():
    try:
        logging.info("start")
        nmap_args = ["nmap", "-iL", target_list, "--excludefile", exclusion_list, "-oX", NEW_SCAN_FILE] + scan_opts
        subprocess.call(nmap_args)
        logging.info("end")
        return True
    except:
        logging.warning("error")
        return False

def scan():
    logging.info("start")
    if os.path.exists(OLD_SCAN_FILE) == True:
        logging.info("moving old file")
        epoch = int(time.time())
        os.rename(OLD_SCAN_FILE, f"{epoch}.xml")

    newfile = os.path.exists(NEW_SCAN_FILE)
    if  newfile == True:
        logging.info("new scan file found. moving new file")
        os.rename(NEW_SCAN_FILE, OLD_SCAN_FILE)
        if nmapscan():
            changes = cleandiff()
            if changes:
                for msg in changes:
                    if notify:
                        notifier(msg)
    elif newfile == False:
        logging.info("no new file found")
        nmapscan()
    logging.info("end")

logging.info("Starting scheduler")
scheduler = BlockingScheduler()
scheduler.add_job(scan, CronTrigger.from_crontab(cron, 'UTC'))
print(scheduler.print_jobs())
scheduler.start()