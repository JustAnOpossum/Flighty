import configparser
from os.path import exists

keys = configparser.ConfigParser()
isLoaded = False

# Loads API keys from file


def loadKeys(configFile):
    if (not exists(configFile)):
        print("No credentials file found")
        return
    else:
        print("Loading keys...")
        isLoaded = True
        keys.read(configFile)

# Gets a key from the config file


def getKey(keyName):
    if isLoaded:
        try:
            return keys['KEYS'][keyName]
        except:
            return ""
