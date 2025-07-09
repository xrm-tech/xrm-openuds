import sys, os


sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('..'))
from actions import *


def generate():

    runGenerate= RunGenerate()
    runGenerate.config={
        '01_broker_primary_ip':'10.1.141.71',
        '02_broker_primary_username':'root',
        '03_broker_primary_authenticator':'admin',
        '04_broker_primary_password':'udsmam0',
        '05_broker_secondary_ip':'10.1.141.78',
        '06_broker_secondary_username':'root',
        '07_broker_secondary_authenticator':'admin',
        '08_broker_secondary_password':'udsmam0',
        #'09_service_pool_name':'w10-fixed;multistatic-service-frst;multistatic-service-scnd'
        '09_service_pool_name':'deb-linked-xrm;',
        '10_ovirt_secondary_fqdn':'engine-secondary.demo.vdi',
        '11_ovirt_secondary_username':'admin@internal',
        '12_ovirt_secondary_password':'hostvm123',
        '13_ovirt_secondary_cluster_uuid':'ee328b10-561f-11ef-97be-00163e67a658',
        '14_ovirt_secondary_storagedomain_uuid':'',
        '15_ovirt_secondary_golden_vm_uuid':'',
    
    }
    runGenerate.packs_path=r'C:\Users\Anakim\Documents\xrm-vdi-pack\.saved'
    runGenerate.run(plan_name= '1')


def failover():

    runFailOver= RunFailOver()
    runFailOver.packs_path=r'C:\Users\Anakim\Documents\xrm-vdi-pack\.saved'
    runFailOver.run(plan_name= '1')

 #=========================================


def delete():

    runDelete= RunDelete()
    runDelete.packs_path=r'C:\Users\Anakim\Documents\xrm-vdi-pack\.saved'
    runDelete.run(plan_name='1')

generate()
failover()
#delete()
