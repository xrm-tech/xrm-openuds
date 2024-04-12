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


class RunFailOver(Action):
    __result= False
    __service_pool:ServicePool
    __service_provider:ServiceProvider
    __authenticator:Authenticator
    __transport:Transport
    __permissions:Permissions

    def __load_plan_data(self, plan):
        
        packs_path= '/opt/stackstorm/packs/saved/'
        plan_ending= '.plandata'
        os.makedirs(os.path.dirname(packs_path), exist_ok=True)
        plan_full_name= os.path.join(packs_path, plan + plan_ending)
        print(plan_full_name)

        with open(plan_full_name, 'rb') as f:
            plan_data_dict= pickle.load(f)
        
        
        self.__service_pool: ServicePool= plan_data_dict['service_pool']
        self.__service_provider: ServiceProvider= plan_data_dict['service_provider']
        self.__authenticator: Authenticator= plan_data_dict['authenticator']
        self.__transport: Transport= plan_data_dict['transport']
        self.__permissions: Permissions= plan_data_dict['permissions']

        self.__service_pool.get_logs()
        self.__service_provider.get_logs()
        self.__authenticator.get_logs()
        self.__transport.get_logs()
        self.__permissions.get_logs()
        

    def run(self, plan_name):

        self.__result= True

        try:
            self.__load_plan_data(plan= plan_name)
            
            


        except Exception as e:
            raise Exception('Caught exception: {}'.format(e))

        finally:
            try:
                #primary_broker_connection.logout()    
                pass

            except Exception as e:
                
                print(e)

            return self.__result