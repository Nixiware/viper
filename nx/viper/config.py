import os
import json
import re

from twisted.logger import Logger


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
        log = Logger()
        varNamePattern = re.compile(r"^((__((ENV)|(FILE))__[A-Z]{3,})|(__((ENV)|(FILE))))__(?P<name>.*)$")
        varTypePattern = re.compile(r"^__((ENV)|(FILE))__(?P<type>[A-Z]{3,})__(.*)$")

        for key, value in sourceDictionary.items():
            # ignoring comments
            if key == "//":
                continue

            if isinstance(value, dict):
                # get node or create one
                node = destinationDictionary.setdefault(key, {})
                Config.mergeDictionaries(value, node)
            elif isinstance(value, str) and (value.startswith("__ENV__") or value.startswith("__FILE__")):
                # extracting environment variable name
                nameMatch = varNamePattern.match(value)
                if nameMatch is None:
                    log.warn("Invalid environmental variable specified: {name}", name=value)
                    continue
                envVariableName = nameMatch.group("name")

                # checking if environment variable is set
                if envVariableName not in os.environ:
                    log.warn("No environment variable {name} is set.", name=envVariableName)
                    continue

                if value.startswith("__ENV__"): # checking if value is set in the environment variable
                    # checking if variable has a defined cast type
                    typeMatch = varTypePattern.match(value)
                    if typeMatch is not None:
                        envVariableType = typeMatch.group("type")

                        # casting value to the specified type
                        if envVariableType == "STR":
                            destinationDictionary[key] = str(os.environ[envVariableName])
                        elif envVariableType == "BOOL":
                            if os.environ[envVariableName] == "1":
                                destinationDictionary[key] = True
                            elif os.environ[envVariableName] == "0":
                                destinationDictionary[key] = False
                        elif envVariableType == "INT":
                            destinationDictionary[key] = int(os.environ[envVariableName])
                        elif envVariableType == "FLOAT":
                            destinationDictionary[key] = float(os.environ[envVariableName])
                        elif envVariableType == "JSON":
                            try:
                                destinationDictionary[key] = json.loads(os.environ[envVariableName])
                            except Exception:
                                log.warn(
                                    "Environment variable {name} contains an invalid JSON value.",
                                    name=envVariableName
                                )
                        else:
                            log.warn(
                                "Unsupported type {type} specified for variable {name}.",
                                name=envVariableName,
                                type=envVariableType
                            )
                            continue
                    else:
                        destinationDictionary[key] = os.environ[envVariableName]
                elif value.startswith("__FILE__"): # checking if value is set in a file
                    filePath = os.environ[envVariableName]

                    # checking if file exists
                    if not os.path.isfile(filePath):
                        log.warn(
                            "File {filePath} does not exist.",
                            filePath=filePath,
                        )
                        continue

                    # checking if file can be read
                    if not os.access(filePath, os.R_OK):
                        log.warn(
                            "File {filePath} cannot be read.",
                            filePath=filePath,
                        )
                        continue

                    # load file contents
                    filePointer = open(filePath, "r")
                    destinationDictionary[key] = filePointer.read().strip()
                    filePointer.close()
            elif isinstance(value, str) and value.startswith("__FILE__"):
                pass
            else:
                destinationDictionary[key] = value

        return destinationDictionary
