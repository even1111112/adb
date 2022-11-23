from model.DataManager import DataManager
from model.LockManager import LockManager
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
        prefix = f"Site {self.site_id} ({'up' if self.up else 'down'})"
        return [prefix] + [v for v in self.data_manager.data]

    def recover(self):
        self.up = True

    def snapshot(self, tick):
        available_data = {}
        for idx, d in enumerate(self.data_manager.data):
            if d and self.data_manager.is_accessible[idx]:
                available_data[idx + 1] = d
        self.snapshots[tick] = deepcopy(available_data)

    def get_snapshot_variable(self, tick, var_id):
        return self.snapshots[tick][var_id]