class Transaction(object):

    def __init__(self, identifier, tick, is_readonly=False):
        self.transaction_id = identifier
        self.is_readonly = is_readonly

        self.operations = []
        self.to_be_aborted = False
        self.tick = tick

    def add_operation(self, operation):
        self.operations.append(operation)

    def __str__(self):
        return "Identifier:" + str(self.transaction_id) + "& ReadOnly:" + str(self.is_readonly) +"& Operations: " +str([str(op) for op in self.operations])

