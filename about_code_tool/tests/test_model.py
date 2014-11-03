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

import posixpath
import unittest

from about_code_tool.tests import get_test_loc
from about_code_tool.tests import get_test_lines


from about_code_tool import Error
from about_code_tool import CRITICAL, INFO, WARNING
from about_code_tool import model
from about_code_tool import util
from about_code_tool import ERROR
from collections import OrderedDict
import about_code_tool
from about_code_tool.tests import get_temp_file
from about_code_tool.tests import get_unicode_content
from about_code_tool.util import load_csv


class FieldTest(unittest.TestCase):
    def test_Field_init(self):
        model.Field()
        model.StringField()
        model.ListField()
        model.UrlField()
        model.BooleanField()
        model.PathField()
        model.TextField()

    def test_empty_Field_has_no_content(self):
        field = model.Field()
        self.assertFalse(field.has_content)

    def test_empty_Field_has_default_value(self):
        field = model.Field()
        self.assertEqual('', field.value)

    def test_PathField_check_location(self):
        test_file = 'license.LICENSE'
        field = model.PathField(name='f', value=test_file, present=True)
        base_dir = get_test_loc('fields')

        errors = field.validate(base_dir=base_dir)
        expected_errrors = []
        self.assertEqual(expected_errrors, errors)

        result = field.value[test_file]
        expected = posixpath.join(util.to_posix(base_dir), test_file)
        self.assertEqual(expected, result)

    def test_PathField_check_missing_location(self):
        test_file = 'does.not.exist'
        field = model.PathField(name='f', value=test_file, present=True)
        base_dir = get_test_loc('fields')
        errors = field.validate(base_dir=base_dir)

        expected_errors = [
            Error(CRITICAL, u'Field f: Path does.not.exist not found')]
        self.assertEqual(expected_errors, errors)

        result = field.value[test_file]
        self.assertEqual(None, result)

    def test_TextField_loads_file(self):
        field = model.TextField(name='f', value='license.LICENSE',
                                present=True)


        base_dir = get_test_loc('fields')
        errors = field.validate(base_dir=base_dir)
        self.assertEqual([], errors)

        expected = [('license.LICENSE', u'some license text')]
        result = field.value.items()
        self.assertEqual(expected, result)

    def test_UrlField_is_valid_url(self):
        self.assertTrue(model.UrlField.is_valid_url('http://www.google.com'))

    def test_UrlField_is_valid_url_not_starting_with_www(self):
        self.assertTrue(model.UrlField.is_valid_url('https://nexb.com'))
        self.assertTrue(model.UrlField.is_valid_url('http://archive.apache.org/dist/httpcomponents/commons-httpclient/2.0/source/commons-httpclient-2.0-alpha2-src.tar.gz'))
        self.assertTrue(model.UrlField.is_valid_url('http://de.wikipedia.org/wiki/Elf (Begriffsklärung)'))
        self.assertTrue(model.UrlField.is_valid_url('http://nothing_here.com'))

    def test_UrlField_is_valid_url_no_schemes(self):
        self.assertFalse(model.UrlField.is_valid_url('google.com'))
        self.assertFalse(model.UrlField.is_valid_url('www.google.com'))
        self.assertFalse(model.UrlField.is_valid_url(''))

    def test_UrlField_is_valid_url_not_ends_with_com(self):
        self.assertTrue(model.UrlField.is_valid_url('http://www.google'))

    def test_UrlField_is_valid_url_ends_with_slash(self):
        self.assertTrue(model.UrlField.is_valid_url('http://www.google.co.uk/'))

    def test_UrlField_is_valid_url_empty_URL(self):
        self.assertFalse(model.UrlField.is_valid_url('http:'))

    def check_validate(self, field_class, value, expected, expected_errors):
        """
        Check field values after validation
        """
        field = field_class(name='s', value=value, present=True)
        # check that validate can be applied multiple times without side effects
        for _ in range(2):
            errors = field.validate()
            self.assertEqual(expected_errors, errors)
            self.assertEqual(expected, field.value)

    def test_StringField_validate_trailing_spaces_are_removed(self):
        field_class = model.StringField
        value = 'trailin spaces  '
        expected = 'trailin spaces'
        self.check_validate(field_class, value, expected, expected_errors=[])

    def test_ListField_contains_list_after_validate(self):
        value = 'string'
        field_class = model.ListField
        expected = [value]
        self.check_validate(field_class, value, expected, expected_errors=[])

    def test_ListField_contains_stripped_strings_after_validate(self):
        value = '''first line    
                   second line  '''
        field_class = model.ListField
        expected = ['first line', 'second line']
        self.check_validate(field_class, value, expected, expected_errors=[])

    def test_PathField_contains_stripped_strings_after_validate(self):
        value = '''first line    
                   second line  '''
        field_class = model.ListField
        expected = ['first line', 'second line']
        self.check_validate(field_class, value, expected, expected_errors=[])

    def test_PathField_contains_dict_after_validate(self):
        value = 'string'
        field_class = model.PathField
        expected = OrderedDict([('string', None)])
        expected_errors = [
            Error(ERROR, u'Field s: Unable to verify path: string: No base directory provided')
                          ]
        self.check_validate(field_class, value, expected, expected_errors)

    def test_UrlField_contains_list_after_validate(self):
        value = 'http://some.com/url'
        field_class = model.UrlField
        expected = [value]
        self.check_validate(field_class, value, expected, expected_errors=[])

    def test_SingleLineField_has_errors_if_multiline(self):
        value = '''line1
        line2'''
        field_class = model.SingleLineField
        expected = value
        expected_errors = [Error(ERROR, u'Field s: Cannot span multiple lines: line1\n        line2')]
        self.check_validate(field_class, value, expected, expected_errors)

    def test_AboutResourceField_can_resolve_single_value(self):
        about_file_path = 'some/dir/me.ABOUT'
        field = model.AboutResourceField(name='s', value='.', present=True)
        field.validate()
        expected = ['some/dir']
        field.resolve(about_file_path)
        result = field.resolved_paths
        self.assertEqual(expected, result)

    def check_AboutResourceField_can_resolve_paths_list(self):
        about_file_path = 'some/dir/me.ABOUT'
        value = '''.
                   ../path1
                   path2/path3/
                   /path2/path3/
                   '''
        field = model.AboutResourceField(name='s', value=value, present=True)
        field.validate()
        expected = ['some/dir',
                    'some/path1',
                    'some/dir/path2/path3']
        field.resolve(about_file_path)
        result = field.resolved_paths
        self.assertEqual(expected, result)

    def test_AboutResourceField_can_resolve_paths_list_multiple_times(self):
        for _ in range(3):
            self.check_AboutResourceField_can_resolve_paths_list()


