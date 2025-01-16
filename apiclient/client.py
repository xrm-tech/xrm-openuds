# -*- coding: utf-8 -*-

# HOSTVM VDI 3.5

from httplib2 import Http
import json
import sys

from dataclasses import asdict

from . import types

class Client:
    _host: str
    _rest_url: str
    _auth: str
    _username: str
    _password: str

    _headers: dict = {}

    def __init__(self, host: str, auth: str, username: str, password: str) -> None:
        self._host = host
        self._auth = auth
        self._username = username
        self._password = password
        self._rest_url = 'https://{}/uds/rest/'.format(self._host)

    def _request(self, endpoint: str, method: str = 'GET', body: str = ''):
        h = Http(disable_ssl_certificate_validation=True)
        resp, content = h.request(uri=self._rest_url + endpoint, method=method, body=body, headers=self._headers)
        return resp, content

    def login(self):
        '''Аутентификация пользователя'''
        parameters = '{ "auth": "' + self._auth + '", "username": "' + self._username + '", "password": "' + self._password + '" }'
        resp, content = self._request('auth/login', 'POST', parameters)
        if resp['status'] != '200':  # Authentication error due to incorrect parameters, bad request, etc...
            raise Exception('Authentication error: {}'.format(resp['status']))
        res = json.loads(content)
        if res['result'] != 'ok':  # Authentication error
            raise Exception('Authentication error: {}'.format(res['result']))
        self._headers['X-Auth-Token'] = res['token']
        return

    def logout(self):
        '''Завершение сессии'''
        resp, content = self._request('auth/logout')
        if resp['status'] != '200':  # Logout error due to incorrect parameters, bad request, etc...
            raise Exception('Authentication error: {}'.format(resp['status']))
        return

#Readers

#Providers
    def list_providers(self):
        '''Получение списка провайдеров'''
        resp, content = self._request('providers')
        if resp['status'] != '200':  # error due to incorrect parameters, bad request, etc...
            raise Exception('Error requesting base services\nresp:{}\ncontent:{}'.format(resp, content))
        return json.loads(content)

    def get_provider(self, provider_id: str):
        '''Получение параметров провайдера'''
        resp, content = self._request('providers/{0}'.format(provider_id))
        if resp['status'] != '200':  # error due to incorrect parameters, bad request, etc...
            raise Exception('Error requesting base services\nresp:{}\ncontent:{}'.format(resp, content))
        return json.loads(content)

    def list_services(self):
        '''Получение всех базовых сервисов'''
        resp, content = self._request('providers/allservices')
        if resp['status'] != '200':  # error due to incorrect parameters, bad request, etc...
            raise Exception('Error requesting base services\nresp:{}\ncontent:{}'.format(resp, content))
        return json.loads(content)

    def list_provider_services(self, provider_id: str):
        resp, content = self._request('providers/{0}/services'.format(provider_id))
        if resp['status'] != '200':  # error due to incorrect parameters, bad request, etc...
            raise Exception('Error requesting base services\nresp:{}\ncontent:{}'.format(resp, content))
        return json.loads(content)

    def get_provider_service(self, provider_id: str, service_id: str):
        '''Получение параметров базового сервиса'''
        resp, content = self._request('providers/{0}/services/{1}'.format(provider_id, service_id))
        if resp['status'] != '200':  # error due to incorrect parameters, bad request, etc...
            raise Exception('Error requesting pools: response: {}, content: {}'.format(resp, content))
        return json.loads(content)

#Authenticators
    def list_auths(self):
        '''Получение списка аутентификаторов'''
        resp, content = self._request('authenticators')
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def get_auth(self, auth_id: str):
        '''Получение параметров аутентификатора'''
        resp, content = self._request('authenticators/{}'.format(auth_id))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def list_auth_groups(self, auth_id: str):
        '''Получение списка групп в аутентификаторе'''
        resp, content = self._request('authenticators/{}/groups'.format(auth_id))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def get_auth_group(self, auth_id: str, group_id: str):
        '''Получение параметров группы аутентификатора'''
        resp, content = self._request('authenticators/{}/groups/{}'.format(auth_id, group_id))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def list_auth_users(self, auth_id: str):
        '''Получение списка пользователей в аутентификаторе'''
        resp, content = self._request('authenticators/{}/users'.format(auth_id))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def get_auth_user(self, auth_id: str, user_id: str):
        '''Получение параметров пользователя в аутентификаторе'''
        resp, content = self._request('authenticators/{}/users/{}'.format(auth_id, user_id))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def list_auth_group_users(self, auth_id: str, group_id: str):
        '''Пользователи группы'''
        resp, content = self._request('authenticators/{}/groups/{}/users'.format(auth_id, group_id))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

