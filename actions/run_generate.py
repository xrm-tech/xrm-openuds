import pickle
import sys, os

sys.path.append(os.path.abspath('.'))
sys.path.append('/opt/stackstorm/packs/xrm_openuds/')
from st2common.runners.base_action import Action
from plan import Generate


class RunGenerate(Action):
    __result= None
    packs_path= '/opt/stackstorm/packs/saved/'    

    
    def run(self, plan_name):

        return Generate.run(self.config, self.packs_path, plan_name)