class ParseTest(unittest.TestCase):
    maxDiff = None
    def test_parse_can_parse_simple_fields(self):
        test = get_test_lines('parse/basic.about')
        errors, result = list(model.parse(test))

        self.assertEqual([], errors)

        expected = [(u'single_line', u'optional'),
                    (u'other_field', u'value'),
                    ]
        self.assertEqual(expected, result)

    def test_parse_can_parse_continuations(self):
        test = get_test_lines('parse/continuation.about')
        errors, result = model.parse(test)

        self.assertEqual([], errors)

        expected = [(u'single_line', u'optional'),
                    (u'other_field', u'value'),
                    (u'multi_line', u'some value\n'
                                     u'and more\n'
                                     u' and yet more')]
        self.assertEqual(expected, result)

    def test_parse_can_handle_complex_continuations(self):
        test = get_test_lines('parse/complex.about')
        errors, result = model.parse(test)
        self.assertEqual([], errors)

        expected = [(u'single_line', u'optional'),
                    (u'other_field', u'value\n'),
                    (u'multi_line', u'some value\n'
                                     u'and more\n'
                                     u' and yet more\n'
                                     u'  '),
                    (u'yetanother', u'\nsdasd')]
        self.assertEqual(expected, result)

    def test_parse_error_for_invalid_field_name(self):
        test = get_test_lines('parse/invalid_names.about')
        errors, result = model.parse(test)
        expected = [(u'val3_id_', u'some:value'),
                    (u'VALE3_ID_', u'some:value')]
        self.assertEqual(expected, result)

        expected_errors = [
            Error(CRITICAL, "Invalid line: 0: u'invalid space:value\\n'"),
            Error(CRITICAL, "Invalid line: 1: u'other-field: value\\n'"),
            Error(CRITICAL, "Invalid line: 4: u'_invalid_dash: value\\n'"),
            Error(CRITICAL, "Invalid line: 5: u'3invalid_number: value\\n'"),
            Error(CRITICAL, "Invalid line: 6: u'invalid.dot: value'")
            ]
        self.assertEqual(expected_errors, errors)

    def test_parse_error_for_invalid_continuation(self):
        test = get_test_lines('parse/invalid_continuation.about')
        errors, result = model.parse(test)
        expected = [(u'single_line', u'optional'),
                    (u'other_field', u'value'),
                    (u'multi_line', u'some value\n' u'and more')]
        self.assertEqual(expected, result)
        expected_errors = [
            Error(CRITICAL, "Invalid continuation line: 0:"
                            " u' invalid continuation1\\n'"),
            Error(CRITICAL, "Invalid continuation line: 7:"
                            " u' invalid continuation2\\n'")]
        self.assertEqual(expected_errors, errors)

    def test_parse_rejects_non_ascii_names_and_accepts_unicode_values(self):
        test = get_test_lines('parse/non_ascii_field_name_value.about')
        errors, result = model.parse(test)
        expected = [(u'name', u'name'),
                    (u'about_resource', u'.'),
                    (u'owner', u'Mat\xedas Aguirre')]
        self.assertEqual(expected, result)

        expected_errors = [
            Error(CRITICAL, "Invalid line: 3: u'Mat\\xedas: unicode field name\\n'")]
        self.assertEqual(expected_errors, errors)

    def test_parse_handles_blank_lines_and_spaces_in_field_names(self):
        test = '''
name: test space
version: 0.7.0
about_resource: about.py
field with spaces: This is a test case for field with spaces
'''.splitlines(True)

        errors, result = model.parse(test)

        expected = [('name', 'test space'),
                    ('version', '0.7.0'),
                    ('about_resource', 'about.py')]
        self.assertEqual(expected, result)

        expected_errors = [
            Error(CRITICAL, "Invalid line: 4: 'field with spaces: This is a test case for field with spaces\\n'")]
        self.assertEqual(expected_errors, errors)

    def test_parse_ignore_blank_lines_and_lines_without_no_colon(self):
        test = '''
name: no colon test
test
version: 0.7.0
about_resource: about.py
test with no colon
'''.splitlines(True)
        errors, result = model.parse(test)

        expected = [('name', 'no colon test'),
                    ('version', '0.7.0'),
                    ('about_resource', 'about.py')]
        self.assertEqual(expected, result)

        expected_errors = [
            Error(CRITICAL, "Invalid line: 2: 'test\\n'"),
            Error(CRITICAL, "Invalid line: 5: 'test with no colon\\n'")]
        self.assertEqual(expected_errors, errors)


