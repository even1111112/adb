from prettytable import PrettyTable


class Operation(object):
    def __init__(self, para: [str]):
        self.para = para
        self.op_t = None

    def __str__(self):
        return f"{self.op_t}({','.join(self.para)})"

    def execute(self, tick: int, tm, retry=False):
        pass

    def save_to_transaction(self, tm):
        length = len(self.para)
        if length == 0:
            raise TypeError("Try to append dump operation to transaction")

        if self.para[0] in tm.transactions is False:
            raise KeyError(f"Try to execute {self.op_t} in a non-existing transaction")

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


def print_result(headers, rows):
    prettyTable = PrettyTable()
    prettyTable.field_names = headers
    for i in range(len(rows)):
        prettyTable.add_row(rows[i])
    print(prettyTable)


def do_read(trans_id, var_id, site):
    if (var_id not in site.data_manager.log[trans_id]) or (trans_id not in site.data_manager.log):
        res = site.data_manager.get_variable(var_id)
    else:
        res = site.data_manager.log[trans_id][var_id]
    print_result(["Transaction", "Site", f"x{var_id}"], [[trans_id, f"{site.site_id}", res]])
    return True
