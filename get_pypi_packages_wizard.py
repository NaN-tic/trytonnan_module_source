#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import logging
import pypi_client

from trytond.model import ModelView, fields
from trytond.wizard import Wizard, StateView, StateTransition, Button
from trytond.pool import Pool

__all__ = [
    'GetPypiPackages', 'GetPypiPackagesPackageList', 'GetPypiPackagesResult',
    ]

def get_serie(version):
    return ".".join(version.split(".")[0:2])

def get_last_version_in_serie(package, serie):
    versions = sorted(package.releases.keys())
    versions.reverse()
    for v in versions:
        if get_serie(v) == serie:
            return v
    return False

def get_serie_releases(client, serie):
    logging_name = 'ir.module.source.get_pypi_packages'
    if not serie:
        return []
    if not client:
        return []
    res = []
    for package_name in client.package_list.keys()[0:30]:
        package = client.get_local_package(package_name)
        if get_serie(package.last_release) < serie:
            logging.getLogger(logging_name).warning('Last version of Tryton '
                    'Pypi Package "%s" (%s) is previous than searched serie '
                    '"%s"' % (package_name, package.last_release, serie))
            continue
        if serie not in [get_serie(r) for r in package.releases]:
            client.get_package_releases(package_name)
        selected_version = get_last_version_in_serie(package, serie)
        if not selected_version:
            logging.getLogger(logging_name).warning('Any version of '
                    'serie %s has been found into package "%s" '
                    'releases: %s' % (serie, package_name,
                            package.releases.keys()))
            continue
        release = package.get_local_release(selected_version)
        res.append(release)
    return res


class GetPypiPackagesPackageList(ModelView):
    'Get Pypi Packages - Package List'
    __name__ = 'ir.module.source.get_pypi_packages.package_list'
    serie = fields.Many2One('ir.module.source.serie', 'Serie Filter',
            required=True, on_change=['serie'])
    n_packages = fields.Integer('Number of Packages', readonly=True,
            depends=['serie'])
    package_list = fields.Text('Package List', readonly=True,
            depends=['serie'])

    @staticmethod
    def default_serie():
        series = Pool().get('ir.module.source.serie').search([],
                order=[('name', 'desc')], limit=1)
        return series and series[0].id or False

    def on_change_serie(self):
        if not self.serie:
            return {
                'n_packages': 0,
                'package_list': '',
                }
        client = pypi_client.load_client('pypi_package_list.json')
        if not client:
            client = pypi_client.PypiClient()
            client.get_package_list()
        releases = get_serie_releases(client, self.serie.name)
        package_list_str = ''
        for release in releases:
            package_list_str += '- %s (%s)\n' % (release.name, release.version)
        # trying to supply initialized client to StateViews
        client.save('pypi_package_list.json')
        return {
            'n_packages': len(releases),
            'package_list': package_list_str,
            }


class GetPypiPackagesResult(ModelView):
    'Get Pypi Packages - Result'
    __name__ = 'ir.module.source.get_pypi_packages.result'
    n_new_sources = fields.Integer('New Sources', readonly=True)
    n_updated_sources = fields.Integer('Updated Sources', readonly=True)


class GetPypiPackages(Wizard):
    "Get Pypi Packages"
    __name__ = "ir.module.source.get_pypi_packages"

    start = StateView('ir.module.source.get_pypi_packages.package_list',
        'module_source.get_pypi_packages_package_list_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Create/Update Module Sources', 'import_packages',
                'tryton-ok', default=True),
                ])
    import_packages = StateTransition()
    result = StateView('ir.module.source.get_pypi_packages.result',
        'module_source.get_pypi_packages_result_view_form', [
            Button('Close', 'end', 'tryton-close'),
            ])

    def default_start(self, fields):
        client = pypi_client.PypiClient()
        # fetch packages in 'Framework :: Tryton' category
        client.get_package_list()
        client.save('pypi_package_list.json')
        return {}

    def transition_import_packages(self):
        ModuleSource = Pool().get('ir.module.source')
        Party = Pool().get('party.party')
        serie = self.start.serie
        client = pypi_client.load_client('pypi_package_list.json')
        if not client:
            client = pypi_client.PypiClient()
            client.get_package_list()
        releases = get_serie_releases(client, serie.name)
        new_sources = []
        updated_sources = []
        for release in releases:
            if not release.package_url:
                client.get_release_data(release.name, release.version)
                release = client.get_local_package(release.name)\
                        .get_local_release(release.version)
            author_ids = Party.search([
                    ('pypi_author', 'ilike', release.author),
                    ])
            module_name = "_".join(release.name.split('_')[1:])
            vals = {
                'name': module_name,
                'author': author_ids and author_ids[0] or False,
                'server_serie': serie.id,
                'pypi_package_name': release.name,
                'pypi_release_version': release.version,
                'pypi_release_url': release.release_url,
                }
            existing_package = ModuleSource.search([
                    ('serie', '=', serie.id),
                    ('pypi_package_name', '=', release.name),
                    ])
            if existing_package:
                ModuleSource.write(existing_package, vals)
                updated_sources.append(existing_package)
            else:
                res = ModuleSource.create(vals)
                new_sources.append(res)
        self.result.n_new_sources = len(new_sources)
        self.result.n_updated_sources = len(updated_sources)
        client.save('pypi_package_list.json')
        return 'result'

    def default_result(self, fields):
        return {
            'n_new_sources': self.result.n_new_sources,
            'n_updated_sources': self.result.n_updated_sources,
            }

