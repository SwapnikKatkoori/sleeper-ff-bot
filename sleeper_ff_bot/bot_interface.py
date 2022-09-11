class BotInterface:
    def __init__(self, bot_id):
        self.bot_id = bot_id

    def send_message(self, message):
        """
        Will be implemented in each derived class differently. Sends a message to the chat. NotImplemented error
        if the method is not implemented in a subclass.
        :param message: The message to send
        :return: None
        """
        raise NotImplementedError('A send message method has not been implemented')

    def send(self, callback, *args):
        """

        :param callback: The callback function to call
        :param args: The arguments to the callback function
        :return: None
        """
        try:
            message = callback(*args)
        except Exception as err:
            message = "There was an error that occurred with the bot: {}\n\n".format(err)
            message += "Please report it at https://github.com/cyrusfarsoudi/sleeper-ff-bot/issues"
        self.send_message(message)
