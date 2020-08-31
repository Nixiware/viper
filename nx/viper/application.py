import os
import ntpath
import importlib.util

from twisted.words.xish.utility import EventDispatcher
from twisted.application.service import Service as TwistedService
from twisted.internet import reactor

from nx.viper.dispatcher import Dispatcher
from nx.viper.config import Config


class Application:
    """
    Viper application

    Core component, handles the loading of configuration, instances all the modules and their services.
    """

    #
    # Events
    #
    eventDispatcher = EventDispatcher()
    kEventApplicationStart = "//event/applicationStart"
    kEventApplicationStop = "//event/applicationStop"

    def __init__(self):
        self.requestDispatcher = Dispatcher(self)

        self.config = self._getConfiguration()
        self._interfaces = self._getInterfaces()

        self._services = {}

        self._loadViperServices()
        self._modules = self._getModules()

    #
    # Configuration
    #
    def _getConfiguration(self):
        """
        Load application configuration files.

        :return: <dict>
        """
        configDirectoryPath = os.path.join("application", "config")
        config = Config(configDirectoryPath)
        configData = config.getData()

        # setting application parameters
        reactor.suggestThreadPoolSize(
            int(configData["performance"]["threadPoolSize"])
        )

        return configData

    #
    # Interfaces
    #
    def _getInterfaces(self):
        """
        Load application communication interfaces.

        :return: <dict>
        """
        interfaces = {}

        interfacesPath = os.path.join("application", "interface")
        interfaceList = os.listdir(interfacesPath)

        for file in interfaceList:
            interfaceDirectoryPath = os.path.join(interfacesPath, file)
            if not os.path.isdir(interfaceDirectoryPath) or file.startswith("__") or file.startswith("."):
                continue

            interfaceName = ntpath.basename(interfaceDirectoryPath)
            interfacePath = os.path.join(interfaceDirectoryPath, interfaceName) + ".py"

            if not os.path.isfile(interfacePath):
                continue

            # importing interface
            interfaceSpec = importlib.util.spec_from_file_location(
                interfaceName,
                interfacePath
            )
            interface = importlib.util.module_from_spec(interfaceSpec)
            interfaceSpec.loader.exec_module(interface)

            # checking if there is an interface in the file
            if hasattr(interface, "Service"):
                # initializing interface
                interfaceInstance = interface.Service(self)
                interfaces[interfaceName] = interfaceInstance

        return interfaces

    def getInterfaces(self):
        """
        Return loaded communication interfaces.

        :return: <dict>
        """
        return self._interfaces

    #
    # Modules
    #
    def _getModules(self):
        """
        Import and load application modules.

        :return: <dict>
        """
        modules = {}
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
            modules[moduleName] = moduleInstance

        return modules

    def isModuleLoaded(self, moduleName):
        """
        Verify if a module is loaded.

        :param moduleName: <str> module name
        :return: <bool> True if loaded, False otherwise
        """
        if moduleName in self._modules:
            return True

        return False

    #
    # Services
    #
    def _loadViperServices(self):
        """
        Load application bundled services.

        :return: <void>
        """
        servicesPath = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "service"
        )
        for serviceFile in os.listdir(servicesPath):
            if serviceFile.startswith("__") or serviceFile.startswith("."):
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
        """
        Add a service instance to the application service pool.

        :param moduleName: <str> module name in which the service is located
        :param serviceName: <str> service name
        :param service: <object> service instance
        :return: <void>
        """
        serviceIdentifier = "{}.{}".format(moduleName, serviceName)
        if serviceIdentifier not in self._services:
            self._services[serviceIdentifier] = service
        else:
            message = "Application - addService() - " \
                      "A service with the identifier {} already exists." \
                      .format(serviceIdentifier)
            raise Exception(message)

    def getService(self, serviceIdentifier):
        """
        Return the requested service instance.

        :param serviceIdentifier: <str> service identifier
        :return: <object> service instance
        """
        if serviceIdentifier in self._services:
            return self._services[serviceIdentifier]
        else:
            message = "Application - getService() - " \
                      "Service with identifier {} does not exist." \
                      .format(serviceIdentifier)
            raise Exception(message)

    def start(self):
        """
        Start the application.

        :return: <void>
        """
        self.eventDispatcher.dispatch(None, self.kEventApplicationStart)

    def stop(self):
        """
        Stop the application.

        :return: <void>
        """
        self.eventDispatcher.dispatch(None, self.kEventApplicationStop)


class ViperApplicationTwistedService(TwistedService):
    """
    Viper application service for deployment with twistd.
    """

    viperApplication = Application()

    def startService(self):
        """
        Start the service.

        :return: <void>
        """
        self.viperApplication.start()

    def stopService(self):
        """
        Stop the service.

        :return: <void>
        """
        self.viperApplication.stop()
