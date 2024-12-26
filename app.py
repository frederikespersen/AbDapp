from src.session import run
from src.layouts import page_template

# ················································································· #

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--debug', help='Debug Mode',
                    action='store_true', default=False)
args = parser.parse_args()

# ················································································· #

run(args.debug)