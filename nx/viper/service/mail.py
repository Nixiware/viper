import smtplib

from twisted.logger import Logger

from nx.viper.application import Application


class Service:
    """
    SMTP mail service

    Email sender based on Pythons's smtplib.
    """
    log = Logger()

    def __init__(self, application):
        self.application = application

        self.application.eventDispatcher.addObserver(
            Application.kEventApplicationStart,
            self._applicationStart
        )

    def _applicationStart(self, data):
        self.configured = False

        if "viper.mail" in self.application.config:
            if "host" in self.application.config["viper.mail"] \
                    and "port" in self.application.config["viper.mail"]:
                if len(self.application.config["viper.mail"]["host"]) > 0 and \
                        self.application.config["viper.mail"]["port"] > 0:
                    self.configured = True

    def send(self, recipient, subject, message):
        """
        Sends an email using the SMTP connection.

        :param recipient: <tuple> recipient's email address as the first element and their name as an optional second
                            element
        :param subject: <str> mail subject
        :param message: <str> mail content (as HTML markup)
        :return: <bool> True if mail was sent successfully, False otherwise
        """
        if self.configured is False:
            return False

        # connecting to server
        try:
            self.smtp = smtplib.SMTP(
                self.application.config["viper.mail"]["host"],
                self.application.config["viper.mail"]["port"]
            )

            self.smtp.connect(
                self.application.config["viper.mail"]["host"],
                self.application.config["viper.mail"]["port"]
            )

            if self.application.config["viper.mail"]["tls"]:
                self.smtp.starttls()
        except Exception as e:
            if hasattr(self, "smtp") and self.smtp is not None:
                self.smtp.quit()

            self.log.warn(
                "[Viper.Mail] Cannot connect to server. Error: {error}",
                error=str(e)
            )
            return False

        # performing authentication
        if len(self.application.config["viper.mail"]["username"]) > 0:
            try:
                self.smtp.login(
                    self.application.config["viper.mail"]["username"],
                    self.application.config["viper.mail"]["password"]
                )
            except Exception as e:
                if hasattr(self, "smtp") and self.smtp is not None:
                    self.smtp.quit()

                self.log.warn(
                    "[Viper.Mail] Cannot authenticate with server. Error: {error}",
                    error=str(e)
                )
                return False

        # composing message headers
        messageHeaders = []
        messageHeaders.append("From: {} <{}>".format(
            self.application.config["viper.mail"]["name"],
            self.application.config["viper.mail"]["from"]
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
                self.application.config["viper.mail"]["from"],
                [recipient[0]],
                emailContents
            )
        except smtplib.SMTPRecipientsRefused as e:
            if hasattr(self, "smtp") and self.smtp is not None:
                self.smtp.quit()

            self.log.warn(
                "[Viper.Mail] Server refused mail recipients: " \
                "{recipients}. Error: {error}",
                recipients=recipient,
                error=str(e)
            )
            return False
        except smtplib.SMTPSenderRefused as e:
            if hasattr(self, "smtp") and self.smtp is not None:
                self.smtp.quit()

            self.log.warn(
                "[Viper.Mail] Server refused mail sender: {sender}. " \
                "Error: {error}",
                sender=self.application.config["viper.mail"]["from"],
                error=str(e)
            )
            return False
        except Exception as e:
            if hasattr(self, "smtp") and self.smtp is not None:
                self.smtp.quit()

            self.log.warn(
                "[Viper.Mail] Server refused to deliver mail. Error: {error}",
                error=str(e)
            )
            return False

        return True
