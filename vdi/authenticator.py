import sys

sys.path.append('/opt/stackstorm/packs/xrm_openuds/')
import apiclient


class Authenticator:
    perm_class = 'authenticators'

    __primary_broker_connection: apiclient.Client
    __secondary_broker_connection: apiclient.Client
    __pool_groups_list: list
    __pool_assigned_services_list: list
    __user_ids_list: list
    auths_list: list
    data_list: list
    groups_list: list
    assigned_users_list: list
    all_users_list: list
    '''
    legacy_id : created_id
    '''
    __old_group_to_new_ids_dict = {}
    __old_auth_to_new_ids_dict = {}

    def __init__(self, primary_broker, pool_groups_list, pool_assigned_services):

        self.__primary_broker_connection = primary_broker
        self.__pool_groups_list = pool_groups_list
        self.__pool_assigned_services_list = pool_assigned_services
        self.auths_list = self.__get_all_auth_ids()
        self.data_list = self.__get_all_auth_data()
        self.groups_list = self.__get_all_groups()
        self.__user_ids_list = self.__get_assigned_user_ids()
        self.assigned_users_list = self.__get_assigned_users()
        self.all_users_list = self.__get_all_users()

    def restore(self):
        """
        Создание аутентификаторов, групп и пользователей
        Возвращает словарь, в котором парами являются прежние и новосозданные id аутентификаторов
        """

        print(f'\nCreating authenticators')

        for auth in self.data_list:

            legacy_id = auth['id']
            params = self.__get_auth_params_by_type(auth)
            if params is not None:

                created_auth = self.__create_auth_by_type(
                    auth_type=auth.get('type'),
                    params=params)
                if created_auth is not None:

                    self.__old_auth_to_new_ids_dict.update({legacy_id: created_auth})
                    '''
                    Создание групп аутентификатора

                    legacy_group_id: new_group_data
                    '''
                    for group_dict in self.groups_list:
                        if legacy_id in group_dict:

                            group = group_dict.get(legacy_id)
                            new_group_data = self.__restore_auth_groups(
                                created_auth_id=created_auth.get('id'),
                                group_data=group
                            )
                            if new_group_data is not None:

                                self.__old_group_to_new_ids_dict.update({group.get('id'): new_group_data})

                    if self.__old_group_to_new_ids_dict:

                        '''
                        Создание пользователей аутентификатора
                        '''
                        self.__restore_auth_users(
                            created_auth_id=created_auth.get('id'),
                            legacy_auth_id=legacy_id,
                            group_id_comparison_dict=self.__old_group_to_new_ids_dict
                        )
        print("  Authenticator restore summary:")
        print(f"  Created group ids match dict: {self.__old_group_to_new_ids_dict}")
        print(f"  Created auth ids match dict: {self.__old_auth_to_new_ids_dict}")

        return self.__old_auth_to_new_ids_dict, self.__old_group_to_new_ids_dict
    def __restore_auth_groups(self, created_auth_id, group_data):

            print(f'\n  Creating {group_data.get("name")} group')
            print(f'    Group_data: {group_data}')
            params = {
                'auth_id': created_auth_id,
                'name': group_data.get('name'),
                'comments': group_data.get('comments'),
                'state': group_data.get('state'),
                'meta_if_any': group_data.get('meta_if_any'),
                'pools': []
            }
            not_none_group_params = {k: v for k, v in params.items() if v is not None}
            created_auth_group = self.__secondary_broker_connection.create_auth_group(
                **not_none_group_params)
            group_name = group_data.get('name')

            if created_auth_group == '':
                '''
                Получение информации о новосозданной группе
                '''
                pool_groups_list = self.__secondary_broker_connection.list_auth_groups(created_auth_id)
                created_group = next(group for group in pool_groups_list if (
                        group.get('name') == group_name
                ))
                print(f'    Created group result: {created_group}')
                print(f'    Created \"{group_name}\" group successfully')
                return created_group

            else:
                print(f'\n{created_auth_group}')
                return None

    def __restore_auth_users(self, created_auth_id, legacy_auth_id, group_id_comparison_dict):
        """
        Создание пользователей
        """
        print(f'\n    Creating authenticator users')
        for users_dict in self.all_users_list:

            if legacy_auth_id in users_dict:
                users_list = users_dict.get(legacy_auth_id)
                for user in users_list:
                    print(f"        User: {user}")

                    legacy_groups_list = user.get('groups')
                    created_groups_list = []

                    print(f"        Legacy_groups_list: {legacy_groups_list}")
                    print(f"        Group_id_comparison: {group_id_comparison_dict}")

                    if legacy_groups_list is not None:
                        for legacy_group_id in legacy_groups_list:
                            created_group_data = group_id_comparison_dict.get(legacy_group_id)

                            print(
                                f"        Looking for legacy_group_id={legacy_group_id} \
in group_id_comparison={group_id_comparison_dict}")

                            if created_group_data is not None:
                                created_group_id = created_group_data.get('id')

                                print(f"        Found old/new group id match: {legacy_group_id}/{created_group_id}")

                                created_groups_list.append(created_group_id)

                    params = {
                        'auth_id': created_auth_id,
                        'username': user.get('name'),
                        'realname': user.get('real_name'),
                        'comments': user.get('comments'),
                        'state': user.get('state'),
                        'password': user.get('password'),
                        'role': user.get('role'),
                        'groups': created_groups_list,
                    }
                    not_none_user_params = {k: v for k, v in params.items() if v is not None}
                    print(f"        Trying to create user with params: {params}")
                    created_auth_user_result = (
                        self.__secondary_broker_connection.create_auth_user(**not_none_user_params))
                    if not created_auth_user_result:
                        print(f'      Created \"{user.get("name")}\" user successfully\n')
                    else:
                        print(f'!!! Warning: {created_auth_user_result}')

    def __get_all_auth_ids(self):
        auth_id_list = []

        for pool_group in self.__pool_groups_list:
            id_dict = {'auth_id': pool_group['auth_id'], 'group_id': pool_group['id']}
            auth_id_list.append(id_dict)

        return auth_id_list

    def __get_all_auth_data(self):
        data_list = []

        for ids_elem in self.auths_list:
            auth_id = ids_elem['auth_id']
            data_list.append(self.__primary_broker_connection.get_auth(auth_id))

        return data_list

    def __get_all_groups(self):
        groups = []

        for id_elem in self.auths_list:
            group_data = self.__primary_broker_connection.get_auth_group(
                auth_id=id_elem['auth_id'],
                group_id=id_elem['group_id'])
            groups.append({str(id_elem['auth_id']): group_data})

        return groups

    def __get_assigned_user_ids(self):
        user_ids = []

        for id_elem in self.__pool_assigned_services_list:
            owner = id_elem['owner_info']
            auth_id = owner['auth_id']
            user_id = owner['user_id']
            owner_id = {'auth_id': auth_id, 'user_id': user_id}
            user_ids.append(owner_id)

        return user_ids

    def __get_assigned_users(self):
        users_list = []

        for user_id_elem in self.__user_ids_list:
            user_data = self.__primary_broker_connection.get_auth_user(
                auth_id=user_id_elem['auth_id'],
                user_id=user_id_elem['user_id'])
            users_list.append(user_data)

        return users_list

    def __get_all_users(self):
        users_list = []

        for auth in self.auths_list:
            auth_id = auth.get("auth_id")
            auth_users = self.__primary_broker_connection.list_auth_users(auth_id)
            users_list_with_group = []
            for user in auth_users:
                user_id = user.get('id')
                user_data = self.__primary_broker_connection.get_auth_user(
                    auth_id=auth_id,
                    user_id=user_id)
                users_list_with_group.append(user_data)

            users_list.append({auth_id: users_list_with_group})

        return users_list

    def __get_auth_params_by_type(self, auth):
        if auth.get("type") == 'ActiveDirectoryAuthenticator':
            print(f'\n  Creating {auth.get("name")}')

            params = {
                'name': auth.get('name'),
                'label': auth.get('small_name'),
                'host': auth.get('host'),
                'username': auth.get('username'),
                'password': auth.get('password'),
                'ldapBase': auth.get('ldapBase'),
                'comments': auth.get('comments'),
                'tags': auth.get('tags'),
                'priority': auth.get('priority'),
                'ssl': auth.get('ssl'),
                'timeout': auth.get('timeout'),
                'groupBase': auth.get('groupBase'),
                'defaultDomain': auth.get('defaultDomain'),
                'nestedGroups': auth.get('nestedGroups'),
                'visible': auth.get('visible'),
            }
            params = {k: v for k, v in params.items() if v is not None}

        elif auth.get("type") == 'InternalDBAuth':
            print(f'\n  Creating {auth.get("name")}')

            params = {
                'name': auth.get('name'),
                'comments': auth.get('comments'),
                'tags': auth.get('tags'),
                'priority': auth.get('priority'),
                'label': auth.get('small_name'),
                'differentForEachHost': auth.get('differentForEachHost'),
                'reverseDns': auth.get('reverseDns'),
                'acceptProxy': auth.get('acceptProxy'),
                'visible': auth.get('visible')
            }
            params = {k: v for k, v in params.items() if v is not None}

        else:
            print(f'\n!!! Warning: skipping unsupported authenticator {auth.get("name")}')
            params = None

        return params

    def __create_auth_by_type(self, auth_type, params):
        created_auth = None

        if auth_type == 'ActiveDirectoryAuthenticator':
            created_auth = self.__secondary_broker_connection.create_ad_auth(**params)
        elif auth_type == 'InternalDBAuth':
            created_auth = self.__secondary_broker_connection.create_internal_auth(**params)

        print(f'  Created authenticator result: {created_auth}')
        return created_auth

    def set_connection(self, secondary_broker_connection):
        self.__secondary_broker_connection = secondary_broker_connection

    def get_logs(self):

        print('Authenticator [ data ]: ', self.data_list, '\n')
        print('Authenticator [ groups ]: ', self.groups_list, '\n')
        print('Authenticator [ all_users ]: ', self.all_users_list, '\n')
        print('Authenticator [ assigned_users ]: ', self.assigned_users_list, '\n')
