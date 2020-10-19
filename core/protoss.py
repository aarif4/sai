import sc2
import random


class Protoss(sc2.BotAI):
    @staticmethod
    def get_race():
        return sc2.Race.Protoss
    

    async def on_step(self, iteration: int):
        await self.distribute_workers()
        await self.increase_supply_cap()
        await self.build_worker_units()
        await self.build_vespene_gas_structure()
        await self.build_townhall_structure()
        await self.build_combat_structures()
        await self.train_combat_units()
        await self.attack_enemy()
        

    async def build_worker_units(self):
        townhall_unitid = sc2.constants.NEXUS
        worker_unitid   = sc2.constants.PROBE
        
        for townhall in self.structures(townhall_unitid):
            if townhall.is_ready and townhall.is_idle:
                if self.can_afford(worker_unitid):
                    townhall.train(worker_unitid)


    async def increase_supply_cap(self):
        MIN_SUPPLY_THRESH = 5
        townhall_unitid = sc2.constants.NEXUS
        supply_unitid = sc2.constants.PYLON
        
        if self.supply_left < MIN_SUPPLY_THRESH and not self.already_pending(supply_unitid):
            for townhall in self.structures(townhall_unitid).ready:
                if self.can_afford(supply_unitid):
                    await self.build(supply_unitid, near=townhall)


    async def build_vespene_gas_structure(self):
        townhall_unitid = sc2.constants.NEXUS
        vgs_unitid = sc2.constants.ASSIMILATOR
        min_dist = 15.0
        
        for townhall in self.structures(townhall_unitid).ready:
            vg_geysers = self.vespene_geyser.closer_than(min_dist, townhall)
            for vg_geyser in vg_geysers:
                if not self.can_afford(vgs_unitid):
                    break
                
                worker = self.select_build_worker(vg_geyser.position)
                if worker is None:
                    break
                
                if not self.structures(vgs_unitid).closer_than(1, vg_geyser).exists and not self.already_pending(vgs_unitid):
                    worker.build(vgs_unitid, vg_geyser)


    async def build_townhall_structure(self):
        MAX_NO_TOWNHALLS = 3
        townhall_unitid = sc2.constants.NEXUS
        
        if self.structures(townhall_unitid).amount < MAX_NO_TOWNHALLS and self.can_afford(townhall_unitid) and not self.already_pending(townhall_unitid):
            await self.expand_now()


    async def build_combat_structures(self):
        supply_unitid = sc2.constants.PYLON
        combat_bldg_unitid = sc2.constants.GATEWAY
        combat_bldg_addon_unitid = sc2.constants.CYBERNETICSCORE

        if self.structures(supply_unitid).ready.exists:
            target_supply = self.structures(supply_unitid).ready.random
            if self.structures(combat_bldg_unitid).ready.exists and not self.structures(combat_bldg_addon_unitid):
                if self.can_afford(combat_bldg_addon_unitid) and not self.already_pending(combat_bldg_addon_unitid):
                    await self.build(combat_bldg_addon_unitid, near=target_supply)
            elif len(self.structures(combat_bldg_unitid)) < 3:
                if self.can_afford(combat_bldg_unitid) and not self.already_pending(combat_bldg_unitid):
                    await self.build(combat_bldg_unitid, near=target_supply)


    async def train_combat_units(self):
        combat_bldg_unitid = sc2.constants.GATEWAY
        combat_bldg_addon_unitid = sc2.constants.CYBERNETICSCORE
        basic_combat_unit = sc2.constants.STALKER
        
        for gw in self.structures(combat_bldg_unitid).ready:
            if gw.is_idle:
                if self.can_afford(basic_combat_unit) and self.supply_left > 0:
                    gw.train(basic_combat_unit)


    def find_target(self, state):
        if len(self.enemy_units) > 0:
            return random.choice(self.enemy_units)
        elif len(self.enemy_structures) > 0:
            return random.choice(self.enemy_structures)
        else:
            return self.enemy_start_locations[0] # since always 1
        
    async def attack_enemy(self):
        basic_combat_unit = sc2.constants.STALKER

        if self.units(basic_combat_unit).amount > 15:
            for s in self.units(basic_combat_unit).idle:
                s.attack(self.find_target(self.state))

        elif self.units(basic_combat_unit).amount > 3:
            if len(self.enemy_units) > 0:
                for s in self.units(basic_combat_unit).idle:
                    s.attack(random.choice(self.enemy_units))