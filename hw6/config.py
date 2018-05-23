import os

class Config():
    DEBUG = True

class TestingConfig():
    TESTING = True

config = {
    'default': Config,
    'testing': TestingConfig,
}
