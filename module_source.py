#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Bool, Eval

__all__ = ['ModuleSourceSerie', 'ModuleSource']

PYPI_STATES = {
    'required': Bool(Eval('pypi_package_name')),
    }
PYPI_DEPENDS = ['pypi_package_name']

SCM_STATES = {
    'required': Bool(Eval('scm_url')),
    }
SCM_DEPENDS = ['scm_url']

PM_STATES = {
    'required': Bool(Eval('pm_url')),
    }
PM_DEPENDS = ['pm_url']


class ModuleSourceSerie(ModelSQL, ModelView):
    """Module Source Serie"""
    __name__ = 'ir.module.source.serie'

    name = fields.Char('Name', required=True)
    stable = fields.Boolean('Stable')

    @classmethod
    def __setup__(cls):
        super(ModuleSourceSerie, cls).__setup__()
        cls._sql_constraints = [
            ('name_uniq', 'UNIQUE(name)',
                     'The name of the Module Source Series must be unique!')
        ]
        cls._order.insert(0, ('name', 'ASC'))


class ModuleSource(ModelSQL, ModelView):
    """Module Source"""
    __name__ = 'ir.module.source'

    name = fields.Char('Name', required=True)
    author = fields.Many2One('party.party', 'Author', select=True)
    server_serie = fields.Many2One('ir.module.source.serie', 'Server Serie',
            required=True, select=True)
    pypi_package_name = fields.Char('Package Name')
    pypi_release_version = fields.Char('Version', states=PYPI_STATES,
            depends=PYPI_DEPENDS)
    pypi_release_url = fields.Char('Package URL', states=PYPI_STATES,
            depends=PYPI_DEPENDS)
    scm_url = fields.Char('SCM URL')
    scm_type = fields.Selection([
        ('git', 'Git'),
        ('hg', 'Mercurial'),
        ], string='SCM Type', translate=False, states=SCM_STATES,
            depends=SCM_DEPENDS)
    scm_branch = fields.Char('SCM Branch', states=SCM_STATES,
            depends=SCM_DEPENDS)
    pm_url = fields.Char('PM URL')
    pm_type = fields.Selection([
        ('github', 'GitHub.com'),
        ('bitbucket', 'BitBucket'),
        ], string='PM Type', translate=False, states=PM_STATES,
            depends=PM_DEPENDS)
    used = fields.Boolean('Used')
    original_source = fields.Many2One('ir.module.source', 'Original Source')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('deprecated', 'Deprecated'),
        ], 'State', readonly=True, sort=False)

    @classmethod
    def __setup__(cls):
        super(ModuleSource, cls).__setup__()
        cls._sql_constraints = [
            ('serie_pypi_package_name_uniq',
                    'UNIQUE(server_serie, pypi_package_name)',
                    'The tuple Server Serie and Package Name of the Module '
                    'Sources must be unique!')
        ]
        cls._order.insert(0, ('name', 'ASC'))
        cls._buttons.update({
                'draft': {
                    'invisible': Eval('state') == 'draft',
                    },
                'validate': {
                    'invisible': Eval('state') != 'draft',
                    },
                'set_deprecated': {
                    'invisible': Eval('state') != 'validated',
                    },
                })

    @staticmethod
    def default_state():
        return 'draft'

    @classmethod
    @ModelView.button
    def draft(cls, sources):
        cls.write(sources, {
            'state': 'draft',
            })

    @classmethod
    @ModelView.button
    def validate(cls, sources):
        cls.write(sources, {
            'state': 'validated',
            })

    @classmethod
    @ModelView.button
    def set_deprecated(cls, sources):
        cls.write(sources, {
            'state': 'deprecated',
            })

