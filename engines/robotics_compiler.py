"""Cloud Wet-Lab Robotics & Protocol Compiler for AION X.
Compiles high-level experimental methodologies into executable Opentrons OT-2 Python scripts
and industry-standard Autoprotocol JSON for autonomous wet-lab execution.
"""
import json
from typing import Dict, Any, List


class RoboticsProtocolCompiler:
    """Translates hypothesis validation protocols into automated liquid-handling robotics instructions."""

    def generate_opentrons_protocol(
        self,
        experiment_name: str,
        pipette_type: str = "p300_single_gen2",
        plate_type: str = "corning_96_wellplate_360ul_flat",
        tiprack_type: str = "opentrons_96_tiprack_300ul",
        sample_count: int = 8,
        transfer_volume_ul: float = 50.0
    ) -> str:
        """Generates fully compliant Opentrons Python Protocol API v2 code."""
        code = f'''from opentrons import protocol_api

metadata = {{
    "protocolName": "AION X Autonomous Protocol — {experiment_name}",
    "author": "AION X Autonomous Omni-Scientist",
    "description": "Automated experimental protocol compiled by AION X Discovery Swarm",
    "apiLevel": "2.13"
}}

def run(protocol: protocol_api.ProtocolContext):
    # 1. Load Labware onto Robot Deck
    tiprack = protocol.load_labware("{tiprack_type}", location="1")
    source_plate = protocol.load_labware("{plate_type}", location="2", label="Source Reagents")
    target_plate = protocol.load_labware("{plate_type}", location="3", label="Reaction Plate")

    # 2. Load Pipette Instrument
    pipette = protocol.load_instrument("{pipette_type}", mount="right", tip_racks=[tiprack])

    protocol.comment("=== Initiating AION X Autonomous Liquid Transfer Protocol ===")

    # 3. Execute Aspirate & Dispense Transfer Loop
    for i in range({sample_count}):
        src_well = source_plate.wells()[i]
        tgt_well = target_plate.wells()[i]

        protocol.comment(f"Transferring {transfer_volume_ul}uL from {{src_well}} to {{tgt_well}}")
        pipette.pick_up_tip()
        pipette.aspirate({transfer_volume_ul}, src_well.bottom(1.0))
        pipette.dispense({transfer_volume_ul}, tgt_well.bottom(2.0))
        pipette.mix(3, {transfer_volume_ul * 0.7:.1f}, tgt_well)
        pipette.drop_tip()

    protocol.comment("=== AION X Protocol Completed Successfully ===")
'''
        return code

    def generate_autoprotocol_json(
        self,
        experiment_name: str,
        sample_count: int = 8,
        transfer_volume_ul: float = 50.0
    ) -> Dict[str, Any]:
        """Generates standard Autoprotocol JSON structure for Cloud Lab execution."""
        instructions = []
        for i in range(sample_count):
            instructions.append({
                "op": "pipette",
                "groups": [
                    {
                        "transfer": [
                            {
                                "shape": {"rows": 1, "columns": 1},
                                "from": f"source_plate/well_{i}",
                                "to": f"reaction_plate/well_{i}",
                                "volume": f"{transfer_volume_ul}:microliter",
                                "mix_after": {
                                    "volume": f"{transfer_volume_ul * 0.6}:microliter",
                                    "repetitions": 3
                                }
                            }
                        ]
                    }
                ]
            })

        return {
            "name": f"AION_X_{experiment_name.replace(' ', '_')}",
            "schema": "autoprotocol-v1.0",
            "containers": {
                "source_plate": {"type": "96-flat", "discard": True},
                "reaction_plate": {"type": "96-flat", "discard": False}
            },
            "instructions": instructions
        }
