from twisted.logger import Logger
from twisted.internet import reactor, defer
from twisted.enterprise import adbapi
from twisted.python.failure import Failure

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
                "[Viper.MySQL] Cannot connect to server. Error: {error}",
                error=str(e)
            )

        if "init" in self.application.config["viper.mysql"] \
                and self.application.config["viper.mysql"]["init"]["runIfEmpty"]:
            self._checkIfDatabaseIsEmpty(
                lambda isEmpty:
                    self._scheduleDatabaseInit(isEmpty)
                ,
                lambda error:
                    self.log.error("[Viper.MySQL] Cannot check if database is empty. Error {error}", error=error)
            )

    def _checkIfDatabaseIsEmpty(self, successHandler=None, failHandler=None):
        """
        Check if database contains any tables.

        :param successHandler: <function(<bool>)> method called if interrogation was successful where the first argument
                                is a boolean flag specifying if the database is empty or not
        :param failHandler: <function(<str>)> method called if interrogation failed where the first argument is the
                                error message
        :return: <void>
        """
        def failCallback(error):
            errorMessage = str(error)
            if isinstance(error, Failure):
                errorMessage = error.getErrorMessage()

            if failHandler is not None:
                reactor.callInThread(failHandler, errorMessage)

        def selectCallback(transaction, successHandler):
            querySelect = \
                "SELECT `TABLE_NAME` " \
                "FROM INFORMATION_SCHEMA.TABLES " \
                "WHERE " \
                "`TABLE_SCHEMA` = %s" \
                ";"

            try:
                transaction.execute(
                    querySelect,
                    (self.application.config["viper.mysql"]["name"],)
                )

                tables = transaction.fetchall()
            except Exception as e:
                failCallback(e)
                return

            if successHandler is not None:
                reactor.callInThread(successHandler, len(tables) == 0)

        interaction = self.runInteraction(selectCallback, successHandler)
        interaction.addErrback(failCallback)

    def _initDatabase(self):
        """
        Initializes the database structure based on application configuration.

        :return: <void>
        """
        queries = []

        if len(self.application.config["viper.mysql"]["init"]["scripts"]) > 0:
            for scriptFilePath in self.application.config["viper.mysql"]["init"]["scripts"]:
                sqlFile = open(scriptFilePath, "r")
                queriesInFile = self.extractFromSQLFile(sqlFile)
                sqlFile.close()

                queries.extend(queriesInFile)

        def failCallback(error):
            errorMessage = str(error)
            if isinstance(error, Failure):
                errorMessage = error.getErrorMessage()

            self.log.error(
                "[Viper.MySQL] _initDatabase() database error: {errorMessage}",
                errorMessage=errorMessage
            )

        def runCallback(transaction, queries):
            try:
                for query in queries:
                    transaction.execute(query)
            except Exception as e:
                failCallback(e)
                return

        interaction = self.runInteraction(runCallback, queries)
        interaction.addErrback(failCallback)

    def _scheduleDatabaseInit(self, isEmpty):
        """
        Schedule database initialization if database is empty.

        :param isEmpty: <bool> flag for database empty status
        :return: <void>
        """
        if isEmpty:
            self._initDatabase()

    def extractFromSQLFile(self, filePointer, delimiter=";"):
        """
        Process an SQL file and extract all the queries sorted.

        :param filePointer: <io.TextIOWrapper> file pointer to SQL file
        :return: <list> list of queries
        """
        data = filePointer.read()

        # reading file and splitting it into lines
        dataLines = []
        dataLinesIndex = 0
        for c in data:
            if len(dataLines) - 1 < dataLinesIndex:
                dataLines.append("")

            if c == "\r\n" or c == "\r" or c == "\n":
                dataLinesIndex += 1
            else:
                dataLines[dataLinesIndex] = "{}{}".format(
                    dataLines[dataLinesIndex],
                    c
                )

        # forming SQL statements from all lines provided
        statements = []
        statementsIndex = 0
        for line in dataLines:
            # ignoring comments
            if line.startswith("--") or line.startswith("#"):
                continue

            # removing spaces
            line = line.strip()

            # ignoring blank lines
            if len(line) == 0:
                continue

            # appending each character to it's statement until delimiter is reached
            for c in line:
                if len(statements) - 1 < statementsIndex:
                    statements.append("")

                statements[statementsIndex] = "{}{}".format(
                    statements[statementsIndex],
                    c
                )

                if c == delimiter:
                    statementsIndex += 1

        return statements

    def runInteraction(self, interaction, *args, **kwargs):
        """
        Interact with the database and return the result.

        :param interaction: <function> method with first argument is a <adbapi.Transaction> instance
        :param args: additional positional arguments to be passed to interaction
        :param kwargs: keyword arguments to be passed to interaction
        :return: <defer>
        """
        try:
            return self._connectionPool.runInteraction(
                interaction,
                *args,
                **kwargs
            )
        except:
            d = defer.Deferred()
            d.errback()
            return d

    def runQuery(self, *args, **kwargs):
        """
        Execute an SQL query and return the result.

        :param args: additional positional arguments to be passed to cursor execute method
        :param kwargs: keyword arguments to be passed to cursor execute method
        :return: <defer>
        """
        try:
            return self._connectionPool.runQuery(*args, **kwargs)
        except:
            d = defer.Deferred()
            d.errback()
            return d

    def runOperation(self, *args, **kwargs):
        """
        Execute an SQL query and return None.

        :param args: additional positional arguments to be passed to cursor execute method
        :param kwargs: keyword arguments to be passed to cursor execute method
        :return: <defer>
        """
        try:
            return self._connectionPool.runOperation(*args, **kwargs)
        except:
            d = defer.Deferred()
            d.errback()
            return d
