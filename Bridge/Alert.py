import time


class Alert:
    def __init__(self, errorType: str, errorString: str):
        self.errorType = errorType
        self.errorString = errorString
        self.time = time.time()
    def toDict(self):
        return {'ErrorType': self.errorType, 'ErrorString': self.errorString, "ErrorTime": time.strftime('[%d/%m/%y | %T]', time.gmtime(self.time + 3600))}