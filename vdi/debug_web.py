import sys, os
sys.path.append(os.path.abspath('.'))
from actions import *



def generate():

    runGenerate= RunGenerate()
    runGenerate.config={
        '01_broker_primary_ip':'10.1.99.156',
        '02_broker_primary_username':'spitsa',
        '03_broker_primary_authenticator':'ad',
        '04_broker_primary_password':'Qwer1234',
        '05_broker_secondary_ip':'10.1.99.149',
        '06_broker_secondary_username':'root',
        '07_broker_secondary_authenticator':'admin',
        '08_broker_secondary_password':'udsmam0',
        '09_service_pool_name':'Windows Server;Windows Static Multiple'
    }
    runGenerate.packs_path=r'C:\Users\Anakim\Documents\xrm-vdi-pack\.saved'
    runGenerate.run(plan_name= 'test22041')


def failover():

    runFailOver= RunFailOver()
    runFailOver.packs_path=r'C:\Users\Anakim\Documents\xrm-vdi-pack\.saved'
    runFailOver.run(plan_name= 'test22041')

 #=========================================

#generate()
failover()
