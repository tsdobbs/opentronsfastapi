from fastapi import FastAPI
import math
import asyncio
import time
import threading
import opentrons.execute as oe
import opentrons.simulate as os
from typing import List

from lock import get_lock, unlock, threaded_execute
import procedures

# Config
opentrons = oe

app = FastAPI()

### Test funcs ####

@app.get("/")
def read_root():
    return {"Message": "Hello World"}

@app.get("/test/unlock")
def test_unlock():
    unlock()

@app.get("/test/lock")
@threaded_execute("Test Lock", msg="Lock acquired for 10 seconds")
def test_lock_func():
    time.sleep(10)
    unlock()
    return {"Message": "Unlocked"}

@app.get("/test/home")
@threaded_execute("Test homing", msg="Lock acquired until home completes")
def test_home_func():
    asyncio.set_event_loop(asyncio.new_event_loop())
    ctx = opentrons.get_protocol_api('2.9')
    ctx.home()
    unlock()

### Demo procedure ####

@app.post("/api/procedure")
@threaded_execute("Demo Procedure", msg= "Lock acquired until procedure completes", simulate=True)
def procedure(procedure_name, **kwargs):
    getattr(procedures, procedure_name)(**kwargs)