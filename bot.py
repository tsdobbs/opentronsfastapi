import math
import asyncio
import time
import threading
import sqlite3
import opentrons.execute as oe
import opentrons.simulate as os
from typing import List
from functools import wraps
import inspect

from fastapi import APIRouter
default_routes = APIRouter()

global opentrons_env
opentrons_env = os

# Setup sqlite3 lock
conn = sqlite3.connect("lock.db")
c = conn.cursor()
table_sql = """
BEGIN;
CREATE TABLE IF NOT EXISTS lock (
    lock_id INT PRIMARY KEY,
    lock_active BOOL NOT NULL DEFAULT false,
    locked_by TEXT NOT NULL DEFAULT ''
);
INSERT INTO lock(lock_id) VALUES (1) ON CONFLICT DO NOTHING;
UPDATE lock SET lock_active = false, locked_by='' WHERE lock_id=1;
COMMIT;
"""
c.executescript(table_sql)
conn.close()

# Robotic locks
def lock_state():
    conn = sqlite3.connect("lock.db")
    c_lock = conn.cursor()
    c_lock.execute("SELECT lock_active, locked_by FROM lock WHERE lock_id=1")
    lock_state = c_lock.fetchone()
    d = {"lock_active": lock_state[0], "locked_by": lock_state[1]}
    conn.close()
    return d

def get_lock(locked_by):
    conn = sqlite3.connect("lock.db")
    c_lock = conn.cursor()
    c_lock.execute("SELECT lock_active, locked_by FROM lock WHERE lock_id=1")
    lock_state = c_lock.fetchone()

    if lock_state[0] == False:
        # Acquire the lock
        c_lock.execute("UPDATE lock SET lock_active = true, locked_by=? WHERE lock_id=1", (locked_by,))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False # Fail to acquire the lock

def unlock():
    conn = sqlite3.connect("lock.db")
    c_lock = conn.cursor()
    c_lock.execute("UPDATE lock SET lock_active = false, locked_by='' WHERE lock_id=1")
    conn.commit()
    conn.close()

# https://gist.github.com/amirasaran/e91c7253c03518b8f7b7955df0e954bb
class BaseThread(threading.Thread):
    def __init__(self, callback=None, callback_args=None, *args, **kwargs):
        target = kwargs.pop('target')
        super(BaseThread, self).__init__(target=self.target_with_callback, *args, **kwargs)
        self.callback = callback
        self.method = target
        self.args = args
        self.kwargs = args

    def target_with_callback(self, *args, **kwargs):
        self.method(*args, **kwargs)
        if self.callback is not None:
            self.callback()

#Decorator that executes the function in a seperate thread
def opentrons_execute(msg = "Execution initiated"):
    def outer(func):
        @wraps(func)
        def inner(*args, **kwargs):
            lock = get_lock(func.__name__)
            if lock == False:
                return {"Message": "App currently locked"}

            # Since we have acquired the lock, we can reset global variable opentrons
            global opentrons_env
            ot = opentrons_env
            try:
                opentrons_env = os
                func(*args, **kwargs)
            except Exception as e:
                unlock()
                return {"Message": str(e)}
            opentrons_env = ot
            BaseThread(target=func, callback=unlock, args=args, kwargs=kwargs).start()
            return {"Message": msg}
        return inner
    return outer


### Test funcs ####

@default_routes.get("/")
def read_root():
    return {"Message": "Hello World"}

@default_routes.get("/test/unlock")
def test_unlock():
    unlock()

@default_routes.get("/test/lock")
@opentrons_execute(msg="Lock acquired for 10 seconds. Will be instant if not executing on real machine")
def test_lock_func():
    asyncio.set_event_loop(asyncio.new_event_loop())
    ctx = opentrons_env.get_protocol_api('2.9')
    ctx.delay(10)

@default_routes.get("/test/lock_state")
def test_lock_state_func():
    return lock_state()

@default_routes.get("/test/home")
@opentrons_execute(msg="Lock acquired until home completes")
def test_home_func():
    asyncio.set_event_loop(asyncio.new_event_loop())
    ctx = opentrons_env.get_protocol_api('2.9')
    ctx.home()

