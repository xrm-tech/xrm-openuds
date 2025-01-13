import argparse
import sys, os
import yaml

# TODO: cleanup from hardcoded path ?
sys.path.append('/opt/stackstorm/packs/xrm_openuds/')
from plan import Generate

# TODO: cleanup from hardcoded path ?
packs_path= '/opt/stackstorm/packs/saved/'    


def parse_cmdline():
    parser = argparse.ArgumentParser(description='Generate xrm openuds plan')
    
    parser.add_argument('-c', '--config', dest='config', action='store', type=str, required=True,
                         help='YAML config file')

    parser.add_argument('-n', '--name', dest='name', action='store', type=str, required=True,
                         help='plan name')
                    
    return parser.parse_args()


def main():
    args = parse_cmdline()

    config = None
    with open(args.config, 'r') as stream:
        config = yaml.safe_load(stream)

    if Generate.run(config, packs_path, args.name):
        sys.exit(0)
    else:
        sys.exit(1)
    
    
if __name__ == "__main__":
    main()


