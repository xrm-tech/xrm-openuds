import argparse
import os
import sys

plan_ending = '.plandata'
# TODO: cleanup from hardcoded path ?
packs_path = '/opt/stackstorm/packs/saved/'    


def parse_cmdline():
    parser = argparse.ArgumentParser(description='Run xrm openuds failover plan')
    
    parser.add_argument('-n', '--name', dest='name', action='store', type=str, required=True,
                         help='plan name')
                    
    return parser.parse_args()


def main():
    args = parse_cmdline()

    plan_full_path = os.path.join(packs_path, args.name + plan_ending)

    try:
        os.remove(plan_full_path)
        print(f'Successfully removed {plan_full_path}')
        os.exit(0)

    except OSError as error:
        sys.stderr.write("{}\nFile path can not be removed... Skipping!\n" % error)
        os.exit(1)
    
    
if __name__ == "__main__":
    main()
