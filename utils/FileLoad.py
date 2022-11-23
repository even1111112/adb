class FileLoader(object):

    def __init__(self, file_name):
        self._lines = []
        self._buffer_idx = -1

        line_count = 0
        with open(file_name, 'r') as f:
          
            for line in f.readlines():
                if line[:2] != "//":  
                    self._lines.append(line.strip())
                    line_count += 1

        self._end_idx = line_count - 1
        

    def next_case(self):

        operations = []
        for line in self._lines[self._buffer_idx + 1:]:
            self._buffer_idx += 1

            if line.strip() == "<END>":
                break
            elif line.strip() != '':
                if line[:2] != '//':
                   operations.append(line.strip())

        return operations

    def has_next(self):
        if self._buffer_idx < self._end_idx:
          return True
        else:
          return False
