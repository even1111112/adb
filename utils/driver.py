from model.Site import Site
from model.managers.TransactionManager import TransactionManager
from model.Operation import OperationParser, OperationCreator

def run(case):
    tm = TransactionManager()
    sites = []
    for i in range(1, 10 + 1):
      sites.append(Site(i))
    tm.attach_sites(sites)
    length = len(case)
    tick = length + 1
    for i in range(length):
        operation = OperationCreator.create(OperationParser.parse(case[i])[0], OperationParser.parse(case[i])[1])
        tm.step(operation, i + 1)
    block_size = len(tm.blocked)
    while tm.blocked:       
        tick += 1
        tm.retry(tick)
        if len(tm.blocked) == block_size:
            print("error: not terminable")
            break
        else:
            block_size = len(tm.blocked)