class AboutTest(unittest.TestCase):

    def test_About_duplicate_field_names_are_detected_with_different_case(self):
        test_file = get_test_loc('parse/dupe_field_name.ABOUT')
        a = model.About(test_file)
        expected = [
            Error(WARNING, u'Field Name is a duplicate. Original value: "old" replaced with: "new"'),
            Error(INFO, u'Field About_Resource is a duplicate with the same value as before.')]
        result = a.errors
        self.assertEqual(expected, result)

    def check_About_hydrate(self, about, fields, errors):
        expected = set([
            'name',
            'home_url',
            'download_url',
            'version',
            'date',
            'license_spdx',
            'license_text_file',
            'copyright',
            'notice_file',
            'about_resource'])

        expected_errors = [
            Error(INFO, u'Field date is a custom field'),
            Error(INFO, u'Field license_spdx is a custom field'),
            Error(INFO, u'Field license_text_file is a custom field')]

        errors = about.hydrate(fields)

        self.assertEqual(expected_errors, errors)

        result = set([f.name for f in about.all_fields() if f.present])
        self.assertEqual(expected, result)

    def test_About_hydrate_normalize_field_names_to_lowercase(self):
        self.maxDiff = None
        test_file = get_test_lines('parser_tests/upper_field_names.ABOUT')
        errors, fields = model.parse(test_file)
        self.assertEqual([], errors)
        a = model.About()
        self.check_About_hydrate(a, fields, errors)

    def test_About_hydrate_can_be_called_multiple_times(self):
        test_file = get_test_lines('parser_tests/upper_field_names.ABOUT')
        errors, fields = model.parse(test_file)
        self.assertEqual([], errors)
        a = model.About()
        for _ in range(3):
            self.check_About_hydrate(a, fields, errors)

    def test_About_with_existing_about_resource_has_no_error(self):
        test_file = get_test_loc('parser_tests/about_resource_field.ABOUT')
        a = model.About(test_file)
        self.assertEqual([], a.errors)
        result = a.about_resource.value['about_resource.c']
        # this means we have a location
        self.assertNotEqual([], result)

    def test_About_has_errors_when_about_resource_is_missing(self):
        test_file = get_test_loc('parser_tests/.ABOUT')
        a = model.About(test_file)
        expected = [
                    Error(CRITICAL, u'Field about_resource is required')
                    ]
        result = a.errors
        self.assertEqual(expected, result)

    def test_About_has_errors_when_about_resource_does_not_exist(self):
        test_file = get_test_loc('parser_tests/missing_about_ref.ABOUT')
        a = model.About(test_file)
        expected = [
            Error(CRITICAL, u'Field about_resource: Path about_file_missing.c not found')]
        result = a.errors
        self.assertEqual(expected, result)

    def test_About_has_errors_when_missing_required_fields_are_missing(self):
        test_file = get_test_loc('parse/missing_required.ABOUT')
        a = model.About(test_file)
        expected = [
            Error(CRITICAL, u'Field about_resource is required'),
            Error(CRITICAL, u'Field name is required'),
            ]
        result = a.errors
        self.assertEqual(expected, result)

    def test_About_has_errors_when_required_fields_are_empty(self):
        test_file = get_test_loc('parse/empty_required.ABOUT')
        a = model.About(test_file)
        expected = [
            Error(CRITICAL, u'Field about_resource is required and empty'),
            Error(CRITICAL, u'Field name is required and empty'),
            ]
        result = a.errors
        self.assertEqual(expected, result)

    def test_About_has_errors_with_empty_notice_file_field(self):
        test_file = get_test_loc('parse/empty_notice_field.about')
        a = model.About(test_file)
        expected = [
            Error(WARNING, u'Field notice_file is present but empty')]
        result = a.errors
        self.assertEqual(expected, result)

    def test_About_custom_fields_are_collected_correctly(self):
        test_file = get_test_loc('parse/custom_fields.about')
        a = model.About(test_file)
        result = [(n, f.value) for n, f in a.custom_fields.items()]
        expected = [
            (u'single_line', u'README STUFF'),
            (u'multi_line', u'line1\nline2'),
            (u'empty', '')]
        self.assertEqual(expected, result)

    def test_About_has_errors_for_illegal_custom_field_name(self):
        test_file = get_test_loc('parse/illegal_custom_field.about')
        a = model.About(test_file)
        result = a.custom_fields.items()
        expected = [
            ]
        self.assertEqual(expected, result)

    def test_About_file_fields_are_empty_if_present_and_path_missing(self):
        test_file = get_test_loc('parse/missing_notice_license_files.ABOUT')
        a = model.About(test_file)
        expected_errors = [
            Error(CRITICAL, u'Field license_file: Path test.LICENSE not found'),
            Error(CRITICAL, u'Field notice_file: Path test.NOTICE not found'),
            ]
        self.assertEqual(expected_errors, a.errors)
        expected = [(u'test.LICENSE', None)]
        result = a.license_file.value.items()
        self.assertEqual(expected, result)

        expected = [(u'test.NOTICE', None)]
        result = a.notice_file.value.items()
        self.assertEqual(expected, result)

    def test_About_notice_and_license_text_are_loaded_from_file(self):
        test_file = get_test_loc('parse/license_file_notice_file.ABOUT')
        a = model.About(test_file)

        expected = '''Tester holds the copyright for test component. Tester relinquishes copyright of
this software and releases the component to Public Domain.

* Email Test@tester.com for any questions'''

        result = a.license_file.value['license_text.LICENSE']
        self.assertEqual(expected, result)

        expected = '''Test component is released to Public Domain.'''
        result = a.notice_file.value['notice_text.NOTICE']
        self.assertEqual(expected, result)

    def test_About_license_and_notice_text_are_empty_if_field_missing(self):
        test_file = get_test_loc('parse/no_file_fields.ABOUT')
        a = model.About(test_file)

        expected_errors = []
        self.assertEqual(expected_errors, a.errors)

        result = a.license_file.value
        self.assertEqual({}, result)

        result = a.notice_file.value
        self.assertEqual({}, result)

    def test_About_rejects_non_ascii_names_and_accepts_unicode_values(self):
        test_file = get_test_loc('parse/non_ascii_field_name_value.about')
        a = model.About(test_file)
        result = a.errors
        expected = [
            Error(CRITICAL, "Invalid line: 3: u'Mat\\xedas: unicode field name\\n'")
                    ]
        self.assertEqual(expected, result)

    def test_About_contains_about_file_path(self):
        test_file = get_test_loc('parse/complete/about.ABOUT')
        a = model.About(test_file, about_file_path='complete/about.ABOUT')
        self.assertEqual([], a.errors)
        expected = 'complete/about.ABOUT'
        result = a.about_file_path
        self.assertEqual(expected, result)

    def test_About_equals(self):
        test_file = get_test_loc('equal/complete/about.ABOUT')
        a = model.About(test_file, about_file_path='complete/about.ABOUT')
        b = model.About(test_file, about_file_path='complete/about.ABOUT')
        self.assertEqual(a, b)

    def test_About_equals_with_small_text_differences(self):
        test_file = get_test_loc('equal/complete2/about.ABOUT')
        a = model.About(test_file, about_file_path='complete2/about.ABOUT')
        test_file2 = get_test_loc('equal/complete/about.ABOUT')
        b = model.About(test_file2, about_file_path='complete/about.ABOUT')
        self.assertEqual(a, b)

    def test_About_same_attribution(self):
        base_dir = 'some_dir'
        a = model.About()
        a.load_dict({'name': u'apache', 'version': u'1.1' }, base_dir)
        b = model.About()
        b.load_dict({'name': u'apache', 'version': u'1.1' }, base_dir)
        self.assertTrue(a.same_attribution(b))

    def test_About_same_attribution_with_different_resource(self):
        base_dir = 'some_dir'
        a = model.About()
        a.load_dict({'about_resource': u'resource', 'name': u'apache', 'version': u'1.1' }, base_dir)
        b = model.About()
        b.load_dict({'about_resource': u'other', 'name': u'apache', 'version': u'1.1' }, base_dir)
        self.assertTrue(a.same_attribution(b))

    def test_About_same_attribution_different_data(self):
        base_dir = 'some_dir'
        a = model.About()
        a.load_dict({'about_resource': u'resource', 'name': u'apache', 'version': u'1.1' }, base_dir)
        b = model.About()
        b.load_dict({'about_resource': u'other', 'name': u'apache', 'version': u'1.2' }, base_dir)
        self.assertFalse(a.same_attribution(b))
        self.assertFalse(b.same_attribution(a))

    def test_field_names(self):
        a = model.About()
        a.custom_fields['f'] = model.StringField(name='f', value='1',
                                                 present=True)
        b = model.About()
        b.custom_fields['g'] = model.StringField(name='g', value='1',
                                                 present=True)
        abouts = [a, b]
        # ensure that custom fields and about file path are collected
        # and that all fields are in the correct order
        expected = [
            model.About.about_file_path_attr,
            model.About.about_resource_path_attr,
            'about_resource',
            'name',
            'version',
            'download_url',
            'description',
            'home_url',
            'notes',
            'license',
            'license_name',
            'license_file',
            'license_url',
            'copyright',
            'notice_file',
            'notice_url',
            'redistribute',
            'attribute',
            'track_change',
            'modified',
            'changelog_file',
            'owner',
            'owner_url',
            'contact',
            'author',
            'vcs_tool',
            'vcs_repository',
            'vcs_path',
            'vcs_tag',
            'vcs_branch',
            'vcs_revision',
            'checksum',
            'spec_version',
            'f',
            'g']
        result = model.field_names(abouts)
        self.assertEqual(expected, result)

    def test_field_names_does_not_return_duplicates_custom_fields(self):
        a = model.About()
        a.custom_fields['f'] = model.StringField(name='f', value='1',
                                                 present=True)
        a.custom_fields['cf'] = model.StringField(name='cf', value='1',
                                                 present=True)
        b = model.About()
        b.custom_fields['g'] = model.StringField(name='g', value='1',
                                                 present=True)
        b.custom_fields['cf'] = model.StringField(name='cf', value='2',
                                                 present=True)
        abouts = [a, b]
        # ensure that custom fields and about file path are collected
        # and that all fields are in the correct order
        expected = [
            'about_resource',
            'name',
            'cf',
            'f',
            'g',
            ]
        result = model.field_names(abouts, with_paths=False,
                                   with_absent=False,
                                   with_empty=False)
        self.assertEqual(expected, result)


