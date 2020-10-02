# classes for the message log
# from: http://rogueliketutorials.com/tutorials/tcod/part-7/

import tcod
import textwrap

# a message object to be printed in a particular color in the message log
class Message:
    def __init__(self, text, color=tcod.white):
        self.text = text
        self.color = color

# the UI element that shows prints messages
class MessageLog:
    def __init__(self, x, width, height):
        self.messages = []
        self.x = x
        self.width = width
        self.height = height

    # adds a message to the log
    def add_message(self, message):
        # split the message if necessary, among multiple lines
        new_msg_lines = textwrap.wrap(message.text, self.width)

        for line in new_msg_lines:
            # if the buffer is full, remove the first line to make room for the new one
            if len(self.messages) == self.height:
                self.messages.pop(0)

            # add the new line as a Message object, with the text and the color
            self.messages.append(Message(line, message.color))