#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from trytond.model import fields
from trytond.pyson import Eval
from trytond.pool import PoolMeta

__all__ = ['Party']
__metaclass__ = PoolMeta

#from party.party import STATES, DEPENDS
STATES = {
    'readonly': ~Eval('active', True),
}
DEPENDS = ['active']


class Party:
    __name__ = 'party.party'

    pypi_author = fields.Char('Pypi Author', states=STATES, depends=DEPENDS,
            help="The string used for this party in the 'Author' field")
    bitbucket_user = fields.Char('Bitbucket User', states=STATES,
            depends=DEPENDS)
    module_sources = fields.One2Many('ir.module.source', 'author', 'Sources',
            states=STATES, depends=DEPENDS)

