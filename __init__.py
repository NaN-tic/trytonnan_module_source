#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from .module_source import *
from .party import *
from .get_pypi_packages_wizard import *


def register():
    Pool.register(
        ModuleSourceSerie,
        ModuleSource,
        Party,
        GetPypiPackagesPackageList,
        GetPypiPackagesResult,
        module='module_source', type_='model')
    Pool.register(GetPypiPackages,
        module='module_source', type_='wizard')

