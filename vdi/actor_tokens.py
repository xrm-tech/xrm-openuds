import sys
sys.path.append('/opt/stackstorm/packs/xrm_openuds/')
import apiclient

class ActorTokens:
    __tokens: list
    __secondary_broker_connection: apiclient.Client

    def __init__(self, primary_broker: apiclient.Client):
        self.__tokens = primary_broker.list_actor_tokens()

    def set_connection(self, secondary_broker_connection):
        self.__secondary_broker_connection = secondary_broker_connection    

    def restore(self):
        print(f'\nCreating actor tokens')
        existing_tokens = self.__secondary_broker_connection.list_actor_tokens()
        if self.__tokens: 
            for token in self.__tokens:
                if not any(existing_token['id'] == token['id'] for existing_token in existing_tokens):
                    print(f"  Token with id {token.get('id')} not found, restoring...")
                    host_value = token["host"]
                    host_parts = host_value.split("-") 
                    mac = host_parts[1].strip()
                    token_id = token.get("id")
                    token.pop("id", None)
                    result = self.__secondary_broker_connection.create_actor_token(mac=mac,token=token_id, **token)
                    print(f"  Result: {result}")
                else:
                    print(f"  Token with id {token.get('id')} already exist, no need to create")
        else:
            print("  Empty data, nothing to restore. Skipping...")
    
    def get_logs(self):
        print('Actor Tokens [ tokens ]: ', self.__tokens, '\n')