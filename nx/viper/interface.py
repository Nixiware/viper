class AbstractApplicationInterfaceProtocol():
    """
    Abstract class for all Viper application communication interface.

    Base interface class for all interfaces instantiated by the Viper application.
    """

    def setup(self):
        """
        Prepares the interface for handling the connection.
        Should be called from the extending interface as soon as possible.

        :return: <void>
        """
        self.requestResponse = {
            "code": 0,
            "content": None,
            "errors": []
        }

    def getIPAddress(self):
        """
        Return the connection client IP address.

        :return: <str>
        """
        raise NotImplementedError(
            "AbstractApplicationInterfaceProtocol - " \
            "getIPAddress"
        )

    def requestPassedDispatcherValidation(self):
        """
        Called before request is passed to controller.

        :return: <void>
        """
        raise NotImplementedError(
            "AbstractApplicationInterfaceProtocol - " \
            "requestPassedDispatcherValidation"
        )

    def failRequestWithErrors(self, errors):
        """
        End the connection with a failure.

        :param errors: <list> errors as <str>
        :return: <void>
        """
        raise NotImplementedError(
            "AbstractApplicationInterfaceProtocol - " \
            "failRequestWithErrors"
        )

    def sendPartialRequestResponse(self):
        """
        Send a partial response over the connection.

        :return: <void>
        """
        raise NotImplementedError(
            "AbstractApplicationInterfaceProtocol - " \
            "sendPartialRequestResponse"
        )

    def sendFinalRequestResponse(self):
        """
        Send a final response over the connection.

        :return: <void>
        """
        raise NotImplementedError(
            "AbstractApplicationInterfaceProtocol - " \
            "sendFinalRequestResponse"
        )
