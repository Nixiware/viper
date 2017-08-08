import smtplib

from nx.viper.application import Application as ViperApplication

from twisted.logger import Logger


class Service:
    log = Logger()
    smtp = None

    def __init__(self, application):
        self.application = application
        self.application.eventDispatcher.addObserver(
            ViperApplication.kEventApplicationStart,
            self._applicationStart
        )

    def _applicationStart(self, data):
        """Initialize the SMTP connection."""
        self.smtp = smtplib.SMTP()

    def send(self, recipient, subject, message):
        """Sends an email using the SMTP connection."""
        # connecting to server
        try:
            self.smtp.connect(
                self.application.config["mail"]["host"],
                self.application.config["mail"]["port"]
            )
        except:
            self.smtp.quit()
            self.log.error("Cannot connect to SMTP server.")
            return False

        # performing authentication
        if len(self.application.config["mail"]["username"]) > 0:
            try:
                self.smtp.login(
                    self.application.config["mail"]["username"],
                    self.application.config["mail"]["password"]
                )
            except:
                self.smtp.quit()
                self.log.error("Cannot authenticate with SMTP server.")
                return False

        # composing message headers
        messageHeaders = []
        messageHeaders.append("From: {} <{}>".format(
            self.application.config["mail"]["name"],
            self.application.config["mail"]["from"]
        ))

        if len(recipient) == 2:
            messageHeaders.append("To: {} <{}>".format(
                recipient[1],
                recipient[0]
            ))
        else:
            messageHeaders.append("To: {}".format(
                recipient[0]
            ))

        messageHeaders.append("MIME-Version: 1.0")
        messageHeaders.append("Content-type: text/html")
        messageHeaders.append("Subject: {}".format(subject))

        # creating email contents
        emailContents = ""
        for messageHeaderLine in messageHeaders:
            if len(emailContents) == 0:
                emailContents = messageHeaderLine
            else:
                emailContents = "{}\n{}".format(
                    emailContents,
                    messageHeaderLine
                )
        emailContents = "{}\n\n{}".format(
            emailContents,
            message
        )

        # sending email
        try:
            self.smtp.sendmail(
                self.application.config["mail"]["from"],
                [recipient[0]],
                emailContents
            )
        except smtplib.SMTPRecipientsRefused:
            self.smtp.quit()
            self.log.warn(
                "SMTP server refused mail recipients: {recipients}.",
                recipients=recipient
            )
            return False
        except smtplib.SMTPSenderRefused:
            self.smtp.quit()
            self.log.warn(
                "SMTP server refused mail sender: {sender}.",
                sender=self.application.config["mail"]["from"]
            )
            return False
        except:
            self.smtp.quit()
            self.log.warn("SMTP server refused to deliver mail.")
            return False

        return True
