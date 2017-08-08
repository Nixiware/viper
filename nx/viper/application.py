import os
import importlib.util

from twisted.words.xish.utility import EventDispatcher
from twisted.application.service import Service as TwistedService
from twisted.internet import reactor

from nx.viper.dispatcher import Dispatcher
from nx.viper.config import Config


class Application():
    """Viper application"""
    requestDispatcher = None
    _interfaces = {}

    _modules = {}
    _models = {}
    _services = {}

    # events
    eventDispatcher = EventDispatcher()
    kEventApplicationStart = "//event/applicationStart"
    kEventApplicationStop = "//event/applicationStop"

    # configuration
    config = {}

    def __init__(self):
        self.requestDispatcher = Dispatcher(self)

        self._loadConfiguration()
        self._loadInterfaces()
        self._loadServices()
        self._loadModules()

    # configuration
    def _loadConfiguration(self):
        """Load application configuration files."""
        configDirectoryPath = os.path.join("application", "config")
        config = Config(configDirectoryPath)

        self.config = config.getData()

        # setting application parameters
        reactor.suggestThreadPoolSize(
            int(self.config["performance"]["threadPoolSize"])
        )

    # interfaces
    def _loadInterfaces(self):
        """Import and load application communication interfaces."""
        interfacesPath = os.path.join("application", "interface")
        interfaceList = os.listdir(interfacesPath)

        for interfaceFile in interfaceList:
            if not interfaceFile.endswith(".py") or interfaceFile.startswith("__"):
                continue

            # importing interface
            interfacePath = os.path.join(interfacesPath, interfaceFile)
            interfaceName = interfaceFile.replace(".py", "")
            interfaceSpec = importlib.util.spec_from_file_location(
                interfaceName,
                interfacePath
            )
            interface = importlib.util.module_from_spec(interfaceSpec)
            interfaceSpec.loader.exec_module(interface)

            # initializing interface
            interfaceInstance = interface.Service(self)
            self._interfaces[interfaceName] = interfaceInstance

    def getInterfaces(self):
        """Returns the loaded communication interfaces."""
        return self._interfaces

    # modules
    def _loadModules(self):
        """Import and load application modules."""
        modulesPath = os.path.join("application", "module")
        moduleList = os.listdir(modulesPath)

        for moduleName in moduleList:
            modulePath = os.path.join(modulesPath, moduleName, "module.py")
            if not os.path.isfile(modulePath):
                continue

            # importing module
            moduleSpec = importlib.util.spec_from_file_location(
                moduleName,
                modulePath
            )
            module = importlib.util.module_from_spec(moduleSpec)
            moduleSpec.loader.exec_module(module)

            # initializing module
            moduleInstance = module.Module(self)
            self._modules[moduleName] = moduleInstance

    def isModuleLoaded(self, moduleName):
        """Checks if a module is loaded."""
        if moduleName in self._modules:
            return True

        return False

    # models
    def addModel(self, moduleName, modelName, model):
        """Adds a model instance to the application model pool."""
        modelIdentifier = "{}.{}".format(moduleName, modelName)
        if modelIdentifier not in self._models:
            self._models[modelIdentifier] = model
        else:
            message = "Application - addModel() - " \
                      "A model with the identifier {} already exists." \
                      .format(modelIdentifier)
            raise Exception(message)

    def getModel(self, modelIdentifier):
        """Returns the requested model."""
        if modelIdentifier in self._models:
            return self._models[modelIdentifier]
        else:
            message = "Application - getModel() - " \
                      "Service with identifier does not exist." \
                      .format(modelIdentifier)
            raise Exception(message)

    # services
    def _loadServices(self):
        """Load application bundled services."""
        servicesPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "service")
        for serviceFile in os.listdir(servicesPath):
            if serviceFile.startswith("__"):
                continue

            serviceName = serviceFile.replace(".py", "")
            servicePath = os.path.join(
                servicesPath, serviceFile
            )

            if not os.path.isfile(servicePath):
                continue

            # importing service
            serviceSpec = importlib.util.spec_from_file_location(
                serviceName,
                servicePath
            )
            service = importlib.util.module_from_spec(serviceSpec)
            serviceSpec.loader.exec_module(service)

            # initializing service
            serviceInstance = service.Service(self)
            self.addService("viper", serviceName, serviceInstance)

    def addService(self, moduleName, serviceName, service):
        """Adds a service instance to the application service pool."""
        serviceIdentifier = "{}.{}".format(moduleName, serviceName)
        if serviceIdentifier not in self._services:
            self._services[serviceIdentifier] = service
        else:
            message = "Application - addService() - " \
                      "A service with the identifier {} already exists." \
                      .format(serviceIdentifier)
            raise Exception(message)

    def getService(self, serviceIdentifier):
        """Returns the requested service."""
        if serviceIdentifier in self._services:
            return self._services[serviceIdentifier]
        else:
            message = "Application - getService() - " \
                      "Service with identifier does not exist." \
                      .format(serviceIdentifier)
            raise Exception(message)

    def start(self):
        """Starts the application."""
        self.eventDispatcher.dispatch(None, self.kEventApplicationStart)

    def stop(self):
        """Stops the application."""
        self.eventDispatcher.dispatch(None, self.kEventApplicationStop)


class ViperApplicationTwistedService(TwistedService):
    """Viper application service for twistd to run."""
    viperApplication = Application()

    def startService(self):
        self.viperApplication.start()

    def stopService(self):
        self.viperApplication.stop()