class SerializationTest(unittest.TestCase):
    def test_About_dumps(self):
        self.maxDiff = None
        test_file = get_test_loc('parse/complete/about.ABOUT')
        a = model.About(test_file)
        self.assertEqual([], a.errors)

        expected = u'''about_resource: .
name: AboutCode
version: 0.11.0
description: AboutCode is a tool
 to process ABOUT files.
 An ABOUT file is a file.
home_url: http://dejacode.org
license: apache-2.0
license_file: apache-2.0.LICENSE
copyright: Copyright (c) 2013-2014 nexB Inc.
notice_file: NOTICE
owner: nexB Inc.
author: Jillian Daguil, Chin Yeung Li, Philippe Ombredanne, Thomas Druez
vcs_tool: git
vcs_repository: https://github.com/dejacode/about-code-tool.git
'''
        result = a.dumps()
        self.assertEqual(expected, result)

    def test_About_dumps_all_fields_if_not_present_with_absent_True(self):
        self.maxDiff = None
        test_file = get_test_loc('parse/complete2/about.ABOUT')
        a = model.About(test_file)
        expected_error = [
            Error(INFO, u'Field custom1 is a custom field'),
            Error(INFO, u'Field custom2 is a custom field'),
            Error(WARNING, u'Field custom2 is present but empty')]
        self.assertEqual(expected_error, a.errors)

        expected = u'''about_resource: .
name: AboutCode
version: 0.11.0
download_url:
description:
home_url:
notes:
license:
license_name:
license_file:
license_url:
copyright:
notice_file:
notice_url:
redistribute:
attribute:
track_change:
modified:
changelog_file:
owner:
owner_url:
contact:
author:
vcs_tool:
vcs_repository:
vcs_path:
vcs_tag:
vcs_branch:
vcs_revision:
checksum:
spec_version:
custom1: multi
 line
custom2:
'''
        result = a.dumps(with_absent=True)
        self.assertEqual(expected, result)

    def test_About_dumps_does_not_dump_not_present_with_absent_False(self):
        self.maxDiff = None
        test_file = get_test_loc('parse/complete2/about.ABOUT')
        a = model.About(test_file)
        expected_error = [
            Error(INFO, u'Field custom1 is a custom field'),
            Error(INFO, u'Field custom2 is a custom field'),
            Error(WARNING, u'Field custom2 is present but empty')]
        self.assertEqual(expected_error, a.errors)

        expected = u'''about_resource: .
name: AboutCode
version: 0.11.0
custom1: multi
 line
custom2:
'''
        result = a.dumps(with_absent=False)
        self.assertEqual(expected, result)

    def test_About_dumps_does_not_dump_present__empty_with_absent_False(self):
        self.maxDiff = None
        test_file = get_test_loc('parse/complete2/about.ABOUT')
        a = model.About(test_file)
        expected_error = [
            Error(INFO, u'Field custom1 is a custom field'),
            Error(INFO, u'Field custom2 is a custom field'),
            Error(WARNING, u'Field custom2 is present but empty')]
        self.assertEqual(expected_error, a.errors)

        expected = u'''about_resource: .
name: AboutCode
version: 0.11.0
custom1: multi
 line
'''
        result = a.dumps(with_absent=False, with_empty=False)
        self.assertEqual(expected, result)

    def test_About_as_dict_contains_special_paths(self):
        self.maxDiff = None
        test_file = get_test_loc('parse/complete/about.ABOUT')
        a = model.About(test_file, about_file_path='complete/about.ABOUT')
        expected_errors = []
        self.assertEqual(expected_errors, a.errors)
        as_dict = a.as_dict(with_paths=True, with_empty=False, with_absent=False)
        expected = 'complete/about.ABOUT'
        result = as_dict[model.About.about_file_path_attr]
        self.assertEqual(expected, result)

        expected = 'complete'
        result = as_dict[model.About.about_resource_path_attr]
        self.assertEqual(expected, result)

    def test_About_as_dict_with_empty(self):
        self.maxDiff = None
        test_file = get_test_loc('as_dict/about.ABOUT')
        a = model.About(test_file, about_file_path='complete/about.ABOUT')
        expected_errors = [
            Error(INFO, u'Field custom1 is a custom field'),
            Error(INFO, u'Field custom_empty is a custom field'),
            Error(WARNING, u'Field author is present but empty'),
            Error(WARNING, u'Field custom_empty is present but empty')]
        self.assertEqual(expected_errors, a.errors)
        expected = {'about_resource': u'.',
                    'author': u'',
                    'copyright': u'Copyright (c) 2013-2014 nexB Inc.',
                    u'custom1': u'some custom',
                    u'custom_empty': u'',
                    'description': u'AboutCode is a tool\nfor files.',
                    'license': u'apache-2.0',
                    'name': u'AboutCode',
                    'owner': u'nexB Inc.'}
        result = a.as_dict(with_paths=False,
                           with_empty=True,
                           with_absent=False)
        self.assertEqual(expected, dict(result))

    def test_About_as_dict_with_present(self):
        self.maxDiff = None
        test_file = get_test_loc('as_dict/about.ABOUT')
        a = model.About(test_file, about_file_path='complete/about.ABOUT')
        expected_errors = [
            Error(INFO, u'Field custom1 is a custom field'),
            Error(INFO, u'Field custom_empty is a custom field'),
            Error(WARNING, u'Field author is present but empty'),
            Error(WARNING, u'Field custom_empty is present but empty')]
        self.assertEqual(expected_errors, a.errors)
        expected = {'about_resource': u'.',
                    'attribute': u'',
                    'changelog_file': u'',
                    'checksum': u'',
                    'contact': u'',
                    'copyright': u'Copyright (c) 2013-2014 nexB Inc.',
                    u'custom1': u'some custom',
                    'description': u'AboutCode is a tool\nfor files.',
                    'download_url': u'',
                    'home_url': u'',
                    'license': u'apache-2.0',
                    'license_file': u'',
                    'license_name': u'',
                    'license_url': u'',
                    'modified': u'',
                    'name': u'AboutCode',
                    'notes': u'',
                    'notice_file': u'',
                    'notice_url': u'',
                    'owner': u'nexB Inc.',
                    'owner_url': u'',
                    'redistribute': u'',
                    'spec_version': u'',
                    'track_change': u'',
                    'vcs_branch': u'',
                    'vcs_path': u'',
                    'vcs_repository': u'',
                    'vcs_revision': u'',
                    'vcs_tag': u'',
                    'vcs_tool': u'',
                    'version': u''}
        result = a.as_dict(with_paths=False,
                           with_empty=False,
                           with_absent=True)
        self.assertEqual(expected, dict(result))

    def test_About_as_dict_with_nothing(self):
        self.maxDiff = None
        test_file = get_test_loc('as_dict/about.ABOUT')
        a = model.About(test_file, about_file_path='complete/about.ABOUT')
        expected_errors = [
            Error(INFO, u'Field custom1 is a custom field'),
            Error(INFO, u'Field custom_empty is a custom field'),
            Error(WARNING, u'Field author is present but empty'),
            Error(WARNING, u'Field custom_empty is present but empty')]
        self.assertEqual(expected_errors, a.errors)
        expected = {'about_resource': u'.',
                    'copyright': u'Copyright (c) 2013-2014 nexB Inc.',
                    u'custom1': u'some custom',
                    'description': u'AboutCode is a tool\nfor files.',
                    'license': u'apache-2.0',
                    'name': u'AboutCode',
                    'owner': u'nexB Inc.'}
        result = a.as_dict(with_paths=False,
                           with_empty=False,
                           with_absent=False)
        self.assertEqual(expected, dict(result))

    def test_loads_dumps_is_idempotent(self):
        test = u'''about_resource: .
name: AboutCode
version: 0.11.0
custom1: multi
 line
'''
        a = model.About()
        base_dir = 'some_dir'
        a.loads(test, base_dir)
        dumped = a.dumps(with_absent=False, with_empty=False)
        self.assertEqual(test, dumped)

    def test_load_dump_is_idempotent(self):
        test_file = get_test_loc('load/this.ABOUT')
        a = model.About()
        a.load(test_file)
        dumped_file = get_temp_file()
        a.dump(dumped_file, with_absent=False, with_empty=False)

        expected = get_unicode_content(test_file).splitlines()
        result = get_unicode_content(dumped_file).splitlines()
        self.assertEqual(expected, result)

    def test_load_can_load_unicode(self):
        test_file = get_test_loc('unicode/nose-selecttests.ABOUT')
        a = model.About()
        a.load(test_file)
        errors = [
            Error(INFO, u'Field dje_license is a custom field'),
            Error(INFO, u'Field license_text_file is a custom field'),
            Error(INFO, u'Field scm_tool is a custom field'),
            Error(INFO, u'Field scm_repository is a custom field'),
            Error(INFO, u'Field test is a custom field'),
            Error(CRITICAL, u'Field about_resource: Path nose-selecttests-0.3.zip not found')]
        self.assertEqual(errors, a.errors)
        self.assertEqual(u'Copyright (c) 2012, Domen Kožar', a.copyright.value)

    def test_load_has_errors_for_non_unicode(self):
        test_file = get_test_loc('unicode/not-unicode.ABOUT')
        a = model.About()
        a.load(test_file)
        err = a.errors[0]
        self.assertEqual(CRITICAL, err.severity)
        self.assertTrue('Cannot load invalid ABOUT file' in err.message)
        self.assertTrue('UnicodeDecodeError' in err.message)

    def test_as_dict_load_dict_is_idempotent(self):
        test = {'about_resource': u'.',
                 'author': u'',
                 'copyright': u'Copyright (c) 2013-2014 nexB Inc.',
                u'custom1': u'some custom',
                u'custom_empty': u'',
                 'description': u'AboutCode is a tool\nfor files.',
                 'license': u'apache-2.0',
                 'name': u'AboutCode',
                 'owner': u'nexB Inc.'}

        a = model.About()
        base_dir = 'some_dir'
        a.load_dict(test, base_dir)
        as_dict = a.as_dict(with_paths=False, with_absent=False,
                           with_empty=True)
        self.assertEqual(test, dict(as_dict))

    def check_csvs(self, expected, result):
        """
        Assert that the content of two CSV file locations are equal.
        """
        expected = [d.items() for d in load_csv(expected)]
        result = [d.items() for d in load_csv(result)]
        for ie, expect in enumerate(expected):
            res = result[ie]
            for ii, exp in enumerate(expect):
                r = res[ii]
                self.assertEqual(exp, r)

    def test_to_csv(self):
        path = 'load/this.ABOUT'
        test_file = get_test_loc(path)
        a = model.About(location=test_file, about_file_path=path)

        csv_file = get_temp_file()
        model.to_csv([a], csv_file)

        expected = get_test_loc('load/expected.csv')
        self.check_csvs(expected, csv_file)


