#!/usr/bin/env python
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import sys
import os
DIR = os.path.abspath(os.path.normpath(os.path.join(__file__,
    '..', '..', '..', '..', '..', 'trytond')))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))

import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT, test_view,\
    test_depends
from trytond.transaction import Transaction


class ModuleSourceTestCase(unittest.TestCase):
    '''
    Test Module Source module.
    '''

    def setUp(self):
        trytond.tests.test_tryton.install_module('module_source')
        self.module_source_serie = POOL.get('ir.module.source.serie')
        self.module_source = POOL.get('ir.module.source')
        self.party = POOL.get('party.party')

    def test0005views(self):
        '''
        Test views.
        '''
        test_view('module_source')

    def test0006depends(self):
        '''
        Test depends.
        '''
        test_depends()

    def test0010serie(self):
        '''
        Create serie.
        '''
        with Transaction().start(DB_NAME, USER,
                context=CONTEXT) as transaction:
            serie28 = self.module_source_serie.create({
                'name': '2.8',
                'stable': False,
                })
            self.assert_(serie28.id)
            transaction.cursor.commit()

    def test0020source(self):
        '''
        Create source.
        '''
        with Transaction().start(DB_NAME, USER,
                context=CONTEXT) as transaction:
            party1 = self.party.search([], limit=1)
            serie1 = self.module_source_serie.search([], limit=1)
            source1 = self.module_source.create({
                'name': 'Source 1',
                'author': party1 and party1[0].id,
                'server_serie': serie1[0].id,
                })
            self.assert_(source1.id)
            transaction.cursor.commit()


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader()\
            .loadTestsFromTestCase(ModuleSourceTestCase))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
