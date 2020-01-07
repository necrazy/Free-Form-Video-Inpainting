# import sys
# import os.path as op
# sys.path.append(op.join(op.pardir, __file__))  # noqa

import re
import argparse
from collections import OrderedDict

import torch


def parse_args():
    parser = argparse.ArgumentParser(
        """
        IMPORTANT NOTE: to run this script, you need to put it under src/ instead of src/scripts
        due to some unpickling issues of torch.load()

        This script is to modify a checkpoint saved in our previous "FVI with Gated Conv" repository.
        1. Add a "use_skip_connection=True" tag in the "arch/args/opts" entry in the config json.
        2. Replace names of nn modules that has been changed during the LGTSM development.
        """
    )
    parser.add_argument('--src', type=str, required=True)
    parser.add_argument('--dst', type=str, required=True)
    args = parser.parse_args()
    return args


def rename_conv_to_featureConv(checkpoint):
    state_dict = checkpoint['state_dict']
    # modified_keys = [k for k, v in state_dict.keys() if 'temporal_discriminator' in k and '.conv.' in k]
    new_state_dict = OrderedDict([
        (k.replace('.conv.', '.featureConv.'), v)
        if 'temporal_discriminator' in k and '.conv.' in k else (k, v)
        for k, v in state_dict.items()
    ])
    new_metadata = OrderedDict([
        (re.sub(r'.conv$', '.featureConv', k), v)
        if 'temporal_discriminator' in k and '.conv' in k else (k, v)
        for k, v in state_dict._metadata.items()
    ])
    setattr(new_state_dict, '_metadata', new_metadata)
    checkpoint['state_dict'] = new_state_dict
    return checkpoint


def main():
    args = parse_args()
    breakpoint()
    checkpoint = torch.load(args.src)
    new_checkpoint = rename_conv_to_featureConv(checkpoint)
    new_checkpoint['config']['arch']['args']['opts']['use_skip_connection'] = True
    torch.save(new_checkpoint, args.dst)


if __name__ == '__main__':
    main()
