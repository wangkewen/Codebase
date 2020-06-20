class HTTPHeader(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self)
        self._list = {}
        self.update(*args, **kwargs)
    def add(self, name, value):
        http_name = HTTPHeader._transfer_name(name)
        if http_name in self:
            dict.__setitem__(self, http_name, self[http_name] + ',' + value)
            self._as_list[http_name].append(value)
        else:
            self[http_name] = value

    def get_list(self, name):
        http_name = HTTPHeader._transfer_name(name)
        return self._as_list.get(http_name, [])

    def get_all(self):
        for name, list in self._as_list.iteritems():
            for value in list:
                yield (name, value)

    def parse_line(self, line):
        name, value = line.split(":", 1)
        self.add(name, value.strip())

    def parse(cls, headers):
        h = cls()
        for line in headers.splitlines():
            if line:
                h.parse_line(line)
        return h 
 
    def _transfer_name(name):
        return "-".join([word.capitalize() for word in name.split("-")])

    def __setitem__(self, name, value):
        http_name = HTTPHeader._transfer_name(name)
        dict.__setitem__(self, http_name, value)
        self._as_list[http_name] = [value]
     
    def __getitem__(self, name):
        return dict.__getitem__(self, HTTPHeader._transfer_name(name))

    def __delitem__(self, name):
        http_name = HTTPHeader._transfer_name(name)
        dict.__delitem__(self, http_name)
        del self._as_list[http_name]
    
    def get(self, name, default=None):
        return dict.get(self, HTTPHeader._transfer_name(name), default)

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).iteritems():
            self[k] = v

if __name__ == "__main__":
    import doctest
    doctest.testmod()
