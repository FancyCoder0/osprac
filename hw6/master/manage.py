from flask import Flask
from app import create_app
from flask_script import Manager

CONFIGURE_MODE = "default"

app = create_app(CONFIGURE_MODE)

manager = Manager(app)

@manager.command
def test():
	"""Run the unit tests."""
	import unittest
	tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == "__main__":
    manager.run()

