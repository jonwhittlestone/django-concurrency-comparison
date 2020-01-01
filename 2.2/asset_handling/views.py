import os
import threading
import time

from django.shortcuts import render
from django.conf import settings
from random import random

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler, FileSystemEventHandler

result = None
result_available = threading.Event()


def background_calculation_event1():
    # here goes some long calculation
    wait_duration = random() * 5 * 60
    print(f'Waiting for {wait_duration}')
    time.sleep(wait_duration)

    # when the calculation is done, the result is stored in a global variable
    global result
    result = 42
    result_available.set()
    # do some more work before existing the thread
    time.sleep(10)


def wait_event1():
    thread = threading.Thread(target=background_calculation_event1)
    thread.start()

    # wait here for the result to be avaiable before continuing
    result_available.wait()

    print('The result is', result)

# ----  background progress thread example ---- 

progress = 0
exit_thread = threading.Event()
def background_thread_progress():
    '''
        Replaced a fixed-time sleep with a wait on an event object
        If some other part of program calls exit_thread.set(), when
        program is in a thread and reaches exit__thread.wait(), it'll will
        return True, and exit
    '''
    # Simple implemntation below without progress
    # while True:
    #     if exit_thread.wait(timeout=10):
    #         break

    global progress 
    for i in range(100):
        time.sleep(random() * 3)
        progress = i + 1

    # when calc is done, store result in global
    global result
    result = 42
    result_available.set()


def wait_progress():
    thread = threading.Thread(target=background_thread_progress)
    thread.start()
    # wait here for result to be available before continuing
    while not result_available.wait(timeout=5):
        print(f'\r{progress}% done ...', end='', flush=True)
    print(f'\r{progress}% done ...', end='')
    print('The result is', result)

class MyEventHandler(FileSystemEventHandler):
    def __init__(self, observer):
        self.observer = observer

    def on_created(self, event):
        if not event.src_path.endswith('.txt'):
            global asset_count
            asset_count = 3


# ----  watchdog example - tinyurl.com/t4y92gp ---- 
def main_wd():
    # resource: getting an observer to stop after a download
    # https://stackoverflow.com/questions/27815408/trouble-getting-watchdog-observer-to-stop-join-python

    # config
    global asset_count, asset_limit
    asset_count = 0
    asset_limit = 3

    patterns = "*"
    ignore_patterns = ""
    ignore_directories = False
    case_sensitive = True
    path = settings.MEDIA_ROOT
    # create handler and register
    # handler = PatternMatchingEventHandler()
    # handler.on_deleted = on_deleted
    # handler.on_modified = on_modified
    # handler.on_moved = on_moved

    # once event handlers are created, we need an observer to
    # actually do the monitoring
    # go_recursively = False
    observer = Observer()
    handler = MyEventHandler(observer)
    handler.on_created = on_created
    observer.schedule(handler, path, recursive=False)

    # start the observer
    observer.start()
    try:
        while asset_count <= 3:
            time.sleep(1)
        print('File count reached. Now to make the zip and return')
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def path_name(full_path):
    filename = os.path.basename(full_path)
    return full_path.replace(filename, '')

def on_created(event):
    basepath = path_name(event.src_path)
    global asset_count
    asset_count = len([name for name in os.listdir(basepath)
                 if os.path.isfile(os.path.join(basepath, name))])
    print(f"Cool! {event.src_path} has been created! ")
    print(f"Now, {basepath} contains {asset_count} files")

def on_deleted(event):
    print(f"what the f**k! Someone deleted {event.src_path}!")

def on_modified(event):
    print(f"hey buddy, {event.src_path} has been modified")

def on_moved(event):
    print(f"ok ok ok, someone moved {event.src_path} to {event.dest_path}")




