from lib.servicepool import ServicePool
from lib.serviceprovider import ServiceProvider
from lib.authenticator import Authenticator
from lib.transport import Transport
from lib.permissions import Permissions
from st2common.runners.base_action import Action
import pickle
import sys
import os
sys.path.append('/etc/apiclient')
import apiclient

class RunGenerate(Action):
    result= False    

    def __save_plan_data(self, plan:str, service_pool_param, service_provider_param, authenticator_param, transport_param, permissions_param):
        
        plan_data= []
        plan_data.append({'service_pool': service_pool_param})
        plan_data.append({'service_provider': service_provider_param})
        plan_data.append({'authenticator': authenticator_param})
        plan_data.append({'transport': transport_param})
        plan_data.append({'permissions': permissions_param})

        packs_path= '/opt/stackstorm/saved/'
        plan_ending= '.plandata'
        plan_full_name= os.path.join(packs_path, plan, plan_ending)


        with open(plan_full_name, 'wb') as f:
            pickle.dump(plan_data, f)

    def run(self, plan_name):
        data = {"broker_primary_ip": self.config['01_broker_primary_ip'],
                "broker_primary_username": self.config['02_broker_primary_username'],
                "broker_primary_auth": self.config['03_broker_primary_authenticator'],
                "broker_primary_password": self.config['04_broker_primary_password'],
                "broker_secondary_ip": self.config['05_broker_secondary_ip'],
                "broker_secondary_username": self.config['06_broker_secondary_username'],
                "broker_secondary_auth": self.config['07_broker_secondary_authenticator'],
                "broker_secondary_password": self.config['08_broker_secondary_password'],
                "service_pool_name": self.config['09_service_pool_name']}

        primary_broker_connection = apiclient.Client(
            host=data['broker_primary_ip'],
            username=data['broker_primary_username'],
            auth=data['broker_primary_auth'],
            password=data['broker_primary_password']
        )    

        try: 
       
            primary_broker_connection.login()

            service_pool = ServicePool(
                primary_broker= primary_broker_connection,
                pool_name=data['service_pool_name']
            )
            service_pool.get_logs()    

            service_provider = ServiceProvider(
                primary_broker= primary_broker_connection,
                service_pool_data= service_pool.data_list
            )            
            service_provider.get_logs()

            authenticator = Authenticator(
                primary_broker= primary_broker_connection,
                pool_groups_list= service_pool.groups_list,
                pool_assigned_services= service_pool.assigned_services_list
            )
            authenticator.get_logs()

            transport = Transport(
                primary_broker= primary_broker_connection,
                pool_transports_list= service_pool.transports_list
            )
            transport.get_logs()

            permissions = Permissions(
                primary_broker= primary_broker_connection,
                service_pool_param= service_pool,
                service_provider_param= service_provider,
                authenticator_param= authenticator,
                transport_param= transport
            )
            permissions.get_logs()

            self.__save_plan_data(
                plan= plan_name, 
                service_pool_param= service_pool, 
                service_provider_param= service_provider, 
                authenticator_param= authenticator, 
                transport_param= transport, 
                permissions_param =permissions
            )

            self.result= True

        except Exception as e:
            raise Exception('Caught exception: {}'.format(e))

        finally:
            try:
                primary_broker_connection.logout()    

            except Exception as e:
                
                print(e)

            return self.result

