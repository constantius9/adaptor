#!/usr/bin/env python

"""
Test the paths management module.

Part of 'Adaptor' framework.

Author: Michael Pankov, 2012-2013.

Please do not redistribute.
"""

import unittest
import paths
import collections
import textwrap
import os


class TestPathsManagerInitFini(unittest.TestCase):
    def setUp(self):
        self.base_path = os.getcwd()

    def test_init(self):
        paths_manager = paths.PathsManager(
            os.path.join(self.base_path, '..'),
            os.path.join(self.base_path, '..', 'data'),
            os.path.join(self.base_path, '..', 'data', 'sources'))

        self.assertEquals(paths_manager.framework_root_dir,
            os.path.abspath(os.path.join(self.base_path, '..')))
        self.assertEquals(paths_manager.benchmark_root_dir,
            os.path.abspath(os.path.join(self.base_path, '..', 'data')))
        self.assertEquals(paths_manager.benchmark_bin_dir,
            os.path.abspath(os.path.join(self.base_path, '..', 'data', 'sources')))
        self.assertEquals(paths_manager.previous_dir,
            os.getcwd())

    def test_init_exception(self):
        self.assertRaises(paths.NonAbsolutePathError,
                          paths.PathsManager,
                          '..',
                          '..',
                          '..')


class TestPathsManagement(unittest.TestCase):
    def setUp(self):
        self.base_path = os.getcwd()
        self.paths_manager = paths.PathsManager(
            os.path.join(self.base_path, '..'),
            os.path.join(self.base_path, '..', 'data'),
            os.path.join(self.base_path, '..', 'data', 'sources'))

    def tearDown(self):
        os.chdir(self.base_path)

    def test_push(self):
        self.assertEquals(self.paths_manager.paths_stack, [])
        self.paths_manager.push_path(os.path.devnull)
        self.assertEquals(self.paths_manager.paths_stack,
                          [os.path.devnull])

    def test_push_exception(self):
        self.assertRaises(paths.NonAbsolutePathError,
                          self.paths_manager.push_path,
                          '..')

    def test_pop(self):
        self.paths_manager.paths_stack = [os.path.devnull]
        path = self.paths_manager.pop_path()
        self.assertEquals(path, os.path.devnull)
        self.assertEquals(self.paths_manager.paths_stack, [])

    def test_get(self):
        self.paths_manager.paths_stack = [os.path.devnull]
        path = self.paths_manager.get_path()
        self.assertEquals(path, os.path.devnull)
        self.assertEquals(self.paths_manager.paths_stack, [os.path.devnull])

    def test_ensure(self):
        self.paths_manager.paths_stack = ['/']
        self.paths_manager.ensure_path()
        self.assertEquals(self.paths_manager.paths_stack, ['/'])
        self.assertEquals(os.getcwd(), '/')

    def test_nest_absolute(self):
        self.paths_manager.nest_path_absolute('/')
        self.assertEquals(self.paths_manager.paths_stack, ['/'])
        self.assertEquals(os.getcwd(), '/')

    def test_nest_absolute_exception(self):
        self.assertRaises(paths.NoSuchNestedPathError,
                          self.paths_manager.nest_path_absolute,
                          'none')

    def test_nest_from_root(self):
        self.paths_manager.nest_path_from_root('..')
        path = os.path.abspath(os.path.join(self.base_path, '..', '..'))
        self.assertEquals(self.paths_manager.paths_stack, [path])
        self.assertEquals(os.getcwd(), path)

    def test_nest_from_benchmark_root(self):
        self.paths_manager.nest_path_from_benchmark_root('sources')
        path = os.path.abspath(os.path.join(
            self.base_path, '..', 'data', 'sources'))
        self.assertEquals(self.paths_manager.paths_stack, [path])
        self.assertEquals(os.getcwd(), path)

    def test_nest(self):
        self.paths_manager.nest_path('..')
        path = os.path.abspath(os.path.join(self.base_path, '..', '..'))
        self.assertEquals(self.paths_manager.paths_stack, [path])
        self.assertEquals(os.getcwd(), path)

    def test_unnest(self):
        self.paths_manager.paths_stack = ['/', os.path.devnull]
        self.paths_manager.unnest_path()
        self.assertEquals(os.getcwd(), '/')

    def test_database_setup(self):
        pm = self.paths_manager
        pm.nest_path_from_root('src')
        pm.unnest_path()
        self.assertEquals(os.getcwd(), self.paths_manager.framework_root_dir)
        pm.nest_path_from_root(os.path.join(
            'couch', 'adaptor'))
        pm.unnest_path()
        self.assertEquals(os.getcwd(), self.paths_manager.framework_root_dir)

    def test_del(self):
        self.paths_manager.nest_path('..')
        path = self.base_path
        del self.paths_manager
        self.assertEquals(os.getcwd(), path)


if __name__ == '__main__':
    unittest.main()