class CollectorTest(unittest.TestCase):

    def test_collect_inventory_in_directory_with_correct_about_file_path(self):
        self.maxDiff = None
        test_loc = get_test_loc('collect-inventory-errors')
        _errors, abouts = model.collect_inventory(test_loc)
        self.assertEqual(2, len(abouts))

        expected = ['collect-inventory-errors/non-supported_date_format.ABOUT',
                    'collect-inventory-errors/supported_date_format.ABOUT']
        result = [a.about_file_path for a in abouts]
        self.assertEqual(sorted(expected), sorted(result))

    def test_collect_inventory_return_errors(self):
        test_loc = get_test_loc('collect-inventory-errors')
        errors, _abouts = model.collect_inventory(test_loc)
        expected_errors = [
            Error(INFO, u'Field date is a custom field'),
            Error(CRITICAL, u'Field about_resource: Path distribute_setup.py not found'),
            Error(INFO, u'Field date is a custom field'),
            Error(CRITICAL, u'Field about_resource: Path date_test.py not found')]
        self.assertEqual(sorted(expected_errors), sorted(errors))

    def test_collect_inventory_can_collect_a_single_file(self):
        test_loc = get_test_loc('thirdparty/django_snippets_2413.ABOUT')
        _errors, abouts = model.collect_inventory(test_loc)
        self.assertEqual(1, len(abouts))
        expected = ['thirdparty/django_snippets_2413.ABOUT']
        result = [a.about_file_path for a in abouts]
        self.assertEqual(expected, result)

    def test_collect_inventory_return_no_warnings(self):
        test_loc = get_test_loc('allAboutInOneDir')
        errors, _abouts = model.collect_inventory(test_loc)
        expected_errors = []
        result = [(level, e) for level, e in errors if level > about_code_tool.INFO]
        self.assertEqual(expected_errors, result)

    def test_collect_inventory_populate_about_file_path(self):
        test_loc = get_test_loc('parse/complete')
        errors, abouts = model.collect_inventory(test_loc)
        self.assertEqual([], errors)
        expected = 'complete/about.ABOUT'
        result = abouts[0].about_file_path
        self.assertEqual(expected, result)

    def test_collect_inventory_works_with_relative_paths(self):
        model.collect_inventory('.')
        model.collect_inventory('')
        model.collect_inventory('./etc')


