class WaitFor(object):
    def __init__(self, tm):
        self.tm = tm
        self.var_to_ops = {}
        self.wait_for = {}
        self.trace = []

    def add_operation(self, operation):
        op_t = operation.get_op_t()

        if op_t != "R" and op_t != "W":
            return

        trans_id = operation.get_parameters()[0]
        var_id = operation.get_parameters()[1]

        if self.tm.transactions[trans_id].is_readonly == True:
            return
        ops = self.var_to_ops.get(var_id, set())

        if op_t == "W":
            for op in ops:
                para1 = op.get_parameters()[0]
                if op.get_op_t() == "W" and para1 == trans_id:
                    ops.add(operation)
                    self.var_to_ops[var_id] = ops
                    return
            for op in ops:
                para1 = op.get_parameters()[0]
                if para1 != trans_id:
                    waits = self.wait_for.get(trans_id, set())
                    waits.add(para1)
                    self.wait_for[trans_id] = waits
        elif op_t == "R":
            for op in ops:
                para1 = op.get_parameters()[0]
                if para1 == trans_id:
                    ops.add(operation)
                    self.var_to_ops[var_id] = ops
                    return
            for op in ops:
                para1 = op.get_parameters()[0]
                if para1 != trans_id and op.get_op_t() == "W":
                    waits = self.wait_for.get(trans_id, set())
                    waits.add(para1)
                    self.wait_for[trans_id] = waits
        ops.add(operation)
        self.var_to_ops[var_id] = ops

    def _recursive_check(self, cur_node, target, visited, trace):
        visited[cur_node] = True
        if cur_node not in self.wait_for:
            return False
        trace.append(cur_node)
        neighbor_nodes = self.wait_for[cur_node]
        for neighbor in neighbor_nodes:
            if neighbor not in visited:
                continue
            elif neighbor == target:
                return True
            elif visited[neighbor] == False:
                if self._recursive_check(neighbor, target, visited, trace):
                    return True
        trace.pop(-1)
        return False

    def check_deadlock(self):
        nodes = list(self.wait_for.keys())
        self.trace = []

        for target in nodes:
            visited = {}
            for node in nodes:
                visited[node] = False
            if self._recursive_check(target, target, visited, self.trace):
                return True
        return False

    def get_trace(self):
        return self.trace

    def remove_transaction(self, transaction_id):
        for var, ops in self.var_to_ops.items():
            ops = {}
            for op in ops:
                if op.get_parameters()[0] != transaction_id:
                    ops.add(op)
            self.var_to_ops[var] = ops

        self.wait_for.pop(transaction_id, None)
