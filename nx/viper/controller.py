class Controller:
    """
    Viper controller

    Base controller class for controllers instantiated by the Viper dispatcher.
    """

    def __init__(self, application, requestProtocol, requestVersion, requestParameters):
        self.application = application
        self.requestProtocol = requestProtocol
        self.requestVersion = requestVersion
        self.requestParameters = requestParameters

        self.responseCode = 0
        self.responseContent = {}
        self.responseErrors = []

    def preDispatch(self):
        """
        Method called before the request action is triggered.

        :return: <void>
        """
        pass

    def postDispatch(self):
        """
        Method called after the request action is triggered.

        :return: <void>
        """
        pass

    def sendPartialResponse(self):
        """
        Send a partial response without closing the connection.

        :return: <void>
        """
        self.requestProtocol.requestResponse["code"] = (
            self.responseCode
        )
        self.requestProtocol.requestResponse["content"] = (
            self.responseContent
        )
        self.requestProtocol.requestResponse["errors"] = (
            self.responseErrors
        )
        self.requestProtocol.sendPartialRequestResponse()

    def sendFinalResponse(self):
        """
        Send the final response and close the connection.

        :return: <void>
        """
        self.requestProtocol.requestResponse["code"] = (
            self.responseCode
        )
        self.requestProtocol.requestResponse["content"] = (
            self.responseContent
        )
        self.requestProtocol.requestResponse["errors"] = (
            self.responseErrors
        )
        self.requestProtocol.sendFinalRequestResponse()