#OS Managers
    def list_osmanagers(self):
        '''Получение списка менеджеров ОС'''
        resp, content = self._request('osmanagers')
        if resp['status'] != '200':  # error due to incorrect parameters, bad request, etc...
            raise Exception('Error requesting osmanagers\nresp:{}\ncontent:{}'.format(resp, content))
        return json.loads(content)

    def get_osmanager(self, osmanager_id: str):
        '''Получение параметров менеджера ОС'''
        resp, content = self._request('osmanagers/{}'.format(osmanager_id))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

#Transports

    def list_transports(self):
        '''Получение списка созданных транспортов'''
        resp, content = self._request('transports')
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def get_transport(self, transport_id: str):
        '''Получение параметров транспорта'''
        resp, content = self._request('transports/{}'.format(transport_id))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

#Pools
    def list_pools(self):
        '''Получение списка сервис-пулов и их параметров'''
        resp, content = self._request('servicespools/overview')
        if resp['status'] != '200':  # error due to incorrect parameters, bad request, etc...
            raise Exception('Error requesting pools: {}'.format(resp['status']))
        return json.loads(content)

    def get_pool_id(self, name: str):
        '''Получение id сервис-пула по имени'''
        res = self.list_pools()
        for r in res:
            if r['name'] == name:
                return r['id']
        return None

    def get_pool(self, pool_id: str):
        '''Получение параметров сервис-пула'''
        resp, content = self._request('servicespools/{}'.format(pool_id))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def list_pool_groups(self, pool_id: str):
        '''Получение списка добавленных в пул групп'''
        resp, content = self._request('servicespools/{}/groups'.format(pool_id))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def list_pool_transports(self, pool_id: str):
        '''Получение списка добавленных в пул транспортов'''
        resp, content = self._request('servicespools/{}/transports'.format(pool_id))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def list_pool_assigned_services(self, pool_id: str):
        '''Получение списка назначенных пользователям сервисов пула'''
        resp, content = self._request('servicespools/{}/services'.format(pool_id))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def list_pool_cached_services(self, pool_id: str):
        '''Получение списка находящихся в кэше сервисов пула'''
        resp, content = self._request('servicespools/{}/cache'.format(pool_id))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def list_pool_publications(self, pool_id: str):
        '''Получение списка публикаций пула'''
        resp, content = self._request('servicespools/{}/publications'.format(pool_id))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def list_pool_changelog(self, pool_id: str):
        '''Получение журнала изменений публикаций пула'''
        resp, content = self._request('servicespools/{}/changelog'.format(pool_id))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def list_pool_assignables(self, pool_id: str):
        '''Получение списка назначаемых сервисов пула'''
        resp, content = self._request('servicespools/{}/listAssignables'.format(pool_id))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

#Config

    def get_config(self):
        '''Get system config'''
        resp, content = self._request('config')
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def get_permissions(self, cls: str, uuid: str):
        '''Get permissions for an object

        Args:
            cls: object class, valid type is one of the following
                {
                    'providers',
                    'service',
                    'authenticators',
                    'osmanagers',
                    'transports',
                    'networks',
                    'servicespools',
                    'calendars',
                    'metapools',
                    'accounts',
                }
            uuid: object id
        '''
        resp, content = self._request('permissions/{}/{}'.format(cls, uuid))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def list_actor_tokens(self):
        ''''''
        resp, content = self._request('actortokens')
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

#Writers

