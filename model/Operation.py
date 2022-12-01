import re
from . import Operation, print_result, parse_variable_id, do_read
from model.Transaction import Transaction
from configurations import *

TABLE_HEADERS = ["Site Name"] 
for i in range(distinct_variable_counts):
  TABLE_HEADERS.append("x"+str(i+1))

class OperationParser(object):
    @staticmethod
    def parse(line):
        res = re.search("(.*)\((.*?)\)", line)
        p1 = res.group(1)
        p2 = []
        for i in range(len(res.group(2).split(","))):
          p2.append(res.group(2).split(",")[i].strip())
        return p1, p2

class Begin(Operation):
    def __init__(self, para):
        super().__init__(para)
        Operation.__setattr__(self, "op_t", "begin")

    def execute(self, tick, tm, retry=False):

        if Transaction(self.para[0], tick).transaction_id not in tm.transactions:
          tm.transactions[Transaction(self.para[0], tick).transaction_id] = Transaction(self.para[0], tick)
          return True
        raise KeyError("Dupilcated transaction" + str(Transaction(self.para[0], tick).transaction_id))


class BeginRO(Operation):
    def __init__(self, para):
        super().__init__(para)
        Operation.__setattr__(self, "op_t", "beginRO")

    def execute(self, tick, tm, retry=False):
        if Transaction(self.para[0], tick, True).transaction_id not in tm.transactions:
            tm.transactions[Transaction(self.para[0], tick, True).transaction_id] = Transaction(self.para[0], tick, True)
            for i in range(len(tm.sites)):
              tm.sites[i].snapshot(tick)
            return True
        else:
            raise KeyError("Dupilcated transaction" + str(Transaction(self.para[0], tick, True).transaction_id))

class Read(Operation):
    def __init__(self, para):
        super().__init__(para)
        Operation.__setattr__(self, "op_t", "R")

    def execute(self, tick: int, tm, retry=False):

        if retry == False:
            self.save_to_transaction(tm)

        trans_id, var_id_str = self.para[0], self.para[1]
        _, var_id = parse_variable_id(var_id_str)

        if tm.transactions[trans_id].is_readonly == True:
            trans_start_tick = tm.transactions[trans_id].tick

            if var_id % 2 == 1:
                site = tm.get_site(var_id % number_of_sites + 1)
                if site.up == True:
                  if var_id in site.snapshots[trans_start_tick]:
                    if var_id in site.snapshots[trans_start_tick]:
                      print_result(["Transaction", "Site", var_id_str], [[trans_id, str(site.site_id), str(site.get_snapshot_variable(trans_start_tick, var_id))]])
                      return True
                else:
                  return False

            elif var_id % 2 == 1:
                new_id = var_id % number_of_sites + 1
                site = tm.get_site(new_id)
    
                if site.up == True:
                  if site.data_manager.check_accessibility(var_id):
                    if site.lock_manager.try_lock_variable(trans_id, var_id_str, 0):
                        return do_read(trans_id, var_id, site)
                    else:
                        return False
                else:
                  return False
            else:
                for i in range(len(tm.sites)):
                    if tm.sites[i].up == False:
                        continue
                    elif site.data_manager.check_accessibility(var_id) and site.lock_manager.try_lock_variable(trans_id, var_id_str, 0):
                        return do_read(trans_id, var_id, site)
            return False
        elif var_id % 2 == 1:
            new_id = var_id % number_of_sites + 1
            site = tm.get_site(new_id)
 
            if site.up == True:
              if site.data_manager.check_accessibility(var_id):
                if site.lock_manager.try_lock_variable(trans_id, var_id_str, 0):
                    return do_read(trans_id, var_id, site)
                else:
                    return False
            else:
              return False
        else:
            for i in range(len(tm.sites)):
                if tm.sites[i].up == False:
                    continue
                elif site.data_manager.check_accessibility(var_id) and site.lock_manager.try_lock_variable(trans_id, var_id_str, 0):
                    return do_read(trans_id, var_id, site)
        return False


