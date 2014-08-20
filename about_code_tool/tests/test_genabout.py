#!/usr/bin/env python
# -*- coding: utf8 -*-

# ============================================================================
#  Copyright (c) 2014 nexB Inc. http://www.nexb.com/ - All rights reserved.
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#      http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# ============================================================================

from __future__ import print_function

import os
import shutil
import tempfile
import unittest

from os.path import abspath, dirname, join

from about_code_tool import genabout


TESTDATA_DIR = join(abspath(dirname(__file__)), 'testdata')
GEN_LOCATION = join(TESTDATA_DIR, 'test_files_for_genabout')


class GenAboutTest(unittest.TestCase):
    def test_get_input_list(self):
        gen = genabout.GenAbout()
        test_input = join(TESTDATA_DIR, 'test_files_for_genabout/about.csv')
        expected_list = [{'about_file': 'about.ABOUT', 'about_resource': '.',
                           'name': 'ABOUT tool', 'version': '0.8.1'}]
        result = gen.get_input_list(test_input)
        self.assertEquals(expected_list, result)

    def test_get_input_list_covert_all_keys_to_lower(self):
        gen = genabout.GenAbout()
        test_input = join(TESTDATA_DIR, 'test_files_for_genabout/about_key_with_upper_case.csv')
        expected_list = [{'about_file': 'about.ABOUT', 'about_resource': '.',
                           'name': 'ABOUT tool', 'version': '0.8.1'}]
        result = gen.get_input_list(test_input)
        self.assertEquals(expected_list, result)

    def test_get_non_empty_rows_list(self):
        gen = genabout.GenAbout()
        input_list = [{'about_file': '/about.ABOUT', 'about_resource': '.',
                       'name': 'ABOUT tool', 'version': '0.8.1'},
                      {'about_file': '', 'about_resource': '',
                       'name': '', 'version': ''}]
        expected_list = [{'about_file': '/about.ABOUT', 'about_resource': '.',
                       'name': 'ABOUT tool', 'version': '0.8.1'}]
        output = gen.get_non_empty_rows_list(input_list)
        self.assertEquals(output, expected_list)

    def test_get_mapping_list(self):
        gen = genabout.GenAbout()
        expected_list = {'about_file': 'directory/filename',
                          'version': 'confirmed version',
                          'name': 'component',
                          'copyright': 'confirmed copyright',
                          'confirmed_license': 'confirmed license'}
        output = gen.get_mapping_list()
        self.assertEquals(output, expected_list)

    def test_convert_input_list(self):
        gen = genabout.GenAbout()
        mapping_list = {'about_file': 'Directory/Filename',
                          'version': 'Confirmed Version',
                           'about_resource': 'file_name', 'name': 'Component'}
        input_list = [{'file_name': 'opensans', 'ignore field': 'i',
                       'Component': 'OpenSans Fonts', 'Confirmed Version': '1',
                       'Directory/Filename': '/extension/streamer/opensans/'}]
        expected_list = [{'about_file': '/extension/streamer/opensans/',
                          'name': 'OpenSans Fonts', 'ignore field': 'i',
                          'version': '1', 'about_resource': 'opensans'}]
        output = gen.convert_input_list(input_list, mapping_list)
        self.assertEquals(output, expected_list)

    def test_validate_value_in_essential_missing_about_file(self):
        gen = genabout.GenAbout()
        test_fields = [{'about_file': '', 'about_resource': '.',
                       'name': 'ABOUT tool', 'version': '0.8.1'}]
        self.assertFalse(gen.validate_value_in_essential_fields(test_fields))

    def test_validate_value_in_essential_missing_about_resource(self):
        gen = genabout.GenAbout()
        test_fields = [{'about_file': '/about.ABOUT', 'about_resource': '',
                       'name': 'ABOUT tool', 'version': '0.8.1'}]
        self.assertTrue(gen.validate_value_in_essential_fields(test_fields))

    def test_validate_value_in_essential_missing_all(self):
        gen = genabout.GenAbout()
        test_fields = [{'about_file': '', 'about_resource': '',
                       'name': 'ABOUT tool', 'version': '0.8.1'}]
        self.assertFalse(gen.validate_value_in_essential_fields(test_fields))

    def test_validate_value_in_essential_fields_no_missing(self):
        gen = genabout.GenAbout()
        test_fields = [{'about_file': '/about.ABOUT', 'about_resource': '.',
                       'name': 'ABOUT tool', 'version': '0.8.1'}]
        self.assertTrue(gen.validate_value_in_essential_fields(test_fields))

    def test_validate_duplication_have_dup(self):
        gen = genabout.GenAbout()
        input_list = [{'about_file': '/about.ABOUT', 'about_resource': '.',
                       'name': 'ABOUT tool', 'version': '0.8.1'},
                      {'about_file': '/about.ABOUT', 'about_resource': '.',
                       'name': 'ABOUT tool', 'version': ''}]
        self.assertTrue(gen.validate_duplication(input_list), 'The list has duplication.')

    def test_validate_duplication_no_dup(self):
        gen = genabout.GenAbout()
        input_list = [{'about_file': '/about.ABOUT', 'about_resource': '.',
                       'name': 'ABOUT tool', 'version': '0.8.1'},
                      {'about_file': 'about1.ABOUT', 'about_resource': 'something',
                       'name': 'ABOUT tool', 'version': ''}]
        self.assertFalse(gen.validate_duplication(input_list), 'The list has no duplication.')

    def test_get_duplicated_keys_have_dup(self):
        gen = genabout.GenAbout()
        test_input = join(TESTDATA_DIR, 'test_files_for_genabout/dup_keys.csv')
        expected_list = ['copyright', 'copyright']
        self.assertEquals(gen.get_duplicated_keys(test_input), expected_list)

    def test_get_duplicated_keys_have_dup_diff_case(self):
        gen = genabout.GenAbout()
        test_input = join(TESTDATA_DIR, 'test_files_for_genabout/dup_keys_with_diff_case.csv')
        expected_list = ['copyright', 'Copyright']
        self.assertEquals(gen.get_duplicated_keys(test_input), expected_list)

    def test_validate_mandatory_fields_no_missing(self):
        gen = genabout.GenAbout()
        input_list = [{'about_file': '/about.ABOUT', 'about_resource': '.',
                       'name': 'ABOUT tool', 'version': '0.8.1'}]
        self.assertTrue(gen.validate_mandatory_fields(input_list))

    def test_validate_mandatory_fields_missing_about_file(self):
        gen = genabout.GenAbout()
        input_list = [{'about_resource': '.',
                       'name': 'ABOUT tool', 'version': '0.8.1'}]
        self.assertFalse(gen.validate_mandatory_fields(input_list))

    def test_validate_mandatory_fields_missing_about_resource(self):
        gen = genabout.GenAbout()
        input_list = [{'about_file': '/about.ABOUT',
                       'name': 'ABOUT tool',
                       'version': '0.8.1'}]
        # self.assertFalse(gen.validate_mandatory_fields(input_list))
        # This is now True as it doesn't need about_resource
        result = gen.validate_mandatory_fields(input_list)
        self.assertTrue(result)

    def test_get_non_supported_fields_no_mapping(self):
        gen = genabout.GenAbout()
        test_fields = [{'about_file': '',
                        'name': 'OpenSans Fonts',
                        'non_supported field': 'TEST',
                        'version': '1',
                        'about_resource': 'opensans'}]
        mapping_keys = []
        result = gen.get_non_supported_fields(test_fields, mapping_keys)
        expected = ['non_supported field']
        self.assertEquals(expected, result)

    def test_get_non_supported_fields_with_mapping(self):
            gen = genabout.GenAbout()
            input = [{'about_file': '', 'name': 'OpenSans Fonts',
                     'non_supported field': 'TEST', 'version': '1',
                     'about_resource': 'opensans'}]
            mapping_keys = ['non_supported field']
            non_supported_list = gen.get_non_supported_fields(input, mapping_keys)
            expected_list = []
            self.assertEquals(non_supported_list, expected_list)

    def test_get_only_supported_fields(self):
        gen = genabout.GenAbout()
        input_list = [{'about_file': '/about.ABOUT',
                       'about_resource': '.',
                       'name': 'ABOUT tool',
                       'version': '0.8.1',
                       'non_supported': 'test'}]
        expected_list = [{'about_file': '/about.ABOUT',
                          'about_resource': '.',
                          'name': 'ABOUT tool',
                          'version': '0.8.1'}]
        ignore_key_list = ['non_supported']
        results = gen.get_only_supported_fields(input_list, ignore_key_list)
        self.assertEquals(expected_list, results)

    def test_get_dje_license_list_no_gen_license_with_no_license_text_file_key(self):
        gen = genabout.GenAbout()
        gen_location = join(TESTDATA_DIR, 'test_files_for_genabout/')
        input_list = [{'about_file': '/about.py.ABOUT',
                       'version': '0.8.1',
                       'about_resource': '.',
                       'name': 'ABOUT tool'}]
        expected_output_list = []
        gen_license = False
        dje_license_dict = {}
        lic_output_list = gen.get_dje_license_list(gen_location,
                                                   input_list,
                                                   gen_license,
                                                   dje_license_dict)
        self.assertEquals(expected_output_list, lic_output_list)
        self.assertFalse(gen.warnings, 'No warnings should be returned.')
        self.assertFalse(gen.errors, 'No errors should be returned.')

    def test_get_dje_license_list_no_gen_license_with_license_text_file_key_not_exist(self):
        gen = genabout.GenAbout()
        gen_location = join(TESTDATA_DIR, 'test_files_for_genabout/')
        input_list = [{'about_file': '/about.py.ABOUT',
                       'version': '0.8.1',
                       'about_resource': '.',
                       'name': 'ABOUT tool',
                       'license_text_file': 'not_exist.txt'}]
        expected = []
        gen_license = False
        dje_license_dict = {}
        result = gen.get_dje_license_list(gen_location,
                                          input_list,
                                          gen_license,
                                          dje_license_dict)
        self.assertEquals(expected, result)
        self.assertFalse(gen.warnings, 'No warnings should be returned.')
        self.assertEqual(1, len(gen.errors))

    def test_get_dje_license_list_file_no_gen_license_with_license_text_file_key_exist(self):
        gen = genabout.GenAbout()
        # FIXME: this is using the about own license, not a test file
        gen_location = join(TESTDATA_DIR, 'test_files_for_genabout/')
        input_list = [{'about_file': '/about.py.ABOUT',
                       'version': '0.8.1',
                       'about_resource': '.',
                       'name': 'ABOUT tool',
                       'license_text_file': '../../../../apache-2.0.LICENSE'}]
        result = gen.get_dje_license_list(gen_location=gen_location,
                                          input_list=input_list,
                                          gen_license=False,
                                          dje_license_dict={})
        expected = []
        self.assertEquals(expected, result)
        self.assertFalse(gen.warnings, 'No warnings should be returned.')
        self.assertFalse(gen.errors, 'No errors should be returned.')

    def test_get_dje_license_list_dir_no_gen_license_with_license_text_file_key_exist(self):
        gen = genabout.GenAbout()
        # FIXME: this is using the about own license, not a test file
        gen_location = join(TESTDATA_DIR, 'test_files_for_genabout/')
        input_list = [{'about_file': '/ABOUT/',
                       'version': '0.8.1',
                       'about_resource': '.',
                       'name': 'ABOUT tool',
                       'license_text_file':
                            '../../../../../apache-2.0.LICENSE'}]
        expected = []
        result = gen.get_dje_license_list(gen_location,
                                                   input_list,
                                                   gen_license=False,
                                                   dje_license_dict={})
        self.assertEquals(expected, result)
        self.assertFalse(gen.warnings, 'No warnings should be returned.')
        self.assertFalse(gen.errors, 'No errors should be returned.')

    def test_get_dje_license_list_file_gen_license_with_license_text_file_key_exist(self):
        gen = genabout.GenAbout()
        gen_location = join(TESTDATA_DIR, 'test_files_for_genabout/')
        input_list = [{'about_file': '/about.py.ABOUT',
                       'version': '0.8.1',
                       'about_resource': '.',
                       'name': 'ABOUT tool',
                       'dje_license': 'Apache License 2.0',
                       'license_text_file': '../../../../apache-2.0.LICENSE'}]
        expected_output_list = []
        gen_license = True
        dje_license_dict = {'Apache License 2.0': [u'apache-2.0',
                                                   'test context']}
        lic_output_list = gen.get_dje_license_list(gen_location,
                                                   input_list,
                                                   gen_license,
                                                   dje_license_dict)
        self.assertEquals(expected_output_list, lic_output_list)
        self.assertFalse(gen.warnings, 'No warnings should be returned.')
        self.assertFalse(gen.errors, 'No errors should be returned.')

    def test_get_dje_license_list_gen_license_with_dje_license_key_empty_license_text_file(self):
        gen = genabout.GenAbout()
        gen_location = join(TESTDATA_DIR, 'test_files_for_genabout/')
        input_list = [{'about_file': '/about.py.ABOUT',
                       'version': '0.8.1',
                       'about_resource': '.',
                       'name': 'ABOUT tool',
                       'dje_license': 'apache-2.0',
                       'dje_license_name': 'Apache License 2.0',
                       'license_text_file': ''}]
        expected_output_list = [('/', 'Apache License 2.0')]
        gen_license = True
        dje_license_dict = {'Apache License 2.0': [u'apache-2.0',
                                                   'test context']}
        lic_output_list = gen.get_dje_license_list(gen_location,
                                                   input_list,
                                                   gen_license,
                                                   dje_license_dict)
        for line in input_list:
            self.assertEquals(line['license_text_file'], 'apache-2.0.LICENSE')
        self.assertEquals(expected_output_list, lic_output_list)
        self.assertFalse(gen.warnings, 'No warnings should be returned.')
        self.assertFalse(gen.errors, 'No errors should be returned.')

    def test_get_dje_license_list_gen_license_with_empty_dje_license_key_empty_license_text_file(self):
        gen = genabout.GenAbout()
        gen_location = join(TESTDATA_DIR, 'test_files_for_genabout/')
        input_list = [{'about_file': '/about.py.ABOUT',
                       'version': '0.8.1',
                       'about_resource': '.',
                       'name': 'ABOUT tool',
                       'license_text_file': '',
                       'dje_license': ''}]
        expected_output_list = []
        gen_license = True
        dje_license_dict = {'Apache License 2.0': [u'apache-2.0',
                                                   'test context']}
        lic_output_list = gen.get_dje_license_list(gen_location, input_list, gen_license, dje_license_dict)
        self.assertEquals(expected_output_list, lic_output_list)
        self.assertTrue(len(gen.warnings) == 1, 'Should return 1 warning.')
        self.assertFalse(gen.errors, 'No errors should be returned.')

    def test_get_dje_license_list_gen_license_with_dje_license_key_no_license_text_file(self):
        gen = genabout.GenAbout()
        gen_location = join(TESTDATA_DIR, 'test_files_for_genabout/')
        input_list = [{'about_file': '/about.py.ABOUT', 'version': '0.8.1',
                        'about_resource': '.', 'name': 'ABOUT tool',
                        'dje_license_name': 'Apache License 2.0',
                        'dje_license': 'Apache License 2.0'}]
        expected_output_list = [('/', 'Apache License 2.0')]
        gen_license = True
        dje_license_dict = {'Apache License 2.0': [u'apache-2.0', 'test context']}
        lic_output_list = gen.get_dje_license_list(gen_location, input_list, gen_license, dje_license_dict)
        for line in input_list:
            self.assertEquals(line['license_text_file'], 'apache-2.0.LICENSE')
        self.assertEquals(expected_output_list, lic_output_list)
        self.assertFalse(gen.warnings, 'No warnings should be returned.')
        self.assertFalse(gen.errors, 'No errors should be returned.')

    def test_pre_generation_about_is_dir_exists_action_0(self):
        gen = genabout.GenAbout()
        gen_location = join(TESTDATA_DIR, 'test_files_for_genabout/')
        action_num = 0
        input_list = [{'about_file': '/TESTCASE/', 'version': '0.8.1',
                        'about_resource': '.', 'name': 'ABOUT tool'}]
        expected_output_list = [[join(TESTDATA_DIR, 'test_files_for_genabout/TESTCASE', 'TESTCASE.ABOUT'),
                                 {'about_file': '/TESTCASE/', 'version': '0.8.1',
                                  'about_resource_path' : '/TESTCASE/',
                                  'about_resource': '.', 'name': 'ABOUT tool'}]]
        output_list = gen.pre_generation(gen_location, input_list, action_num, False)
        self.assertEquals(expected_output_list, output_list)
        self.assertFalse(gen.warnings, 'No warnings should be returned.')
        self.assertFalse(gen.errors, 'No errors should be returned.')

    def test_pre_generation_about_exists_action_0(self):
        gen = genabout.GenAbout()
        gen_location = join(TESTDATA_DIR, 'test_files_for_genabout/')
        action_num = 0
        input_list = [{'about_file': '/about.py.ABOUT', 'version': '0.8.1',
                        'about_resource': '.', 'name': 'ABOUT tool'}]
        expected_output_list = []
        output_list = gen.pre_generation(gen_location, input_list, action_num, False)
        self.assertEquals(expected_output_list, output_list)
        self.assertTrue(len(gen.warnings) == 1, 'Should return 1 warnings.')
        self.assertFalse(gen.errors, 'No errors should be returned.')

    def test_pre_generation_about_exists_action_1(self):
        gen = genabout.GenAbout()
        test_input = [{'about_file': '/about.py.ABOUT',
                       'version': '0.8.2',
                       'about_resource': '.',
                       'name': ''}]
        expected = [[join(TESTDATA_DIR, 'test_files_for_genabout',
                          'about.py.ABOUT'),
                     {'about_file': '/about.py.ABOUT',
                      'about_resource_path': '/about.py.ABOUT',
                      'version': '0.8.2',
                     'about_resource': '.',
                     'name': 'ABOUT tool'}]]
        result = gen.pre_generation(GEN_LOCATION, test_input, 
                                    action_num=1, 
                                    all_in_one=False)
        self.assertEquals(expected, result)
        self.assertFalse(gen.warnings, 'No warnings should be returned.')
        self.assertFalse(gen.errors, 'No errors should be returned.')

    def test_pre_generation_about_exists_action_2(self):
        gen = genabout.GenAbout()
        test_input = [{'about_file': '/about.py.ABOUT',
                       'version': '0.8.2',
                       'about_resource': '.',
                       'name': '',
                       'test': 'test sample'}]
        expected = [[join(TESTDATA_DIR,
                                      'test_files_for_genabout',
                                      'about.py.ABOUT'),
                                 {'about_file': 'about.py.ABOUT',
                                  'name': 'ABOUT tool',
                                  'about_resource_path': '/about.py.ABOUT',
                                  'version': '0.8.1',
                                  'test': 'test sample',
                                  'about_resource': '.'}]]
        result = gen.pre_generation(GEN_LOCATION,
                                         test_input,
                                         action_num=2,
                                         all_in_one=False)
        self.assertEquals(expected, result)
        self.assertFalse(gen.warnings, 'No warnings should be returned.')
        self.assertFalse(gen.errors, 'No errors should be returned.')

    def test_pre_generation_about_exists_action_3(self):
        gen = genabout.GenAbout()
        action_num = 3
        input_list = [{'about_file': '/about.py.ABOUT',
                       'version': '0.8.2',
                        'about_resource': '.',
                        'name': '',
                        'test': 'test sample'}]
        expected_output_list = [[join(TESTDATA_DIR,
                                      'test_files_for_genabout',
                                      'about.py.ABOUT'),
                                  {'about_file': '/about.py.ABOUT',
                                   'version': '0.8.2',
                                   'about_resource_path': '/about.py.ABOUT',
                                   'about_resource': '.',
                                   'name': '',
                                   'test': 'test sample'}]]
        output_list = gen.pre_generation(GEN_LOCATION, input_list, action_num, False)
        self.assertEquals(expected_output_list, output_list)
        self.assertFalse(gen.warnings, 'No warnings should be returned.')
        self.assertFalse(gen.errors, 'No errors should be returned.')

    def test_pre_generation_all_in_one(self):
        gen = genabout.GenAbout()
        action_num = 0
        input_list = [{'about_file': 'test_generation/elasticsearch.ABOUT',
                       'version': '0.19.8',
                       'about_resource': 'elasticsearch-0.19.8.zip',
                       'name': 'ElasticSearch'}]
        expected_output_list = []
        output_list = gen.pre_generation(GEN_LOCATION, input_list, action_num, True)
        self.assertFalse(os.path.exists('testdata/test_files_for_genabout/test_generation'),
                         'This directory should not be generted as the all_in_one is set to True.')
        self.assertEquals(expected_output_list, output_list)
        self.assertTrue(len(gen.warnings) == 1, 'Should return 1 warning.')
        self.assertFalse(gen.errors, 'No errors should be returned.')

    def test_format_output(self):
        gen = genabout.GenAbout()
        input_list = [
            [join(TESTDATA_DIR, 'test_files_for_genabout/about.py.ABOUT'),
             {'about_file': '/about.py.ABOUT',
              'version': '0.8.1',
              'about_resource': '.',
              'name': 'ABOUT Tool'}]]
        expected_output = [[join(TESTDATA_DIR,
                                 'test_files_for_genabout/about.py.ABOUT'),
            'about_resource: .\nname: ABOUT Tool\nversion: 0.8.1\n\n']]
        output = gen.format_output(input_list)
        self.assertEqual(expected_output, output)
        self.assertFalse(gen.warnings, 'No warnings should be returned.')
        self.assertFalse(gen.errors, 'No errors should be returned.')

    def test_format_output_with_continuation(self):
        gen = genabout.GenAbout()
        input_list = [
            [join(TESTDATA_DIR, 'test_files_for_genabout/about.py.ABOUT'),
             {'about_file': '/about.py.ABOUT',
              'version': '0.8.1',
              'about_resource': '.',
              'name': 'ABOUT Tool',
              'readme': 'This is a readme test with \nline continuation.'}]]
        expected_output = [
            [join(TESTDATA_DIR, 'test_files_for_genabout/about.py.ABOUT'),
            'about_resource: .\nname: ABOUT Tool\n'
            'version: 0.8.1\n\n'
            'readme: This is a readme test with \n line continuation.\n']]
        output = gen.format_output(input_list)
        self.assertEqual(expected_output, output)
        self.assertFalse(gen.warnings, 'No warnings should be returned.')
        self.assertFalse(gen.errors, 'No errors should be returned.')

    def test_verify_files_existence_exist(self):
        gen = genabout.GenAbout()
        # FIXME: this is using the files at the root, not testfiles
        input_list = [{'version': '0.8.1',
                       'about_file': '/TESTCASE/',
                       'license_text_file': 'apache-2.0.LICENSE',
                       'name': 'ABOUT tool',
                       'about_resource': '.'}]
        path = '.'
        expected_list = [(join('.', 'apache-2.0.LICENSE'), 'TESTCASE')]
        output = gen.verify_files_existence(input_list, path, False)
        self.assertEqual(expected_list, output)
        self.assertFalse(gen.warnings, 'No warnings should be returned.')
        self.assertFalse(gen.errors, 'No errors should be returned.')

    def test_verify_files_existence_exist_license_in_project(self):
        gen = genabout.GenAbout()
        # FIXME: this is using the files at the root, not testfiles
        input_list = [{'version': '0.8.1',
                       'about_file': '.',
                       'license_text_file': 'apache-2.0.LICENSE',
                       'name': 'ABOUT tool',
                       'about_resource': '.'}]
        path = '.'
        expected_list = [(join('.', 'apache-2.0.LICENSE'), '')]
        output = gen.verify_files_existence(input_list, path, True)
        self.assertEqual(expected_list, output)
        self.assertFalse(gen.warnings, 'No warnings should be returned.')
        self.assertFalse(gen.errors, 'No errors should be returned.')

    def test_verify_files_existence_not_exist(self):
        gen = genabout.GenAbout()
        input_list = [{'version': '0.8.1',
                       'about_file': '/about.py.ABOUT',
                       'license_text_file': 'not_exist.LICENSE.txt',
                        'name': 'ABOUT tool',
                        'about_resource': '.'}]
        path = '.'
        expected_list = []
        output = gen.verify_files_existence(input_list, path, False)
        self.assertEquals(expected_list, output)
        self.assertTrue(len(gen.warnings) == 1, 'Should return 1 warning.')
        self.assertFalse(gen.errors, 'No errors should be returned.')

    def test_verify_files_existence_not_exist_license_in_project(self):
        gen = genabout.GenAbout()
        input_list = [{'version': '0.8.1',
                       'about_file': '/TESTCASE/',
                       'license_text_file': 'not_exist.LICENSE.txt',
                       'name': 'ABOUT tool',
                       'about_resource': '.'}]
        path = '.'
        expected_list = []
        output = gen.verify_files_existence(input_list, path, False)
        self.assertEquals(expected_list, output)
        self.assertTrue(len(gen.warnings) == 1, 'Should return 1 warning.')
        self.assertFalse(gen.errors, 'No errors should be returned.')

    def test_verify_files_existence_no_key(self):
        gen = genabout.GenAbout()
        input_list = [{'version': '0.8.1',
                       'about_file': '/about.py.ABOUT',
                       'name': 'ABOUT tool',
                       'about_resource': '.'}]
        path = '.'
        self.assertRaises(Exception, gen.verify_files_existence, input_list, path)

    def test_gen_license_list_license_text_file_no_value(self):
        gen = genabout.GenAbout()
        input_list = {'about_file': '/tmp/3pp/opensans/',
                      'name': 'OpenSans Fonts',
                      'version': '1',
                      'dje_license': 'apache-2.0',
                      'dje_license_name': 'Apache License 2.0',
                      'license_text_file': '',
                      'about_resource': 'opensans'}
        expected_list = ('/tmp/3pp/opensans', 'Apache License 2.0')
        output = gen.gen_license_list(input_list)
        self.assertEquals(expected_list, output)

    def test_gen_license_list_no_license_text_file_key(self):
        gen = genabout.GenAbout()
        input_list = {'about_file': '/tmp/3pp/opensans/',
                      'name': 'OpenSans Fonts',
                      'version': '1',
                      'dje_license': 'apache-2.0',
                      'dje_license_name': 'Apache License 2.0',
                      'about_resource': 'opensans'}
        expected_list = ('/tmp/3pp/opensans', 'Apache License 2.0')
        output = gen.gen_license_list(input_list)
        self.assertEquals(expected_list, output)

    def test_copy_files_test_path_not_endswith_slash(self):
        # FIXME: this is using the files at the root, not testfiles
        gen = genabout.GenAbout()
        input_list = [('apache-2.0.LICENSE', '.')]
        expected_list = ['apache-2.0.LICENSE']
        tmp_path = tempfile.mkdtemp()
        gen.copy_files(tmp_path, input_list)
        self.assertEquals(expected_list, os.listdir(tmp_path))
        shutil.rmtree(tmp_path)

    def test_copy_files_test_path_endswith_slash(self):
        gen = genabout.GenAbout()
        # FIXME: this is using the files at the root, not testfiles
        input_list = [('apache-2.0.LICENSE', '.')]
        expected_list = ['apache-2.0.LICENSE']
        tmp_path = tempfile.mkdtemp() + '/'
        gen.copy_files(tmp_path, input_list)
        self.assertEquals(expected_list, os.listdir(tmp_path))
        # According to the doc, the user of mkdtemp() is responsible for
        # deleting the temporary directory and its contents when done with it.
        shutil.rmtree(tmp_path)

    def test_write_licenses(self):
        gen = genabout.GenAbout()
        fh, tmp_license_name = tempfile.mkstemp()
        tmp_license_context = 'This is a test.'
        input_list = [[tmp_license_name, tmp_license_context]]
        gen.write_licenses(input_list)
        self.assertTrue(os.path.exists(tmp_license_name))
        with open(tmp_license_name, 'rU') as file_in:
            context = ''
            for line in file_in.readlines():
                context = line
        self.assertEquals(context, tmp_license_context)
        os.close(fh)
        os.remove(tmp_license_name)

    def test_process_dje_licenses(self):
        gen = genabout.GenAbout()
        test_license_list = [('/', 'test')]
        test_license_dict = {'test': [u'test_key', u'This is a test license.']}
        test_path = '/test'
        expected_output = [[join(u'/test', 'test_key.LICENSE'), 'This is a test license.']]
        output = gen.process_dje_licenses(test_license_list, test_license_dict, test_path)
        self.assertEquals(output, expected_output)

    def test_update_about_resource_about_file_and_field_exist(self):
        gen = genabout.GenAbout()
        input_dict = {'about_resource': 'test.c', 'about_file': '/tmp/test.c'}
        about_file_exist = True
        gen.update_about_resource(input_dict, about_file_exist)
        self.assertTrue(input_dict == input_dict, 'The dict should not be changed.')

    def test_update_about_resource_about_file_and_field_not_exist_isFile(self):
        gen = genabout.GenAbout()
        input_dict = {'about_file': '/tmp/test.c'}
        expected_output = {'about_file': '/tmp/test.c', 'about_resource': 'test.c'}
        about_file_exist = True
        gen.update_about_resource(input_dict, about_file_exist)
        self.assertEquals(input_dict, expected_output)

    def test_update_about_resource_about_file_and_field_not_exist_isdir(self):
        gen = genabout.GenAbout()
        input_dict = {'about_file': '/tmp/test/'}
        expected_output = {'about_file': '/tmp/test/', 'about_resource': '.'}
        about_file_exist = True
        gen.update_about_resource(input_dict, about_file_exist)
        self.assertEquals(input_dict, expected_output)

    def test_update_about_resource_no_about_file_field_exist(self):
        gen = genabout.GenAbout()
        input_dict = {'about_resource': 'test.c', 'about_file': '/tmp/test.c'}
        about_file_exist = False
        gen.update_about_resource(input_dict, about_file_exist)
        self.assertTrue(input_dict == input_dict, 'The dict should not be changed.')

    def test_update_about_resource_no_about_file_no_field_isFile(self):
        gen = genabout.GenAbout()
        input_dict = {'about_file': '/tmp/test.c'}
        expected_output = {'about_file': '/tmp/test.c', 'about_resource': 'test.c'}
        about_file_exist = False
        gen.update_about_resource(input_dict, about_file_exist)
        self.assertEquals(input_dict, expected_output)

    def test_update_about_resource_no_about_file_no_field_isdir(self):
        gen = genabout.GenAbout()
        input_dict = {'about_file': '/tmp/test/'}
        expected_output = {'about_file': '/tmp/test/', 'about_resource': '.'}
        about_file_exist = False
        gen.update_about_resource(input_dict, about_file_exist)
        self.assertEquals(input_dict, expected_output)

    def test_update_about_resource_path_about_file_field_exist(self):
        gen = genabout.GenAbout()
        input_dict = {'about_resource_path': '/tmp/test.c', 'about_file': '/tmp/test.c'}
        about_file_exist = True
        gen.update_about_resource_path(input_dict, about_file_exist)
        self.assertTrue(input_dict == input_dict, 'The dict should not be changed.')

    def test_update_about_resource_path_about_file_field_not_exist_isFile(self):
        gen = genabout.GenAbout()
        input_dict = {'about_file': '/tmp/test.c'}
        expected_output = {'about_file': '/tmp/test.c', 'about_resource_path': '/tmp/test.c'}
        about_file_exist = True
        gen.update_about_resource_path(input_dict, about_file_exist)
        self.assertEquals(input_dict, expected_output)

    def test_update_about_resource_path_about_file_field_not_exist_isDir(self):
        gen = genabout.GenAbout()
        input_dict = {'about_file': '/tmp/test/'}
        expected_output = {'about_file': '/tmp/test/', 'about_resource_path': '/tmp/test/'}
        about_file_exist = True
        gen.update_about_resource_path(input_dict, about_file_exist)
        self.assertEquals(input_dict, expected_output)

    def test_update_about_resource_path_no_about_file_field_exist(self):
        gen = genabout.GenAbout()
        input_dict = {'about_resource_path': '/tmp/test.c', 'about_file': '/tmp/test.c'}
        about_file_exist = False
        gen.update_about_resource_path(input_dict, about_file_exist)
        self.assertTrue(input_dict == input_dict, 'The dict should not be changed.')

    def test_update_about_resource_path_no_about_file_field_not_exist_isFile(self):
        gen = genabout.GenAbout()
        input_dict = {'about_file': '/tmp/test.c'}
        expected_output = {'about_file': '/tmp/test.c', 'about_resource_path': '/tmp/test.c'}
        about_file_exist = False
        gen.update_about_resource_path(input_dict, about_file_exist)
        self.assertEquals(input_dict, expected_output)

    def test_update_about_resource_path_no_about_file_field_not_exist_isDir(self):
        gen = genabout.GenAbout()
        input_dict = {'about_file': '/tmp/test/'}
        expected_output = {'about_file': '/tmp/test/', 'about_resource_path': '/tmp/test/'}
        about_file_exist = False
        gen.update_about_resource_path(input_dict, about_file_exist)
        self.assertEquals(input_dict, expected_output)


