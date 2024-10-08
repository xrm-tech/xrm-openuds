import sys
sys.path.append('/opt/stackstorm/packs/xrm_openuds/')
import apiclient

class ServicePool:

    perm_class= 'servicespools'
    name:str
    id:str
    data_dict:dict
    groups_list:list
    transports_list:list
    assigned_services_list:list
    assignables_list:list
    __secondary_broker_connection: apiclient.Client

    def __init__(self, primary_broker, pool_name):

        self.name= pool_name
        self.id= primary_broker.get_pool_id(pool_name)
        self.data_dict= primary_broker.get_pool(self.id)
        self.groups_list= primary_broker.list_pool_groups(self.id)
        self.transports_list= primary_broker.list_pool_transports(self.id)
        __unfiltered_assigned_services_list= primary_broker.list_pool_assigned_services(self.id)
        self.assigned_services_list= list(filter(self.__filter_valid_services, __unfiltered_assigned_services_list))
        self.assignables_list= primary_broker.list_pool_assignables(self.id)


    def __filter_valid_services(self, assigned_service):
        if (assigned_service['state'] == 'U'):
            return True
        else:
            return False

    def __get_params_by_type(self, created_service_id):
        #TODO пока без анализа типа
        params = {
            'name': self.data_dict.get('name'),
            'service_id': created_service_id,
            'short_name': self.data_dict.get('short_name'),
            'comments': self.data_dict.get('comments'),
            'tags': self.data_dict.get('tags'),
            'visible': self.data_dict.get('visible'),
            'image_id': self.data_dict.get('image_id'),
            'pool_group_id': self.data_dict.get('pool_group_id'),
            'calendar_message': self.data_dict.get('calendar_message'),
            'allow_users_remove': self.data_dict.get('allow_users_remove'),
            'allow_users_reset': self.data_dict.get('allow_users_reset'),
            'ignores_unused': self.data_dict.get('ignores_unused'),
            'show_transports': self.data_dict.get('show_transports'),
            'account_id': self.data_dict.get('account_id'),
            'initial_srvs': self.data_dict.get('initial_srvs'),
            'cache_l1_srvs': self.data_dict.get('cache_l1_srvs'),
            'cache_l2_srvs': self.data_dict.get('cache_l2_srvs'),
            'max_srvs': self.data_dict.get('max_srvs'),
        }
        not_none_auth_params = {k: v for k, v in params.items() if v is not None}
        return not_none_auth_params
    def restore(self, created_base_services_id, created_auth_groups_id):
        '''
        Создание сервис-пулов         TODO: перепроверить.
        '''

        print(f'\nCreating service pool \"{self.name}\"')

        created_service_id = created_base_services_id.get(
            self.data_dict.get('service_id')
        )
        if created_service_id is not None:
            print("  Found required base service")
            params = self.__get_params_by_type(created_service_id)
            created_service_pool = self.__secondary_broker_connection.create_pool(**params)
            created_service_pool_id = created_service_pool.get('id')
            print(f"  Created service pool {self.name}\n  Result: {created_service_pool}")

            '''
            Добавление групп в созданный сервис пул
            '''
            for group in self.groups_list:

                if group.get("id") in created_auth_groups_id:
                    print(f"  Found created group \"{group.get('name')}\" with old id: {group.get('id')}. Trying to attach it to servicepool")
                    created_group_data = created_auth_groups_id.get(group.get('id'))
                    created_group_id = created_group_data.get('id')
                    result = self.__secondary_broker_connection.add_pool_groups(
                        pool_id=created_service_pool_id,
                        group_id=created_group_id
                    )
                    if not result:
                        print(f"  Attached group successfully")
                    else:
                        print(f"  Error when attaching group: {result}")


                else:
                    print(f"  Warning! Not found created group \"{group.get('name')}\" with old id: {group.get('id')}. "
                          f"  Cannot attach it to servicepool...")


            return created_service_pool_id

        else:
            print(f"  Not found required base service with old id: {self.data_dict.get('service_id')} (m.b. not supported?)")

    def set_connection(self, secondary_broker_connection):
        self.__secondary_broker_connection = secondary_broker_connection

    def get_logs(self):

        print('ServicePool [ id ]: ', self.id, '\n')
        print('ServicePool [ data ]: ', self.data_dict, '\n')
        print('ServicePool [ groups ]: ', self.groups_list, '\n')
        print('ServicePool [ transports ]: ', self.transports_list, '\n')
        print('ServicePool [ assigned_services ]: ', self.assigned_services_list, '\n')
        print('ServicePool [ assignables ]: ', self.assignables_list, '\n')
