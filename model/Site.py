from model.managers.DataManager import DataManager
from model.managers.LockManager import LockManager
from copy import deepcopy

class Site(object):
    def __init__(self, id):
        self.site_id = id
        self.data_manager = DataManager(id)
        self.lock_manager = LockManager()
        self.up = True
        self.snapshots = {}

    def fail(self):
        self.up = False
        self.data_manager.clear_uncommitted_changes()
        self.lock_manager.clear()
        self.data_manager.disable_accessibility()

    def echo(self):
        if self.up == True:
            prefix = "site" + str(self.site_id) + "up"
        else:
            prefix = "site" + str(self.site_id) + "down"
        a = [prefix]
        for v in self.data_manager.data:
            a = a + [v]
        return a

    def recover(self):
        self.up = True

    def snapshot(self, tick):
        available_data = {}
        for number, d in enumerate(self.data_manager.data, start=1):
            if self.data_manager.is_accessible[number - 1] == True and d:
                available_data[number] = d
        self.snapshots[tick] = deepcopy(available_data)

    def get_snapshot_variable(self, tick, var_id):
        return self.snapshots[tick][var_id]