#Providers

    def create_static_provider(self, name: str, comments: str='', tags: list=[], config: str=''):
        '''Создание сервис-провайдера Static IP Machines'''
        data = {
            'name': name,
            'type': 'PhysicalMachinesServiceProvider',
            'comments': comments,
            'tags': tags,
            'config': config,
        }
        resp, content = self._request('providers', 'PUT', body=json.dumps(data))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def create_staticmultiple_service(
        self,
        provider_id: str,
        name: str,
        comments: str='',
        tags: list=[],
        iplist: list=[],
        token: str='',
        port: int=0,
        skipTimeOnFailure: int=0,
        maxSessionForMachine: int=0,
        lockByExternalAccess: bool=False,
    ):
        '''Создание базового сервиса Static Multiple IP'''
        data = {
            'name': name,
            'type': 'IPMachinesService',
            'comments': comments,
            'data_type': 'IPMachinesService',
            'tags': tags,
            'proxy_id': '-1',
            'ipList': iplist,
            'token': token,
            'port': port,
            'skipTimeOnFailure': skipTimeOnFailure,
            'maxSessionForMachine': maxSessionForMachine,
            'lockByExternalAccess': lockByExternalAccess,
        }
        resp, content = self._request(
            'providers/{0}/services'.format(provider_id),
            'PUT',
            body=json.dumps(data)
        )
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def create_ovirt_provider(self, name: str, **kwargs):
        '''Создание сервис-провайдера oVirt/RHEV Platform'''
        data = asdict(types.oVirtPlatform(name=name, **kwargs))
        resp, content = self._request('providers', 'PUT', body=json.dumps(data))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def create_ovirtlinked_service(self, provider_id: str, name: str, **kwargs):
        '''Создание базового сервиса oVirt/RHEV Linked Clone'''
        data = asdict(types.oVirtLinkedService(name=name, **kwargs))
        resp, content = self._request(
            'providers/{0}/services'.format(provider_id),
            'PUT',
            body=json.dumps(data)
        )
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

