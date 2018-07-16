from twisted.logger import Logger
from twisted.internet import defer, reactor
from twisted.enterprise import adbapi

from nx.viper.application import Application as ViperApplication

import pymysql
pymysql.install_as_MySQLdb()


class Service:
    """
    MySQL Database service

    Wrapper for Twisted's adbapi for interacting with a MySQL database.
    """
    log = Logger()

    def __init__(self, application):
        self.application = application
        self.application.eventDispatcher.addObserver(
            ViperApplication.kEventApplicationStart,
            self._applicationStart
        )

    def _applicationStart(self, data):
        """
        Initializes the database connection pool.

        :param data: <object> event data object
        :return: <void>
        """
        checkup = False
        if "viper.mysql" in self.application.config \
                and isinstance(self.application.config["viper.mysql"], dict):
            if "host" in self.application.config["viper.mysql"] and \
                    "port" in self.application.config["viper.mysql"] and \
                    "name" in self.application.config["viper.mysql"]:
                if len(self.application.config["viper.mysql"]["host"]) > 0 and \
                        self.application.config["viper.mysql"]["port"] > 0 and \
                        len(self.application.config["viper.mysql"]["name"]) > 0:
                    checkup = True

        if checkup is not True:
            return

        try:
            self._connectionPool = adbapi.ConnectionPool(
                "MySQLdb",
                host=self.application.config["viper.mysql"]["host"],
                port=int(self.application.config["viper.mysql"]["port"]),

                user=self.application.config["viper.mysql"]["username"],
                passwd=self.application.config["viper.mysql"]["password"],

                db=self.application.config["viper.mysql"]["name"],
                charset=self.application.config["viper.mysql"]["charset"],

                cp_min=int(
                    self.application.config["viper.mysql"]["connectionsMinimum"]
                ),
                cp_max=int(
                    self.application.config["viper.mysql"]["connectionsMaximum"]
                ),
                cp_reconnect=True
            )
        except Exception as e:
            self.log.error(
                "[Viper.Database] Cannot connect to server. Error: {error}",
                error=str(e)
            )

    def runInteraction(self, interaction, *args, **kwargs):
        """
        Interact with the database and return the result.

        :param interaction: <function> method with first argument is a <adbapi.Transaction> instance
        :param args: additional positional arguments to be passed to interaction
        :param kwargs: keyword arguments to be passed to interaction
        :return: <defer>
        """
        return self._connectionPool.runInteraction(
            interaction,
            *args,
            **kwargs
        )

    def runQuery(self, *args, **kwargs):
        """
        Execute an SQL query and return the result.

        :param args: additional positional arguments to be passed to cursor execute method
        :param kwargs: keyword arguments to be passed to cursor execute method
        :return: <defer>
        """
        return self._connectionPool.runQuery(*args, **kwargs)

    def runOperation(self, *args, **kwargs):
        """
        Execute an SQL query and return None.

        :param args: additional positional arguments to be passed to cursor execute method
        :param kwargs: keyword arguments to be passed to cursor execute method
        :return: <defer>
        """
        return self._connectionPool.runOperation(*args, **kwargs)
