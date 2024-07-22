import base64
import os
import requests
import sys
from st2common.runners.base_action import Action


class RunDelete(Action):

    plan_ending = '.plandata'
    packs_path = '/opt/stackstorm/packs/saved/'

    def run(self, plan_name):

        plan_full_path = os.path.join(self.packs_path, plan_name + self.plan_ending)

        try:
            os.remove(plan_full_path)
            print(f'Successfully removed {plan_full_path}')
            return True

        except OSError as error:
            print(error)
            print("File path can not be removed... Skipping!")
            return False
