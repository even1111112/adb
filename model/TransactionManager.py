from algorithms.DeadLockDetector import *

class TransactionManager(object):

    def __init__(self):
        self.transactions = {}
        self.wait_for_graph = WaitFor(self)
        self.blocked = []
        self.blocked_transactions = set()
        self.sites = []

    def retry(self, tick):
        operations = []
        trans = []
        for operation in self.blocked:
            if not operation.execute(tick, self, True):
                operations.append(operation)

                if operation.get_op_t() != "end" or operation.get_parameters()[0] not in tx_b:
                  trans.append(operation.get_parameters()[0])

        self.blocked = operations
        self.blocked_transactions = set(trans)

    def _distribute_operation(self, operation, tick):
        if not operation.execute(tick, self):
            self.blocked.append(operation)

    def step(self, operation, tick):

        self.retry(tick)
        self._distribute_operation(operation, tick)

        if operation.get_op_t() == "R" or operation.get_op_t() == "W":
          if self.wait_for_graph.check_deadlock():
            self.abort(self.get_youngest_transaction(self.wait_for_graph.get_trace())[0], 2)

    def attach_sites(self, sites):
        self.sites = sites

    def get_site(self, idx):
        return self.sites[idx - 1]

    def get_youngest_transaction(self, trace):
        val = - self.transactions[trace[0]].tick 
        ans = trace[0]
        for i in range(len(trace)):
          if - self.transactions[trace[i]].tick < val:
            ans = trace[i]
            val = - self.transactions[trace[i]].tick
        return ans, - val

    def abort(self, transaction_id, abort_type):

        for i in range(len(self.sites)):
            if self.sites[i].up:
                self.sites[i].lock_manager.release_transaction_locks(transaction_id)
                self.sites[i].data_manager.revert_transaction_changes(transaction_id)
        updated_blocked = []
        for i in range(len(self.blocked)):
          if self.blocked[i].get_parameters()[0] != transaction_id:
              updated_blocked.append(self.blocked[i])
        self.blocked = updated_blocked

        self.wait_for_graph.remove_transaction(transaction_id)

        self.transactions.pop(transaction_id)
        print("Transaction", transaction_id, "aborted")


