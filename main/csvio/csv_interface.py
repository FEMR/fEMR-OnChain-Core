class CSVHandler(object):
    def __init__(self) -> None:
        super().__init__()
        pass

    def read(self, upload, campaign):
        return self.__import(upload, campaign)

    def write(self, response, formulary):
        return self.__export(response, formulary)

    def __import(self, upload, campaign):
        pass

    def __export(self, response, formulary):
        pass
