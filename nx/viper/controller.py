class Controller:
    """Base controller class that every controller must extend from."""
    responseCode = 0
    responseContent = {}
    responseErrors = []

    def __init__(self, application, requestProtocol, requestParameters):
        self.application = application
        self.requestProtocol = requestProtocol
        self.requestParameters = requestParameters

        self.responseCode = 0
        self.responseContent = {}
        self.responseErrors = []

    def preDispatch(self):
        """Method called before the request action is triggered."""
        pass

    def postDispatch(self):
        """Method called after the request action is triggered."""
        pass

    def sendPartialResponse(self):
        """Sends a partial response without closing the request."""
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
        """Sends the final response and closes the request."""
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
