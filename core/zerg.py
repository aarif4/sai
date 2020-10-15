import sc2

class Zerg(sc2.BotAI):
    @staticmethod
    def get_race():
        return sc2.Race.Zerg
    
    async def on_step(self, iteration: int):
        await self.distribute_workers()
        await self.increase_supply_cap()
        await self.build_worker_units()


    async def build_worker_units(self):
        townhall_unitid = sc2.constants.HATCHERY
        worker_unitid   = sc2.constants.DRONE
        
        for townhall in self.structures(townhall_unitid):
            for target_larva in self.larva.closest_n_units(townhall.position, 1):
                if self.can_afford(worker_unitid):
                    target_larva.train(worker_unitid)


    async def increase_supply_cap(self):
        MIN_SUPPLY_THRESH = 5
        townhall_unitid = sc2.constants.HATCHERY
        supply_unitid = sc2.constants.OVERLORD
        
        if self.supply_left < MIN_SUPPLY_THRESH and not self.already_pending(supply_unitid):
            for townhall in self.structures(townhall_unitid).ready:
                for target_larva in self.larva.closest_n_units(townhall.position, 1):
                    if self.can_afford(supply_unitid):
                        target_larva.train(supply_unitid)