#Authenticators

    def create_ad_auth(
        self,
        name: str,
        label: str,
        host: str,
        username: str,
        password: str,
        ldapBase: str,
        comments: str='',
        tags: list=[],
        priority: int=1,
        ssl: bool=False,
        timeout: int=10,
        groupBase: str='',
        defaultDomain: str='',
        nestedGroups: str=False,
        visible: bool=True
    ):
        '''Создание аутентификатора Active Directory'''
        data = {
            'name': name,
            'small_name': label,
            'host': host,
            'username': username,
            'password': password,
            'ldapBase': ldapBase,
            'comments': comments,
            'tags': tags,
            'priority': priority,
            'ssl': ssl,
            'timeout': str(timeout),
            'groupBase': groupBase,
            'defaultDomain': defaultDomain,
            'nestedGroups': nestedGroups,
            'data_type': 'ActiveDirectoryAuthenticator',
            'visible': visible
        }
        resp, content = self._request('authenticators', 'PUT', body=json.dumps(data))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def create_internal_auth(
        self,
        name: str,
        comments: str,
        tags: list,
        priority: int,
        label: str,
        differentForEachHost: bool,
        reverseDns: bool,
        acceptProxy: bool,
        visible: bool
    ):
        '''Создание аутентификатора Internal Database'''
        data = {
            'name': name,
            'comments': comments,
            'tags': tags,
            'priority': str(priority),
            'small_name': label,
            'differentForEachHost': differentForEachHost,
            'reverseDns': reverseDns,
            'acceptProxy': acceptProxy,
            'data_type': 'InternalDBAuth',
            'visible': visible
        }
        resp, content = self._request('authenticators', 'PUT', body=json.dumps(data))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def create_regexldap_auth(
        self,
        name: str,
        label: str,
        host: str,
        username: str,
        password: str,
        ldapBase: str,
        comments: str='',
        tags: list=[],
        priority: int=1,
        port: int=389,
        ssl: bool=False,
        timeout: int=10,
        userClass: str='posixAccount',
        userIdAttr: str='uid',
        groupNameAttr: str='cn',
        userNameAttr: str='uid',
        altClass: str='',
        visible: bool=True
    ):
        '''Создание аутентификатора Regex LDAP'''
        data = {
            'name': name,
            'small_name': label,
            'host': host,
            'username': username,
            'password': password,
            'ldapBase': ldapBase,
            'comments': comments,
            'tags': tags,
            'priority': priority,
            'port': str(port),
            'ssl': ssl,
            'timeout': str(timeout),
            'userClass': userClass,
            'userIdAttr': userIdAttr,
            'groupNameAttr': groupNameAttr,
            'userNameAttr': userNameAttr,
            'altClass': altClass,
            'data_type': 'RegexLdapAuthenticator',
            'visible': visible
        }
        resp, content = self._request('authenticators', 'PUT', body=json.dumps(data))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def create_simpleldap_auth(
        self,
        name: str,
        label: str,
        host: str,
        username: str,
        password: str,
        ldapBase: str,
        comments: str='',
        tags: list=[],
        priority: int=1,
        port: int=389,
        ssl: bool=False,
        timeout: int=10,
        userClass: str='posixAccount',
        groupClass: str='posixGroup',
        userIdAttr: str='uid',
        groupIdAttr: str='cn',
        memberAttr: str='memberUid',
        userNameAttr: str='uid',
        visible: bool=True
    ):
        '''Создание аутентификатора Simple LDAP'''
        data = {
            'name': name,
            'small_name': label,
            'host': host,
            'username': username,
            'password': password,
            'ldapBase': ldapBase,
            'comments': comments,
            'tags': tags,
            'priority': priority,
            'port': str(port),
            'ssl': ssl,
            'timeout': str(timeout),
            'userClass': userClass,
            'groupClass': groupClass,
            'userIdAttr': userIdAttr,
            'groupIdAttr': groupIdAttr,
            'memberAttr': memberAttr,
            'userNameAttr': userNameAttr,
            'data_type': 'SimpleLdapAuthenticator',
            'visible': visible
        }
        resp, content = self._request('authenticators', 'PUT', body=json.dumps(data))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def create_saml_auth(
        self,
        name: str,
        label: str,
        privateKey: str,
        serverCertificate: str,
        idpMetadata: str,
        userNameAttr: str,
        groupNameAttr: str,
        realNameAttr: str,
        comments: str='',
        tags: list=[],
        priority: int=1,
        entityID: str='',
        usePassword: bool=False,
        pwdAttr: str='',
        visible: bool=True
    ):
        '''Создание аутентификатора SAML'''
        data = {
            'name': name,
            'small_name': label,
            'privateKey': privateKey,
            'serverCertificate': serverCertificate,
            'idpMetadata': idpMetadata,
            'userNameAttr': userNameAttr,
            'groupNameAttr': groupNameAttr,
            'realNameAttr': realNameAttr,
            'comments': comments,
            'tags': tags,
            'priority': priority,
            'entityID': entityID,
            'usePassword': usePassword,
            'pwdAttr': pwdAttr,
            'data_type': 'SAML20Authenticator',
            'visible': visible
        }
        resp, content = self._request('authenticators', 'PUT', body=json.dumps(data))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def create_auth_group(
        self,
        auth_id: str,
        name: str,
        comments: str = '',
        state: str = 'A',
        meta_if_any: bool = False,
        pools: list = []
    ):
        '''Добавление группы в аутентификатор'''
        data = {
            'type': 'group',
            'name': name,
            'comments': comments,
            'state': state,
            'meta_if_any': meta_if_any,
            'pools': pools
        }
        resp, content = self._request(
            'authenticators/{}/groups'.format(auth_id),
            'PUT',
            body=json.dumps(data)
        )
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def create_auth_user(
        self,
        auth_id: str,
        username: str,
        realname: str = '',
        comments: str = '',
        state: str = 'A',
        password: str = '',
        role: str = 'user',
        groups: list = [],
    ):
        '''Добавление пользователя в аутентификатор'''
        role = role.lower()
        valid_role = {'admin', 'staff', 'user'}
        staff_member = False
        is_admin = False
        if role not in valid_role:
            raise ValueError('Role must be one of: %s' % valid_role)
        if role == 'admin':
            is_admin = True 
            staff_member = True
        elif role == 'staff':
            staff_member = True
        data = {
            'name': username,
            'real_name': realname,
            'comments': comments,
            'state': state,
            'staff_member': staff_member,
            'is_admin': is_admin,
            'groups': groups,
            'role': role,
        }
        if password:
            data['password'] = password
        resp, content = self._request(
            'authenticators/{}/users'.format(auth_id),
            'PUT',
            body=json.dumps(data)
        )
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        # print("Successfully added user {} for auth {}".format(username, auth_id))
        return json.loads(content)

#OS Managers

    def create_linux_osmanager(self, name: str, **kwargs):
        '''Создание менеджера ОС Linux'''
        data = asdict(types.LinuxManager(name=name, **kwargs))
        resp, content = self._request('osmanagers', 'PUT', body=json.dumps(data))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def create_linrandom_osmanager(self, name: str, **kwargs):
        '''Создание менеджера ОС Linux Random Password'''
        data = asdict(types.LinRandomPasswordManager(name=name, **kwargs))
        resp, content = self._request('osmanagers', 'PUT', body=json.dumps(data))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def create_windows_osmanager(self, name: str, **kwargs):
        '''Создание менеджера ОС Windows Basic'''
        data = asdict(types.WindowsManager(name=name, **kwargs))
        resp, content = self._request('osmanagers', 'PUT', body=json.dumps(data))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def create_winrandom_osmanager(self, name: str, **kwargs):
        '''Создание менеджера ОС Windows Random Password'''
        data = asdict(types.WinRandomPasswordManager(name=name, **kwargs))
        resp, content = self._request('osmanagers', 'PUT', body=json.dumps(data))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def create_windomain_osmanager(self, name: str, **kwargs):
        '''Создание менеджера ОС Windows Domain'''
        data = asdict(types.WinDomainManager(name=name, **kwargs))
        resp, content = self._request('osmanagers', 'PUT', body=json.dumps(data))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

