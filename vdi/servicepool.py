import sys
sys.path.append('/opt/stackstorm/packs/xrm_openuds/')
import apiclient

class ServicePool:

    perm_class= 'servicespools'
    name:str
    parent_type:str
    id:str
    os_manager_id:str
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
        self.os_manager_id= self.data_dict.get("osmanager_id")
        self.parent_type= self.data_dict.get("parent_type")
        self.groups_list= primary_broker.list_pool_groups(self.id)
        self.transports_list= primary_broker.list_pool_transports(self.id)
        __unfiltered_assigned_services_list= primary_broker.list_pool_assigned_services(self.id)
        self.assigned_services_list= list(filter(self.__filter_valid_services, __unfiltered_assigned_services_list))
        self.assignables_list= primary_broker.list_pool_assignables(self.id)

    def __attach_groups(self, created_auth_group_ids, created_service_pool_id):
        '''
        Добавление групп в созданный сервис пул
        '''
        for group in self.groups_list:

            if group.get("id") in created_auth_group_ids:
                print(
                    f"  Found created group \"{group.get('name')}\" with old id: {group.get('id')}. Trying to attach it to servicepool")
                created_group_data = created_auth_group_ids.get(group.get('id'))
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
                      f"  Cannot attach it to servicepool... Check __create_transport_by_type in transport")

    def __attach_transports(self, created_transport_ids, created_servicepool_id):
        '''
        Добавление транспортов в созданный сервис пул
        '''
        for trans in self.transports_list:
            old_id = trans.get('id')
            if old_id in created_transport_ids:
                print(
                    f"  Found created transport \"{trans.get('name')}\" with old id: {old_id}. Trying to attach it to servicepool")
                created_trans_id = created_transport_ids.get(old_id)
                result = self.__secondary_broker_connection.add_pool_transports(
                    pool_id=created_servicepool_id,
                    transport_id=created_trans_id
                )

                if not result:
                    print(f"  Attached transport successfully")
                else:
                    print(f"  Error when attaching group: {result}")

            else:
                print(f"  Warning! Not found created transport \"{trans.get('name')}\" with old id: {trans.get('id')}. "
                      f"  Cannot attach it to servicepool... Check if type in transport.__create_transport_by_type")

    def __attach_users_if_required(self, created_servicepool_id, created_user_ids):
        '''
        Назначение сервисов пользователям
        '''
        print(f"  Assigning users to services")
        OVIRT_FIXED = 'oVirtFixedService'
        OVIRT_LINKED = 'oVirtLinkedService'
        
        if self.parent_type == OVIRT_LINKED:
            print("    Not required for this ServicePool type, skipping.")
        else:
            for assigned_service in self.assigned_services_list:
                legacy_owner_id = assigned_service.get('owner_info').get('user_id')
                if legacy_owner_id in created_user_ids:
                    if self.data_dict.get('parent_type') == OVIRT_FIXED:
                        created_pool_assignables = self.__secondary_broker_connection.list_pool_assignables(created_servicepool_id)
                        friendly_name = assigned_service.get('friendly_name')
                        assignable = next((item for item in created_pool_assignables if item['text'] == friendly_name), None)
                        unique_id = assignable.get('id')
                    else:                 
                        unique_id = assigned_service.get('unique_id')
                                    
                    assign_result = self.__secondary_broker_connection.assign_pool_service(
                        pool_id=created_servicepool_id,
                        user_id=created_user_ids.get(legacy_owner_id),
                        assignable_id=unique_id
                    )
                    if assign_result:
                        print(f"  Assigned service successfully for user \"{assigned_service.get('owner')}\"")
                    else:
                        print(f"  Some error when attaching user...")

                else:
                    print(f"    Cant find user with old id {legacy_owner_id}...skipping")

    def __filter_valid_services(self, assigned_service):
        if assigned_service['state'] == 'U':
            return True
        else:
            return False

    def __get_params_by_type(self, created_service_id, created_osmanager_id):
        #TODO пока без анализа типа
        params = self.data_dict.copy()
        params.update({'service_id':created_service_id})
        if created_osmanager_id is not None:
            params.update({"osmanager_id": created_osmanager_id})
        return params

    def restore(self, created_base_service_ids, created_auth_group_ids, created_transport_ids, created_user_ids, created_osmanager_id):
        '''
        Создание сервис-пулов
        '''
        print(f'\nCreating service pool \"{self.name}\"')

        created_service_id = created_base_service_ids.get(
            self.data_dict.get('service_id')
        )
        if created_service_id is not None:
            print("  Found required base service")
            params = self.__get_params_by_type(created_service_id, created_osmanager_id)
            created_service_pool = self.__secondary_broker_connection.create_pool(**params)
            created_service_pool_id = created_service_pool.get('id')
            print(f"  Created service pool {self.name}\n  Result: {created_service_pool}")

            self.__attach_groups(created_auth_group_ids, created_service_pool_id)

            self.__attach_transports(created_transport_ids, created_service_pool_id)

            self.__attach_users_if_required(created_service_pool_id, created_user_ids)

            self.__publicate_if_required(created_service_pool_id)
            
            return created_service_pool_id

        else:
            print(f"  Not found required base service with old id: {self.data_dict.get('service_id')} (m.b. not supported?)")

    def __publicate_if_required(self, pool_id):
        OVIRT_LINKED = "oVirtLinkedService"
        if self.parent_type == OVIRT_LINKED:
            print("  ServicePool publication requested")
            self.__secondary_broker_connection.publish_pool(pool_id)
        else:
            print("  ServicePool publication not required")

    def set_connection(self, secondary_broker_connection):
        self.__secondary_broker_connection = secondary_broker_connection

    def get_logs(self):

        print('ServicePool [ id ]: ', self.id, '\n')
        print('ServicePool [ data ]: ', self.data_dict, '\n')
        print('ServicePool [ groups ]: ', self.groups_list, '\n')
        print('ServicePool [ transports ]: ', self.transports_list, '\n')
        print('ServicePool [ assigned_services ]: ', self.assigned_services_list, '\n')
        print('ServicePool [ assignables ]: ', self.assignables_list, '\n')
