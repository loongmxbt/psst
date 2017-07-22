import os
import logging

import pandas as pd
import traitlets as t
import traittypes as tt
import ipywidgets as ipyw

from . import matpower
from .generator import Generator

logger = logging.getLogger(__name__)

KEYS = (
    'generator_bus',
    'initial_real_power',
    'initial_imag_power',
    'maximum_imag_power',
    'minimum_imag_power',
    'generator_voltage',
    'base_power',
    'initial_status',
    'maximum_real_power',
    'maximum_imag_power',
    # 'PC1',
    # 'PC2',
    # 'QC1MIN',
    # 'QC1MAX',
    # 'QC2MIN',
    # 'QC2MAX',
    # 'RAMP_AGC',
    # 'RAMP_10',
    # 'RAMP_30',
    # 'RAMP_Q',
    # 'APF',
    # 'MU_PMAX',
    # 'MU_PMIN',
    # 'MU_QMAX',
    # 'MU_QMIN'
)


class Case(t.HasTraits):

    name = t.Unicode()
    gen = tt.DataFrame()
    gencost = tt.DataFrame()
    bus = tt.DataFrame()
    load = tt.DataFrame()
    branch = tt.DataFrame()
    bus_name = t.List(t.Unicode())
    gen_name = t.List(t.Unicode())
    branch_name = t.List(t.Unicode())
    _attributes = t.List(t.Unicode())

    def __init__(self, filename, *args, **kwargs):

        super(Case, self).__init__(*args, **kwargs)

        if filename.endswith('.m'):
            self._attributes = list()
            self.read_matpower(filename)

    def read_matpower(self, filename, auto_assign_names=True, fill_loads=True, remove_empty=True, reset_generator_status=True):

        with open(os.path.abspath(filename)) as f:
            string = f.read()

        gen_list = list()
        for attribute in matpower.find_attributes(string):
            _list = matpower.parse_file(attribute, string)
            if attribute == 'gen':
                for row in _list:
                    model = Generator(**dict(zip(KEYS, row)))
                    s = pd.Series(model._trait_values)
                    gen_list.append(s)

        self.gen = pd.DataFrame(gen_list)
        self.gen['name'] = ['GenCo{i}'.format(i=i) for i in range(0, len(self.gen['name']))]


class CaseView(ipyw.VBox):

    case = t.Instance(Case)

    def __init__(self, case, *args, **kwargs):

        self.case = case

        super(CaseView, self).__init__(**kwargs)

        self.generator_names = ipyw.Dropdown(
            options=list(self.case.gen.index)
        )

        children = [
            self.generator_names,
        ]

        self.children = children
