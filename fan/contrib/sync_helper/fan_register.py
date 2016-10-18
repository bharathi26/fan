import asyncio
import os
import re
import sys
import yaml

from . import SyncHelper


R = re.compile('%\{(.*?)\}')
P = '%{{{}}}'.format
D = os.path.dirname(__file__)


def env(s):
    for k in R.findall(s):
        s = s.replace(P(k), os.environ.get(k, 'NO_VARIABLE_{}'.format(k)))
    return s


def set_fields(dct):
    for k, v in dct.items():
        if not v and k in os.environ:
            dct[k] = os.environ[k]


def traverse(obj):
    t = type(obj)
    if t == dict:
        return {traverse(k): traverse(v) for k, v in obj.items()}
    elif t == list:
        return list(map(traverse, obj))
    elif t == str:
        return env(obj)
    return obj


def main():
    args = sys.argv[1:]
    assert len(args) == 1, 'Give yaml config name'
    zk_config = os.environ.get('ZK_HOST')
    conf = traverse(yaml.load(open(args[0])))
    print('Call with conf: {}'.format(conf))
    loop = asyncio.get_event_loop()
    h = SyncHelper(zk_config, '/', conf)
    loop.create_task(h.on_start())
    print('run loop')
    loop.run_forever()



if __name__ == '__main__':
    main()