import argparse
import pickle
import sys, os

# TODO: cleanup from hardcoded path ?
sys.path.append('/opt/stackstorm/packs/xrm_openuds/')

from plan import FailOver

# TODO: cleanup from hardcoded path ?
packs_path= '/opt/stackstorm/packs/saved/'    


def parse_cmdline():
    parser = argparse.ArgumentParser(description='Run xrm openuds failover plan')
    
    parser.add_argument('-n', '--name', dest='name', action='store', type=str, required=True,
                         help='plan name')
                    
    return parser.parse_args()


def main():
    args = parse_cmdline()

    if FailOver.run(packs_path, args.name):
        sys.exit(0)
    else:
        sys.exit(1)
    
    
if __name__ == "__main__":
    main()
