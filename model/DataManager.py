class DataManager(object):

    @staticmethod
    def _init_db(idx):

        data = [None] * 20

        for i in range(20):
            if i % 2 or (i + 1) % 10 + 1 == idx:
                data[i] = 10 * (i + 1)
        return data


    def __init__(self, site_id):
        self.site_id = site_id
        self.data = self._init_db(site_id)

        self.is_accessible = []
        for i in range(len(self.data)):
          if self.data[i]:
            self.is_accessible.append(True)
          else:
            self.is_accessible.append(False)

        self.log = {}

    def clear_uncommitted_changes(self):

        self.log = {}

    def commit(self, transaction_id):

        self.data.update(self.log[transaction_id])
        self.log[transaction_id] = {}

    def disable_accessibility(self):

        for i in range(20):
            if i % 2 == 0 and (i + 1) % 10 + 1 == self.site_id:
                self.is_accessible[i] = True
            else:
                self.is_accessible[i] = False



    def revert_transaction_changes(self, transaction_id):

        self.log.pop(transaction_id, None)

    def get_variable(self, idx):

        return self.data[idx - 1]

    def set_variable(self, idx, val):

        self.data[idx - 1] = val
    
    def check_accessibility(self, idx):

        return self.is_accessible[idx - 1]
