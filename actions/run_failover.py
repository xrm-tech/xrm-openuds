import pickle
import sys, os

sys.path.append(os.path.abspath('.'))
sys.path.append('/opt/stackstorm/packs/xrm_openuds/')
from st2common.runners.base_action import Action
from vdi import *
from apiclient import Client


class RunFailOver(Action):
    __result = None
    packs_path = '/opt/stackstorm/packs/saved/'

    def __send_data(self, plan_data_list_param):
        created_auths_id = {}
        created_groups_id = {}

        for plan_index, plan_data_dict in enumerate(plan_data_list_param):
            try:
                service_name = plan_data_dict['service_name']
                service_pool = plan_data_dict['service_pool']
                service_provider = plan_data_dict['service_provider']
                authenticator = plan_data_dict['authenticator']
                transport = plan_data_dict['transport']
                permissions = plan_data_dict['permissions']

                dst_broker_ip = plan_data_dict['dst_broker_ip']
                dst_broker_user = plan_data_dict['dst_broker_user']
                dst_broker_auth = plan_data_dict['dst_broker_auth']
                dst_broker_pwd = plan_data_dict['dst_broker_pwd']

                print(f'\nTrying to send "{service_name}" data to secondary broker')

                dst_broker_connection = Client(
                    host=dst_broker_ip,
                    auth=dst_broker_auth,
                    username=dst_broker_user,
                    password=dst_broker_pwd
                )
                dst_broker_connection.login()


                if plan_index == 0:
                    '''
                    Аутентификаторы восстанавливаются сразу все, из тех что поддерживаются, это действие выполняется
                    единожды за план восстановления
                    '''
                    authenticator.set_connection(secondary_broker_connection=dst_broker_connection)
                    created_auths_id, created_groups_id = authenticator.restore()

                service_provider.set_connection(secondary_broker_connection=dst_broker_connection)
                created_provider_id = service_provider.restore()
                created_base_services_id = service_provider.restore_base_services()

                service_pool.set_connection(secondary_broker_connection=dst_broker_connection)
                created_service_pool_id = service_pool.restore(created_base_services_id, created_groups_id)


            except KeyError as k:
                print(f'\nError: no field {k} found at saved data!')

            except Exception as e:
                print(f"\nError: {e}")

            finally:
                try:
                    dst_broker_connection.logout()

                except Exception as e:
                    print(f"\nError: {e}")

    def __load_plan_data(self, plan):

        plan_ending = '.plandata'
        os.makedirs(os.path.dirname(self.packs_path), exist_ok=True)
        plan_full_name = os.path.join(self.packs_path, plan + plan_ending)
        print(f'\nTrying to read saved data from "{plan_full_name}" config file\n')
        plan_data_list = []

        with open(plan_full_name, 'rb') as f:
            plan_data_list = pickle.load(f)

        return plan_data_list

    def run(self, plan_name):

        try:
            plan_data_list = self.__load_plan_data(plan=plan_name)
            print(plan_data_list)

            if (plan_data_list):
                self.__send_data(plan_data_list_param=plan_data_list)
                self.__result = True
            else:
                print('\nError: read data is empty... Skipping!')

        except Exception as e:
            print(f"\nError: {e}")

        finally:
            return self.__result
