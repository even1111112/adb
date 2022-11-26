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
        return f"Identifier: {self.transaction_id} & ReadOnly: {self.is_readonly} & " \
               f"Operations: {[str(op) for op in self.operations]}"

