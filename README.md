# Example

```python3
from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
import opentrons.execute as oe
import opentrons.simulate as os
import opentronsfastapi

# Set our opentrons_env to opentrons.simulate
# On real robots, this would be set to opentrons.execute
opentronsfastapi.opentrons_env = os

app = FastAPI()

class DispenseWell(BaseModel):
    address: str

@app.post("/api/procedure/demo_procedure")
@opentronsfastapi.opentrons_execute()
def demo_procedure(dispenseWell:DispenseWell):

    # Asyncio must be set to allow the robot to run protocols in
    # the background while still responding to API requests
    asyncio.set_event_loop(asyncio.new_event_loop())
    ctx = opentronsfastapi.opentrons_env.get_protocol_api('2.9')

    ctx.home()
    plate = ctx.load_labware("corning_96_wellplate_360ul_flat", 1)
    tip_rack = ctx.load_labware("opentrons_96_filtertiprack_20ul", 2)
    p20 = ctx.load_instrument("p20_single_gen2", "left", tip_racks=[tip_rack])

    p20.pick_up_tip()

    p20.aspirate(10, plate.wells_by_name()['A1'])
    p20.dispense(10, plate.wells_by_name()[dispenseWell.address])

    p20.drop_tip()
```

# opentronsfastapi

opentronsfastapi is a library that allows for FastAPIs to be easily deployed onto Opentrons liquid handling robots (OT2) with robotic protocols. The protocols can be parameterized, allowing complex robotic functions to take place. Communication is done over HTTP via a REST API, and execution of the protocols begins immediately, allowing the OT2 to work as part of a larger lab management system, or simply allowing the user to build a user interface that suits their needs better than the stock options Opentrons provides.

For example, a biofoundry might have the following components for successfully executing a protocol:
1. A job queue that lists the tasks to be done
2. A system-level execution manager that decides what job to do next and passes the job to an appropriate robot
3. A client on the robot that receives job requests and, if accepted, initiates execution on the robot
4. A low-level layer that converts job instructions to the acutation of motors

opentronsfastapi specifically helps with #3.

## Features
opentronsfastapi:
- (done) Allows API endpoints to be wrapped with a decorator for execution on an Opentrons robot
- (done) Manages robot state - if the robot is busy, then job requests are refused until the robot work is complete, and an error code is returned to the requestor
- (done) Can report the state of the robot to a requestor, via API endpoint
- (todo) Can report the protocol version the robot will use, in the form of a unique hash, via an API endpoint
- (done) Allows the API to be accessed by any arbitrary tool, as long as POST requests are sent in the right format
- (todo) Can be deployed on stock OT2's without special tools

## Limitations
- Works at the level of a single robot, and is naive of other robots. However, it can be deployed on multiple robots, which can then be managed by a supervisor.

## Todo
- Better and clearer exception handling of errors
- Automatic recongition of being deployed on a robot (users shouldn't have to set the `opentrons_env` global variable)
- Simple git deployment onto robots
- Hash returns of any individual protocol

# Contributors
- Thank you Tim Dobbs for writing most of the README, adding essential wrappers, and generally bringing this project into reality.
