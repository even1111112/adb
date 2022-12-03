from tabulate import tabulate
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
        for_snap = {}
        for number, d in enumerate(self.data_manager.data, start=1):
            if self.data_manager.is_accessible[number - 1] == True and d:
                for_snap[number] = d
        self.snapshots[tick] = deepcopy(for_snap)

    def get_snapshot_variable(self, tick, var_id):
        return self.snapshots[tick][var_id]
        
class Operation(object):
    def __init__(self, para: [str]):
        self.para = para
        self.op_t = None

    def __str__(self):
        return str(self.op_t)+','.join(self.para)

    def execute(self, tick: int, tm, retry=False):
        pass

    def save_to_transaction(self, tm):
        length = len(self.para)
        if length == 0:
            raise TypeError("Cannot perform dump operation after transaction.")

        if self.para[0] in tm.transactions is False:
            raise KeyError("Cannot execute ",str(self.op_t), " when transaction doesn't exist.")

        tm.transactions[self.para[0]].add_operation(self)
        tm.wait_for_graph.add_operation(self)

    def get_parameters(self):
        return self.para

    def get_op_t(self):
        return self.op_t


def do_read(trans_id, var_id, site):
    if (trans_id not in site.data_manager.log) or (var_id not in site.data_manager.log[trans_id]):
        ans = site.data_manager.get_variable(var_id)
    else:
        ans = site.data_manager.log[trans_id][var_id]
    print(tabulate(["Transaction", "Site", "x"+str(var_id)], [[trans_id, str(site.site_id), ans]]))
    return True
