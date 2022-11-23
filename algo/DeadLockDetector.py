class WaitFor(object):
    def __init__(self, tm):
        self.tm = tm
        self.var_to_ops = {}
        self.wait_for = {}
        self.trace = []

    def add_operation(self, operation):
        op_t = operation.get_op_t()
        para = operation.get_parameters()

        if not (op_t == "R" or op_t == "W"):
            return

        trans_id = para[0]
        var_id = para[1]

        if self.tm.transactions[trans_id].is_readonly:
            return
        ops = self.var_to_ops.get(var_id, set())

        # Case 1: operation is W
        if op_t == "W":
            for op in ops:
                if op.get_parameters()[0] == trans_id and op.get_op_t() == "W":
                    ops.add(operation)
                    self.var_to_ops[var_id] = ops
                    return

            for op in ops:
                if op.get_parameters()[0] != trans_id:
                    waits = self.wait_for.get(trans_id, set())
                    waits.add(op.get_parameters()[0])
                    self.wait_for[trans_id] = waits
        # Case 2: operation is W
        else:
            for op in ops:
                if op.get_parameters()[0] == trans_id:
                    ops.add(operation)
                    self.var_to_ops[var_id] = ops
                    return

            for op in ops:
                if op.get_op_t() == "W" and op.get_parameters()[0] != trans_id:
                    waits = self.wait_for.get(trans_id, set())
                    waits.add(op.get_parameters()[0])
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
            if neighbor == target:
                return True
            elif neighbor not in visited:
                continue
            elif not visited[neighbor]:
                if self._recursive_check(neighbor, target, visited, trace):
                    return True
        trace.pop(-1)
        return False

    def check_deadlock(self):
        nodes = list(self.wait_for.keys())
        self.trace = []

        for target in nodes:
            visited = {node: False for node in nodes}
            if self._recursive_check(target, target, visited, self.trace):
                return True
        return False

    def get_trace(self):
        return self.trace

    def remove_transaction(self, transaction_id):
        for var, ops in self.var_to_ops.items():
            ops = {op for op in ops if op.get_parameters()[0] != transaction_id}
            self.var_to_ops[var] = ops

        self.wait_for.pop(transaction_id, None)