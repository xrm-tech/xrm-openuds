import pickle
import sys, os
sys.path.append(os.path.abspath('.'))
sys.path.append('/opt/stackstorm/packs/xrm_openuds/')
from st2common.runners.base_action import Action
from vdi import *

class RunFailOver(Action):
    __result= False
    __service_pool:ServicePool
    __service_provider:ServiceProvider
    __authenticator:Authenticator
    __transport:Transport
    __permissions:Permissions
    packs_path= '/opt/stackstorm/packs/saved/'

    def __load_plan_data(self, plan):

        plan_ending= '.plandata'
        os.makedirs(os.path.dirname(self.packs_path), exist_ok=True)
        plan_full_name= os.path.join(self.packs_path, plan + plan_ending)
        print(plan_full_name)

        with open(plan_full_name, 'rb') as f:
            plan_data_dict={}
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