class Write(Operation):
    def __init__(self, para):
        super().__init__(para)
        Operation.__setattr__(self, "op_t", "W")

    def execute(self, tick: int, tm, retry=False):

        if retry == False:
            self.save_to_transaction(tm)

        trans_id, var_id_str, write_value = self.para[0], self.para[1], self.para[2]
        _, var_id = parse_variable_id(var_id_str)

        if var_id % 2 == 1:
            site = tm.get_site(var_id % number_of_sites + 1)
            if site.up == True and site.lock_manager.try_lock_variable(trans_id, var_id_str, 1):
                logs = site.data_manager.log.get(trans_id, {})
                logs[var_id] = write_value
                site.data_manager.log[trans_id] = logs
                return True
            else:
              return False
        else:
            locked_sites = []
            for i in range(len(tm.sites)):
                site = tm.sites[i]
                if site.up == True:
                  if site.lock_manager.try_lock_variable(trans_id, var_id_str, 1):
                    locked_sites.append(site)
                  else:
                    for i in range(len(locked_sites)):
                      locked_sites[i].try_unlock_variable(var_id_str, trans_id)
                    return False
                else:
                  continue

            if not locked_sites:
                return False

            for i in range(len(locked_sites)):
                logs = locked_sites[i].data_manager.log.get(trans_id, {})
                logs[var_id] = int(write_value)
                locked_sites[i].data_manager.log[trans_id] = logs

            return True

class Dump(Operation):
    def __init__(self, para):
        super().__init__(para)
        Operation.__setattr__(self, "op_t", "dump")

    def execute(self, tick: int, tm, retry=False):
        res = []
        for i in range(len(tm.sites)):
          res.append(tm.sites[i].echo())
        print_result(TABLE_HEADERS, res)
        return True

class Fail(Operation):
    def __init__(self, para):
        super().__init__(para)
        Operation.__setattr__(self, "op_t", "fail")

    def execute(self, tick: int, tm, retry=False):
        site = tm.get_site(int(self.para[0]))
        transactions = site.lock_manager.get_involved_transactions()
        for i in range(len(transactions)):
            tm.transactions[transactions[i]].to_be_aborted = True
        site.fail()
        return True


class Recover(Operation):
    def __init__(self, para):
        super().__init__(para)
        Operation.__setattr__(self, "op_t", "recover")

    def execute(self, tick: int, tm, retry=False):
        tm.get_site(int(self.para[0])).recover()
        return True


class End(Operation):
    def __init__(self, para):
        super().__init__(para)
        Operation.__setattr__(self, "op_t", "end")

    def execute(self, tick: int, tm, retry=False):

        if retry == False:
            self.save_to_transaction(tm)

        if tm.transactions[self.para[0]].to_be_aborted:
            tm.abort(self.para[0], 1)
            return True

        if self.para[0] in tm.blocked_transactions:
            return False

        print("Transaction ", str(self.para[0]), " commit")

        for site in tm.sites:
            if site.up:
              if self.para[0] in site.data_manager.log:
                for key in site.data_manager.log[self.para[0]].keys():
                    site.data_manager.set_variable(key, site.data_manager.log[self.para[0]][key])
                    site.data_manager.is_accessible[key - 1] = True
                site.data_manager.log.pop(self.para[0])
              elif tm.transactions[self.para[0]].tick in site.snapshots:
                site.snapshots.pop(tm.transactions[self.para[0]].tick)

            site.lock_manager.release_transaction_locks(self.para[0])

        if self.para[0] in tm.blocked_transactions:
            tm.transactions.remove(self.para[0])
        tm.wait_for_graph.remove_transaction(self.para[0])
        return True



class OperationCreator(object):
    types = {
        "dump": Dump,
        "W": Write,
        "R": Read,
        "beginRO": BeginRO,
        "begin": Begin,
        "end": End,
        "fail": Fail,
        "recover": Recover
    }

    @staticmethod
    def create(op_t, para):

        if op_t in OperationCreator.types:
          return OperationCreator.types[op_t](para)
        else:
          raise KeyError("Type Error")