class GroupingsTest(unittest.TestCase):

    def test_unique(self):
        base_dir = 'some_dir'
        test = {'about_resource': u'.',
                 'author': u'',
                 'copyright': u'Copyright (c) 2013-2014 nexB Inc.',
                u'custom1': u'some custom',
                u'custom_empty': u'',
                 'description': u'AboutCode is a tool\nfor files.',
                 'license': u'apache-2.0',
                 'name': u'AboutCode',
                 'owner': u'nexB Inc.'}

        a = model.About()
        a.load_dict(test, base_dir)

        b = model.About()
        b.load_dict(test, base_dir)
        abouts = [a, b]
        results = model.unique(abouts)
        self.assertEqual([a], results)

    def test_by_license(self):
        base_dir = 'some_dir'
        a = model.About()
        a.load_dict({'license': u'apache-2.0\n cddl-1.0', }, base_dir)
        b = model.About()
        b.load_dict({'license': u'apache-2.0', }, base_dir)
        c = model.About()
        c.load_dict({}, base_dir)
        d = model.About()
        d.load_dict({'license': u'bsd', }, base_dir)

        abouts = [a, b, c, d]
        results = model.by_license(abouts)
        expected = OrderedDict([
                                ('', [c]),
                                ('apache-2.0', [a,b]),
                                ('bsd', [d]),
                                ('cddl-1.0', [a]),
                                ])
        self.assertEqual(expected, results)

    def test_by_name(self):
        base_dir = 'some_dir'
        a = model.About()
        a.load_dict({'name': u'apache', 'version': u'1.1' }, base_dir)
        b = model.About()
        b.load_dict({'name': u'apache', 'version': u'1.2' }, base_dir)
        c = model.About()
        c.load_dict({}, base_dir)
        d = model.About()
        d.load_dict({'name': u'eclipse', 'version': u'1.1' }, base_dir)

        abouts = [a, b, c, d]
        results = model.by_name(abouts)
        expected = OrderedDict([
                                ('', [c]),
                                ('apache', [a,b]),
                                ('eclipse', [d]),
                                ])
        self.assertEqual(expected, results)

