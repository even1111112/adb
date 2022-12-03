from tabulate import tabulate

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


def parse_variable_id(variable_id):
    for num, c in enumerate(variable_id, start=1):
        if c.isdigit() == True:
            return variable_id[:(num - 1)], int(variable_id[(num - 1):])


def do_read(trans_id, var_id, site):
    if (trans_id not in site.data_manager.log) or (var_id not in site.data_manager.log[trans_id]):
        ans = site.data_manager.get_variable(var_id)
    else:
        ans = site.data_manager.log[trans_id][var_id]
    print(tabulate(["Transaction", "Site", "x"+str(var_id)], [[trans_id, str(site.site_id), ans]]))
    return True
