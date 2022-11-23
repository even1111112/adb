from configurations import *
from model.Site import Site
from model.managers.TransactionManager import TransactionManager
from model.Operation import OperationParser, OperationCreator


def init_sites():

    sites = []
    for i in range(1, number_of_sites + 1):
      sites.append(Site(i))
    return sites


def run(case):
    tm = TransactionManager()
    tm.attach_sites(init_sites())


    for i in range(len(case)):
        op, para = OperationParser.parse(case[i])
        operation = OperationCreator.create(op, para)
        tm.step(operation, i + 1)

    tick = len(case) + 1
    while tm.blocked == True:
        prev_size = len(tm.blocked)
        tick += 1
        tm.retry(tick)
        new_size = len(tm.blocked)

        if prev_size == new_size:
            print("error: not terminable")
            break
