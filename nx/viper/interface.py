class AbstractApplicationInterfaceProtocol():
    """
    Abstract class for Viper application communication interface.

    All communication interfaces must extend this class in order to
    ensure 100% compatibility with the request dispatcher.
    """
    requestResponse = {
        "code": 0,
        "content": None,
        "errors": []
    }

    def getIPAddress(self):
        raise NotImplementedError(
            "AbstractApplicationInterfaceProtocol - "
            "getIPAddress"
        )

    def requestPassedDispatcherValidation(self):
        raise NotImplementedError(
            "AbstractApplicationInterfaceProtocol - "
            "requestPassedDispatcherValidation"
        )

    def failRequestWithErrors(self, errors):
        raise NotImplementedError(
            "AbstractApplicationInterfaceProtocol - "
            "failRequestWithErrors"
        )

    def sendPartialRequestResponse(self):
        raise NotImplementedError(
            "AbstractApplicationInterfaceProtocol - "
            "sendPartialRequestResponse"
        )

    def sendFinalRequestResponse(self):
        raise NotImplementedError(
            "AbstractApplicationInterfaceProtocol - "
            "sendFinalRequestResponse"
        )
