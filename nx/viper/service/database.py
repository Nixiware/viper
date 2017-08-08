from twisted.enterprise import adbapi
import pymysql

from nx.viper.application import Application as ViperApplication

pymysql.install_as_MySQLdb()


class Service:
    _connectionPool = None

    def __init__(self, application):
        self.application = application
        self.application.eventDispatcher.addObserver(
            ViperApplication.kEventApplicationStart,
            self._applicationStart
        )

    def _applicationStart(self, data):
        """Initializes the database connection pool."""
        self._connectionPool = adbapi.ConnectionPool(
            "MySQLdb",
            host=self.application.config["database"]["host"],
            port=int(self.application.config["database"]["port"]),

            user=self.application.config["database"]["username"],
            passwd=self.application.config["database"]["password"],

            db=self.application.config["database"]["name"],
            charset=self.application.config["database"]["charset"],

            cp_min=int(
                self.application.config["database"]["connectionsMinimum"]
            ),
            cp_max=int(
                self.application.config["database"]["connectionsMaximum"]
            ),
            cp_reconnect=True
        )

    def runInteraction(self, interaction, *args, **kwargs):
        """Interact with the database and return the result."""
        return self._connectionPool.runInteraction(
            interaction,
            *args,
            **kwargs
        )

    def runOperation(self, *args, **kwargs):
        """Execute an SQL query and return L{None}."""
        return self._connectionPool.runOperation(*args, *kwargs)

    def runQuery(self, *args, **kwargs):
        """Execute an SQL query and return the result."""
        return self._connectionPool.runQuery(*args, **kwargs)
