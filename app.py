from fastapi import FastAPI
from pydantic import BaseModel
from bot import opentrons_execute, default_routes
import asyncio
import opentrons.execute as oe
import opentrons.simulate as os

app = FastAPI()
global opentrons_env
opentrons_env = os
app.include_router(default_routes)

##################### Build time #######################

class DispenseWell(BaseModel):
    name: str
    address: str
    uuid: str

@app.post("/api/procedure/demo_procedure")
@opentrons_execute()
def demo_procedure(dispenseWell:DispenseWell):
    asyncio.set_event_loop(asyncio.new_event_loop())
    ctx = opentrons_env.get_protocol_api('2.9')

    ctx.home()
    plate = ctx.load_labware("corning_96_wellplate_360ul_flat", 1)
    tip_rack = ctx.load_labware("opentrons_96_filtertiprack_20ul", 2)
    p20 = ctx.load_instrument("p20_single_gen2", "left", tip_racks=[tip_rack])

    p20.pick_up_tip()

    p20.aspirate(10, plate.wells_by_name()['A1'])
    p20.dispense(10, plate.wells_by_name()[dispenseWell.address])

    p20.drop_tip()

