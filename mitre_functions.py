import numpy as np
import pandas as pd
from config import raw_data_path, configuration

raw_data = raw_data_path()
config_info = configuration()

class helpers(object):
    """docstring for helpers"""
    def __init__(self):
        return

    def cross_entropy(self, p, q):
        return -np.sum(np.multiply(p,np.log(q+1e-5)))

'''
Testing below:
'''
# f = helpers()
# print(f.load_FAF())

    