from fastapi import FastAPI
from pydantic import BaseModel
import opentronsfastapi

app = FastAPI()
app.include_router(opentronsfastapi.default_routes)

class DispenseWell(BaseModel):
    address: str

@app.post("/api/procedure/demo_procedure")
@opentronsfastapi.opentrons_execute(apiLevel='2.8', version_flag='version')
def demo_procedure(dispenseWell:DispenseWell, version:bool = False, protocol = opentronsfastapi.protocol_ctx_hold()):

    plate = protocol.load_labware("corning_96_wellplate_360ul_flat", 1)
    tip_rack = protocol.load_labware("opentrons_96_filtertiprack_20ul", 2)
    p20 = protocol.load_instrument("p20_single_gen2", "left", tip_racks=[tip_rack])

    p20.pick_up_tip()

    p20.aspirate(10, plate.wells_by_name()['A1'])
    p20.dispense(10, plate.wells_by_name()[dispenseWell.address])

    p20.drop_tip()