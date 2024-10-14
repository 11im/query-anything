import os
import configparser
import argparse

def checkConfig(path:str) :
    if os.path.exists(path) :
        return True
    else: 
        print("Cannot Open File : No Such File %s",path)
        exit(1)

def getConfig(path:str = "./config/config.ini"):
    if checkConfig:
        config=configparser.ConfigParser()
        config.read(path)
        return config
    return None

def getArg():
    parser = argparse.ArgumentParser()
    path = parser.add_argument_group('Path','Configure File Path')
    path.add_argument('--config',required=False, default= "./config/config.ini",type=str,help='Config File Path, Defalut: ./config/config.ini')
    return parser.parse_args().config

def get_API_keys(path:str="./claude.key"):
    with open(path) as f:
        key = f.read()
        f.close()
    return key