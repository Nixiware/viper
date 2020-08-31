import os
import ntpath
import importlib.util

from nx.viper.config import Config


class Module:
    """
    Viper module

    Container for services and their configuration.
    """

    def __init__(self, moduleName, modulePath, application):
        self.name = moduleName
        self.path = os.path.dirname(os.path.realpath(modulePath))
        self.application = application

        self._loadConfiguration()
        self._loadServices()

    def _loadConfiguration(self):
        """
        Load module configuration files.

        :return: <void>
        """
        configPath = os.path.join(self.path, "config")
        if not os.path.isdir(configPath):
            return

        config = Config(configPath)

        Config.mergeDictionaries(config.getData(), self.application.config)

    def _loadServices(self):
        """
        Load module services.

        :return: <void>
        """
        servicesPath = os.path.join(self.path, "service")
        if not os.path.isdir(servicesPath):
            return

        self._scanDirectoryForServices(servicesPath)

    def _scanDirectoryForServices(self, directoryPath):
        """
        Scan a directory looking for service files.
        If another directory is found (excluding any python bytecode cache), the method recursively calls itself on
        that directory.
        If a .py file is found, a quiet attempt to load the service from it is performed.

        :param: <str> path to look for services
        :return: <void>
        """
        # checking if path is actually a directory
        if not os.path.isdir(directoryPath):
            return

        for item in os.listdir(directoryPath):
            itemPath = os.path.join(
                directoryPath, item
            )

            if os.path.isdir(itemPath) and not item.startswith("__") and not item.startswith("."):
                self._scanDirectoryForServices(itemPath)
                continue

            if os.path.isfile(itemPath) and itemPath.lower().endswith((".py",)):
                self._loadService(itemPath)
                continue

    def _loadService(self, servicePath):
        """
        Check if an application service can be found at the specified path.
        If found, instantiate it and add it to the application service pool.

        :param: <str> service file path
        :return: <void>
        """
        serviceName = ntpath.basename(servicePath).replace(".py", "")

        # importing service
        serviceSpec = importlib.util.spec_from_file_location(
            serviceName,
            servicePath
        )
        service = importlib.util.module_from_spec(serviceSpec)
        serviceSpec.loader.exec_module(service)

        # checking if there is a service in the file
        if hasattr(service, "Service"):
            # instantiate the service
            serviceInstance = service.Service(self.application)
            self.application.addService(
                self.name,
                serviceName,
                serviceInstance
            )
