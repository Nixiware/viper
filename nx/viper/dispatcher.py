import os
import importlib.util


class Dispatcher():
    application = None

    def __init__(self, application):
        self.application = application

    def dispatch(self, requestProtocol, requestPayload):
        """Dispatches the request to the appropiate handler."""
        # method decoding
        method = requestPayload["method"].split(".")
        if len(method) != 3:
            requestProtocol.failRequestWithErrors(["InvalidMethod"])
            return

        # parsing method name
        methodModule = method[0]
        methodController = method[1]
        methodAction = method[2]

        # checking if module exists
        if not self.application.isModuleLoaded(methodModule):
            requestProtocol.failRequestWithErrors(["InvalidMethodModule"])
            return

        # checking if controller exists
        controllerPath = os.path.join(
            "application",
            "module",
            methodModule,
            "controller",
            "{}.py".format(methodController)
        )
        if not os.path.isfile(controllerPath):
            requestProtocol.failRequestWithErrors(["InvalidMethodController"])
            return

        # importing controller
        controllerSpec = importlib.util.spec_from_file_location(
            methodController,
            controllerPath
        )
        controller = importlib.util.module_from_spec(controllerSpec)
        controllerSpec.loader.exec_module(controller)

        # instancing controller
        controllerInstance = controller.Controller(
            self.application,
            requestProtocol,
            requestPayload["version"],
            requestPayload["parameters"]
        )

        # checking if action exists
        action = getattr(
            controllerInstance,
            "{}Action".format(methodAction),
            None
        )
        if not callable(action):
            requestProtocol.failRequestWithErrors(["InvalidMethodAction"])
            return

        # executing action
        requestProtocol.requestPassedDispatcherValidation()

        preDispatchAction = getattr(controllerInstance, "preDispatch")
        postDispatchAction = getattr(controllerInstance, "postDispatch")

        preDispatchAction()
        action()
        postDispatchAction()
