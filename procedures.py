import asyncio

from pydantic import BaseModel

from .lock import get_lock, unlock

##################### Build time #######################

class DispenseWell(BaseModel):
    name: str
    address: str
    uuid: str

def demo_procedure(ot, dispenseWell, simulate=False):
    asyncio.set_event_loop(asyncio.new_event_loop())
    ctx = ot.get_protocol_api('2.9')

    #demo procedure
    ctx.home()
    plate = ctx.load_labware("corning_96_wellplate_360ul_flat", 1)
    tip_rack = ctx.load_labware("opentrons_96_filtertiprack_20ul", 2)
    p20 = ctx.load_instrument("p20_single_gen2", "left", tip_racks=tip_rack)

    p20.aspirate(10, plate['A1'])
    p20.dispense(10, dispenseWell.address)

    p20.drop_tip

    #procedures should unlock when finished
    unlock()