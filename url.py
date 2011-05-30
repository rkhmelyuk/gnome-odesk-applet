__author__ = 'ruslan'

class url:
    def __init__(self, url):
        self.url = url
        self.params = []

    def addParam(self, name, value):
        self.params.append({name: value})

    def asString(self):
        string = self.url
        first = True
        for param in self.params:
            if first:
                string += "?"
                first = False
            else:
                string += "&"
            for key, value in param.items():
                string += str(key) + '=' + str(value)

        return string

