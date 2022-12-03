class FileLoader(object):

    def __init__(self, file_name):
        self._lines = []
        self._buffer_idx = -1

        line_count = 0
        with open(file_name, 'r') as filename:         
            for line in filename.readlines():
                if line[:2] != "//":  
                    self._lines.append(line.strip())
                    line_count += 1

        self._end_idx = line_count - 1
        

    def next_case(self):

        res = []
        for line in self._lines[self._buffer_idx + 1:]:
            self._buffer_idx += 1
            stripped = line.strip()
            if stripped != ('' or "<END>"):
              if line[:2] != '//':
                res.append(stripped)
        return res

    def has_next(self):
        if self._buffer_idx < self._end_idx:
          return True
        else:
          return False
