import os
import ntpath
import importlib.util

from nx.viper.config import Config


class Module:
    """
    Viper module

    Container for models and services together with their configuration.
    """

    def __init__(self, moduleName, modulePath, application):
        self.name = moduleName
        self.path = os.path.dirname(os.path.realpath(modulePath))
        self.application = application

        self._loadConfiguration()
        self._loadModels()
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

    def _loadModels(self):
        """
        Load module models.

        :return: <void>
        """
        modelsPath = os.path.join(self.path, "model")
        if not os.path.isdir(modelsPath):
            return

        for modelFile in os.listdir(modelsPath):
            modelName = modelFile.replace(".py", "")
            modelPath = os.path.join(
                self.path, "model", modelFile
            )

            if not os.path.isfile(modelPath):
                continue

            # importing model
            modelSpec = importlib.util.spec_from_file_location(
                modelName,
                modelPath
            )
            model = importlib.util.module_from_spec(modelSpec)
            modelSpec.loader.exec_module(model)

            # initializing model
            modelInstance = model.Model(self.application)
            self.application.addModel(self.name, modelName, modelInstance)

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

            if os.path.isdir(itemPath) and not "__pycache__" in itemPath:
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
