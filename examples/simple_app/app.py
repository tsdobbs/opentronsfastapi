from fastapi import FastAPI
from pydantic import BaseModel
import opentronsfastapi as otf

app = FastAPI()
app.include_router(otf.default_routes)
app.include_router(otf.arbitrary_routes)

class DispenseWell(BaseModel):
    address: str

@app.post("/api/procedure/demo_procedure")
@otf.opentrons_execute(apiLevel='2.8')
def demo_procedure(dispenseWell:DispenseWell,
                   version = otf.ot_flags.protocol_version_flag,
                   protocol = otf.ot_flags.protocol_context
                  ):

    plate = protocol.load_labware("corning_96_wellplate_360ul_flat", 1)
    tip_rack = protocol.load_labware("opentrons_96_filtertiprack_20ul", 2)
    p20 = protocol.load_instrument("p20_single_gen2", "left", tip_racks=[tip_rack])

    p20.pick_up_tip()

    p20.aspirate(10, plate.wells_by_name()['A1'])
    p20.dispense(10, plate.wells_by_name()[dispenseWell.address])

    p20.drop_tip()