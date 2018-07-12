import os
import json


class Config:
    """
    Configuration

    Load JSON configuration files at a specified directory, prioritizing
    *.local over *.global and merging into a single dictionary.
    Allows inclusion of comments in JSON.
    """

    def __init__(self, directoryPath):
        """
        Load all configuration files at a given path.

        :param directoryPath: <str> path to load
        """
        self._data = {}

        configFiles = os.listdir(directoryPath)
        configFilesPendingLoading = []

        # loading global and *.global.json files
        if "global.json" in configFiles:
            configFilesPendingLoading.append(
                os.path.join(directoryPath, "global.json")
            )
        for configFile in configFiles:
            if configFile.endswith(".global.json"):
                configFilesPendingLoading.append(
                    os.path.join(directoryPath, configFile)
                )

        # loading local and *.local.json files
        if "local.json" in configFiles:
            configFilesPendingLoading.append(
                os.path.join(directoryPath, "local.json")
            )
        for configFile in configFiles:
            if configFile.endswith(".local.json"):
                configFilesPendingLoading.append(
                    os.path.join(directoryPath, configFile)
                )

        # loading remaining config files
        for configFile in configFiles:
            if configFile.endswith(".config.json"):
                configFilesPendingLoading.append(
                    os.path.join(directoryPath, configFile)
                )

        for configFilePath in configFilesPendingLoading:
            configFile = open(configFilePath, "r")
            Config.mergeDictionaries(json.load(configFile), self._data)

    def getData(self):
        """
        Return the loaded configuration data.

        :return: <dict>
        """
        return self._data

    @staticmethod
    def mergeDictionaries(sourceDictionary, destinationDictionary):
        """
        Deep merge dictionaries recursively.

        :param sourceDictionary: <dict> first dictionary with data
        :param destinationDictionary: <dict> second dictionary with data
        :return: <dict> merged dictionary
        """
        for key, value in sourceDictionary.items():
            # ignoring comments
            if key == "//":
                continue

            if isinstance(value, dict):
                # get node or create one
                node = destinationDictionary.setdefault(key, {})
                Config.mergeDictionaries(value, node)
            else:
                destinationDictionary[key] = value

        return destinationDictionary
