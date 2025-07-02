import sys
sys.path.append('/opt/stackstorm/packs/xrm_openuds/')
import apiclient

class OSManager:

    #TODO: perm_class= '...' 
    name:str = None
    type:str = None
    data:dict = None
    __secondary_broker_connection: apiclient.Client

    def __init__(self, primary_broker: apiclient.Client, id:str):
        if id is not None:
            self.data = primary_broker.get_osmanager(id)
            self.name = self.data.get("name")
            self.type = self.data.get("type")

    def set_connection(self, secondary_broker_connection):
        self.__secondary_broker_connection = secondary_broker_connection    

    def restore(self):
        if self.data is not None: 
            print(f'\nCreating OS Manager \"{self.name}\"')

            restored_id = None
            existing_id = self.__return_id_if_exist()
            if existing_id:
                restored_id = existing_id
                print(f"  OS Manager already exist with id: {restored_id}")
            else:
                restored_id = self.__create_new()
                print(f"  OS Manager created with id: {restored_id}")
            return restored_id
        else:
            print("\nOS Manager data is empty, no need to restore")

    def __return_id_if_exist(self):
        osmanagers = self.__secondary_broker_connection.list_osmanagers()
        for osmanager in osmanagers:
            if osmanager.get("type") == self.type and osmanager.get("name") == self.name:
                return osmanager.get("id")
    
    def __create_new(self):
        SUPPORTED_TYPES = {
                "LinuxManager": self.__secondary_broker_connection.create_linux_osmanager,
                "LinRandomPasswordManager": self.__secondary_broker_connection.create_linrandom_osmanager,
                "WindowsManager": self.__secondary_broker_connection.create_windows_osmanager,
                "WinRandomPasswordManager": self.__secondary_broker_connection.create_winrandom_osmanager,
                "WinDomainManager": self.__secondary_broker_connection.create_windomain_osmanager,
        }
        
        if self.type in SUPPORTED_TYPES:
            legacy_id = self.data.get("id")
            self.data.pop("id", None)
            self.data.pop("name", None)
            self.data.pop("deployed_count", None)
            self.data.pop("type_name", None)
            self.data.pop("servicesTypes", None)
            self.data.pop("permission", None)
            result = SUPPORTED_TYPES[self.type](name= self.name, **self.data)
            print(f"  Restore result: {result}")
            return result.get("id")
        
        else:
            print(f"  Warning: Unsupported {self.name} OS Manager type: {self.type}. Skipping...")
            return None

    def get_logs(self):
        print('OS Manager [ data ]: ', self.data, '\n')