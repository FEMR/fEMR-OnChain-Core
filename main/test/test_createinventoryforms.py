from main.management.commands.createinventoryforms import Command


def test_command():
    c = Command()
    c.handle()
