import random

import data.textdata as data


class NoMemberFound(Exception):
    def __init__(self, arg):
        self.arg = arg

    def __str__(self):
        rest = random.choice(data.notfoundelist)
        return f"{rest}\n\nThe Member {self.arg} was not found"


class NoImageFound(Exception):
    def __init__(self, arg):
        self.arg = arg

    def __str__(self):
        return (f'There was no valid image at your source.\n Please provide a valid ```-attachment\n-User\n-Link\n-Emoji\n-Attachment```')


class CustomError(Exception):
    pass