#Transports

    # def create_transport(
    #     self,
    #     name: str,
    #     trans_type: str,
    #     tags: list = [],
    #     comments: str = '',
    #     priority: int = 1,
    #     nets_positive: bool = True,
    #     label: str = '',
    #     networks: list = [],
    #     allowed_oss: list = [],
    #     pools: list = [],
    #     **kwargs
    # ):
    #     '''Create transport
        
    #     Args:
    #         trans_type - transport type, valid values are:
    #             HTML5RATransport
    #             HTML5RDPTransport
    #             PCoIPTransport
    #             RATransport
    #             TRATransport
    #             RDPTransport
    #             TSRDPTransport
    #             SPICETransport
    #             TSSPICETransport
    #             URLTransport
    #             X2GOTransport
    #             TX2GOTransport
        
    #     **kwargs
    #         keyword arguments, transport type dependent
    #     '''
    #     data = {}
    #     resp, content = self._request(
    #         'transports',
    #         'PUT',
    #         body=json.dumps(data)
    #     )
    #     if resp['status'] != '200':
    #         raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
    #     return json.loads(content)

    def create_rdpdirect_transport(self, name: str, **kwargs):
        '''Create RDP direct transport'''
        data = asdict(types.RDPTransport(name=name, **kwargs))
        resp, content = self._request(
            'transports',
            'PUT',
            body=json.dumps(data)
        )
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def create_rdptunnel_transport(self, name: str, tunnelServer: str, **kwargs):
        '''Create RDP tunnel transport'''
        if not tunnelServer:
            raise ValueError('tunnelServer cannot be empty, valid format is HOST:PORT')
        data = asdict(types.TSRDPTransport(name=name, tunnelServer=tunnelServer, **kwargs))
        resp, content = self._request(
            'transports',
            'PUT',
            body=json.dumps(data)
        )
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    # def create_x2go_transport(
    #     self,
    #     name: str,
    #     tags: list = [],
    #     comments: str = '',
    #     priority: int = 1,
    #     nets_positive: bool = True,
    #     label: str = '',
    #     networks: list = [],
    #     allowed_oss: list = [],
    #     pools: list = []
    # ):
    #     '''Create X2GO direct transport'''
    #     data = {
    #         'name': name,
    #         'tags': tags,
    #         'comments': comments,
    #         'priority': priority,
    #         'nets_positive': nets_positive,
    #         'label': label,
    #         'networks': networks,
    #         'allowed_oss': allowed_oss,
    #         'pools': pools,
    #         'type': 'X2GOTransport',
    #         # TODO: transport config
    #     }
    #     resp, content = self._request(
    #         'transports',
    #         'PUT',
    #         body=json.dumps(data)
    #     )
    #     if resp['status'] != '200':
    #         raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
    #     return json.loads(content)

    def add_transport_networks(self, network_id: str, transport_id: str):
        '''Add network to a transport'''
        data = {'id': network_id}
        resp, content = self._request(
            'transports/{}/networks'.format(transport_id),
            'PUT',
            body=json.dumps(data)
        )
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        # print("Successfully added transport {} for network {}".format(transport_id, network_id))
        return

