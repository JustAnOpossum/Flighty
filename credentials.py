import configparser

keys = configparser.ConfigParser()

#Loads API keys from file
def loadKeys(configFile):
    keys.read(configFile)

#Gets a key from the config file
def getKey(keyName):
    try:
        return keys['KEYS'][keyName]
    except:
        return ""
    