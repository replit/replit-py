import sys

from replit.comm import context as context
from replit.comm import logger as log
from replit.comm.serialization import pack, unpack


class ReplitImport(object):
    # Only try and dynamically import modules starting with replit.community
    def find_module(self, fullname, path):
        if fullname.startswith('replit.community'):
            log.debug("Using ReplitImport for %s", fullname)
            return self

    def create_module(self, spec):
        name = spec.name.split('.')[-1]

        log.debug("Creating dynamic RPC module for %s", name)

        # Module is a package so we can get rpcs from it
        package = type(sys)(name)
        setattr(package, '__package__', name)
        setattr(package, '__path__', name)

        # Override get attribute to create an RPC proxy for each attempt to
        # access something in the package
        def get_attr(attribute):
            log.debug("Accessing dynamic RPC %s.%s", name, attribute)
            return replit.rpc.RPCProxy(spec.name, attribute)
        setattr(package, '__getattr__', get_attr)

        return package

    # Nothing to do at runtime, we set everything up in create module
    def exec_module(self, module):
        pass

# Add our coustom importer to the system importers
sys.meta_path = [ReplitImport()]
