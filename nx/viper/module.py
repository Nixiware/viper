import os
import importlib.util

from nx.viper.config import Config


class Module:
    def __init__(self, moduleName, modulePath, application):
        self.name = moduleName
        self.path = os.path.dirname(os.path.realpath(modulePath))
        self.application = application

        self._loadConfiguration()
        self._loadModels()
        self._loadServices()

    def _loadConfiguration(self):
        """Load module configuration files."""
        configPath = os.path.join(self.path, "config")
        if not os.path.isdir(configPath):
            return

        config = Config(configPath)

        Config.mergeDictionaries(config.getData(), self.application.config)

    def _loadModels(self):
        """Load module models."""
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
        """Load module services."""
        servicesPath = os.path.join(self.path, "service")
        if not os.path.isdir(servicesPath):
            return

        for serviceFile in os.listdir(servicesPath):
            serviceName = serviceFile.replace(".py", "")
            servicePath = os.path.join(
                self.path, "service", serviceFile
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
            serviceInstance = service.Service(self.application)
            self.application.addService(
                self.name,
                serviceName,
                serviceInstance
            )