#Pools

    def create_pool(
        self,
        name: str,
        service_id: str,
        osmanager_id: str = None,
        short_name: str = '',
        comments: str = '',
        tags: list = [],
        visible: bool = True,
        image_id: str = '-1',
        pool_group_id: str = '-1',
        calendar_message: str = '',
        allow_users_remove: bool = True,
        allow_users_reset: bool = True,
        ignores_unused: bool = False,
        show_transports: bool = True,
        account_id: str = '-1',
        initial_srvs: int = 0,
        cache_l1_srvs: int = 0,
        cache_l2_srvs: int = 0,
        max_srvs: int = 0,
    ):
        '''Создание нового пула'''
        if image_id is None: image_id = '-1'
        if pool_group_id is None: pool_group_id = '-1'
        if account_id is None: account_id = '-1'

        data = {
            'name': name,
            'short_name': short_name,
            'comments': comments,
            'tags': tags,
            'service_id': service_id,
            'osmanager_id': osmanager_id,
            'image_id': image_id,
            'pool_group_id': pool_group_id,
            'initial_srvs': initial_srvs,
            'cache_l1_srvs': cache_l1_srvs,
            'cache_l2_srvs': cache_l2_srvs,
            'max_srvs': max_srvs,
            'show_transports': show_transports,
            'visible': visible,
            'allow_users_remove': allow_users_remove,
            'allow_users_reset': allow_users_reset,
            'ignores_unused': ignores_unused,
            'account_id': account_id,
            'calendar_message': calendar_message
        }

        resp, content = self._request('servicespools','PUT', body=json.dumps(data))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        #r = json.loads(content)
        #print("Correctly created {} with id {}".format(r['name'], r['id']))
        #print("The record created was: {}".format(r))
        return json.loads(content)

    def delete_pool(self, pool_id: str):
        '''Удаление сервис-пула'''
        # Method MUST be DELETE
        resp, content = self._request('servicespools/{}'.format(pool_id), 'DELETE')
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        #print("Correctly deleted {}".format(pool_id))
        return

    def modify_pool(self, pool_id: str, max_services: int):
        '''Изменение параметров пула

        В качестве примера для демонстрации реализовано изменение максимального количества ВРС в пуле
        '''
        # TODO: pool paramaters
        resp, content = self._request('servicespools/{}'.format(pool_id))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        data = json.loads(content)
        data['max_srvs'] = max_services
        resp, content = self._request('servicespools/{}'.format(pool_id), 'PUT', body=json.dumps(data))
        if resp['status'] != '200':
            print("Error in request: \n-------------------\n{}\n{}\n----------------".format(resp, content))
            sys.exit(1)
        #r = json.loads(content)
        #print("Successfully modified pool id: {} with data:\n{}".format(pool_id, r))
        return json.loads(content)

    def publish_pool(self, pool_id: str):
        '''Публикация пула'''
        resp, content = self._request('servicespools/{}/publications/publish'.format(pool_id))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

    def add_pool_groups(self, pool_id: str, group_id: str):
        '''Добавление в пул группы доступа'''
        data = {'id': group_id}
        resp, content = self._request(
            'servicespools/{}/groups'.format(pool_id),
            'PUT',
            body=json.dumps(data)
        )
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        #print("Successfully added group {} for pool {}".format(group_id, pool_id))
        return json.loads(content)

    def add_pool_transports(self, pool_id: str, transport_id: str):
        '''Добавление в пул транспорта'''
        data = {'id': transport_id}
        resp, content = self._request(
            'servicespools/{}/transports'.format(pool_id),
            'PUT',
            body=json.dumps(data)
        )
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        #print("Successfully added transport {} for pool {}".format(transport_id, pool_id))
        return json.loads(content)

    def assign_pool_service(self, pool_id: str, user_id: str, assignable_id: str):
        '''Assign pool service to a user'''
        data = {
            'user_id': user_id,
            'assignable_id': assignable_id,
        }
        resp, content = self._request(
            'servicespools/{}/createFromAssignable'.format(pool_id),
            body=json.dumps(data)
        )
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)

#Config

    def set_permissions(self, cls: str, uuid: str, perm_type: str, entity_id: str, perm: int):
        '''Set permissions for an object

        Args:
            cls: object class, valid type is one of the following
                {
                    'providers',
                    'service',
                    'authenticators',
                    'osmanagers',
                    'transports',
                    'networks',
                    'servicespools',
                    'calendars',
                    'metapools',
                    'accounts',
                }
            uuid: object id
            perm_type: must be 'users' or 'groups'
            entity_id: user or group id
            perm: permissions
                32 - read
                64 - manage
        '''
        if perm_type not in ['users', 'groups']:
            raise ValueError('Invalid permission type: {}'.format(perm_type))
        perms = {
            '32': '1',
            '64': '2'
        }
        data = {'perm': perms.get(str(perm), None)}
        if not data['perm']:
            raise ValueError('Invalid permission: {}'.format(perm))
        resp, content = self._request('permissions/{}/{}/{}/add/{}'.format(cls, uuid, perm_type, entity_id), 'PUT', body=json.dumps(data))
        if resp['status'] != '200':
            raise Exception('Error in request: \n-------------------\n{}\n{}\n----------------'.format(resp, content))
        return json.loads(content)
