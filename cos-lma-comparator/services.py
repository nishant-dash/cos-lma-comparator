import json

class NagiosService():
    def __init__(self, sc, context):
        for k, v in sc.items():
            setattr(self, k, v)
        self.nagios_context = context
        self.__extractUnitName()

    def __str__(self):
        return json.dumps(self.__dict__, indent=2)
    
    def __haveMatchingContext(self):
        return self.host_display_name.startswith(self.nagios_context)
    
    def __extractUnitName(self):
        if self.__haveMatchingContext():
            self.juju_unit = self.host_display_name[len(self.nagios_context)+1:].replace("-", "/")
        else:
            self.juju_unit = None

    def __extractAppName(self):
        if self.juju_unit:
            self.app_name = self.juju_unit.splint("/")[0]
    

class NagiosClient():
    def __init__(self, nagios_context):
        self.nagios_host_context = nagios_context
        self.fetchNagiosData()

    def fetchNagiosData(self):
        with open("nagios.services") as fd:
            services_raw = json.load(fd)

        self.services = []
        for s in services_raw:
            service = NagiosService(s, self.nagios_host_context)
            if service.juju_unit:
                self.services.append(service)