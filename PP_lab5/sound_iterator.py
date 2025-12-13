import csv

class SoundPathIterator:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self._file = None
        self._reader = None

    def __iter__(self):
        self._file = open(self.csv_path, mode='r', encoding='utf-8', newline='')
        self._reader = csv.reader(self._file)
        next(self._reader, None)
        return self

    def __next__(self):
        try:
            row = next(self._reader)
            if len(row) >= 2:
                return row[1] 
            else:
                raise StopIteration
        except StopIteration:
            if self._file:
                self._file.close()
            raise