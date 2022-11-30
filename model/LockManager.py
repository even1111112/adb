class LockManager(object):
    def __init__(self):
        self.lock_table = {}

    def try_lock_variable(self, transaction_id, variable_id, lock_type):
        if lock_type == 0:
          if variable_id not in self.lock_table:
            self.lock_table[variable_id] = {0: {transaction_id}, 1: None}
            return True 
          if self.lock_table[variable_id][1] == transaction_id:
            self.lock_table[variable_id][0].add(transaction_id)
            return True
          if self.lock_table[variable_id][1] is not None:
            return False
          else:
            self.lock_table[variable_id][0].add(transaction_id)
            return True

          
        elif lock_type == 1:
          if variable_id not in self.lock_table:
            self.lock_table[variable_id] = {0: set(), 1: transaction_id}
            return True
          if transaction_id in self.lock_table[variable_id][0] and len(self.lock_table[variable_id][0]) == 1:
                      self.lock_table[variable_id][0].remove(transaction_id)
                      self.lock_table[variable_id][1] = transaction_id
                      return True
          elif transaction_id == self.lock_table[variable_id][1]:
              return True
          else:
              return False


    def try_unlock_variable(self, variable_id, transaction_id):

        unlock = 0

        if transaction_id in self.lock_table[variable_id][0]:
            self.lock_table[variable_id][0].remove(transaction_id)
            unlock += 1

        if transaction_id == self.lock_table[variable_id][1]:
            self.lock_table[variable_id][1] = None
            unlock += 1

        assert unlock == 1

    def release_transaction_locks(self, trans_id):

        delete = []
        for key in self.lock_table.keys():
            if trans_id in self.lock_table[key][0]:
                self.lock_table[key][0].remove(trans_id)

            if self.lock_table[key][1] == trans_id:
                self.lock_table[key][1] = None

            if len(self.lock_table[key][0]) == 0 and self.lock_table[key][1] is None:
                delete.append(key)

        for id in delete:
            self.lock_table.pop(id)

    def clear(self):

        self.lock_table = {}

    def get_involved_transactions(self):
        t = []
        for key in self.lock_table.keys():
            for t_id in self.lock_table[key][0]:
                t.add(t_id)
            if self.lock_table[key][1]:
                t.add(self.lock_table[key][1])
        return set(t)
