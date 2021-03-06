from __future__ import absolute_import
from lintreview.review import Problems, Comment
from lintreview.tools.csslint import Csslint
from unittest import TestCase
from nose.tools import eq_, assert_in
from tests import root_dir, requires_image


class TestCsslint(TestCase):

    fixtures = [
        'tests/fixtures/csslint/no_errors.css',
        'tests/fixtures/csslint/has_errors.css',
    ]

    def setUp(self):
        self.problems = Problems()
        self.tool = Csslint(self.problems, base_path=root_dir)

    def test_match_file(self):
        self.assertFalse(self.tool.match_file('test.php'))
        self.assertFalse(self.tool.match_file('dir/name/test.py'))
        self.assertFalse(self.tool.match_file('test.py'))
        self.assertTrue(self.tool.match_file('test.css'))
        self.assertTrue(self.tool.match_file('dir/name/test.css'))

    @requires_image('nodejs')
    def test_check_dependencies(self):
        self.assertTrue(self.tool.check_dependencies())

    @requires_image('nodejs')
    def test_process_files__one_file_pass(self):
        self.tool.process_files([self.fixtures[0]])
        eq_([], self.problems.all(self.fixtures[0]))

    @requires_image('nodejs')
    def test_process_files__one_file_fail(self):
        self.tool.process_files([self.fixtures[1]])
        problems = self.problems.all(self.fixtures[1])
        eq_(2, len(problems))

        fname = self.fixtures[1]
        eq_(fname, problems[0].filename)
        eq_(1, problems[0].line)
        assert_in("Warning - Don't use IDs in selectors.", problems[0].body)

        eq_(fname, problems[1].filename)
        eq_(2, problems[1].line)
        assert_in("Warning - Using width with padding", problems[1].body)

    @requires_image('nodejs')
    def test_process_files_two_files(self):
        self.tool.process_files(self.fixtures)

        eq_([], self.problems.all(self.fixtures[0]))

        problems = self.problems.all(self.fixtures[1])
        eq_(2, len(problems))

    @requires_image('nodejs')
    def test_process_files_with_config(self):
        config = {
            'ignore': 'box-model'
        }
        tool = Csslint(self.problems, config, root_dir)
        tool.process_files([self.fixtures[1]])

        problems = self.problems.all(self.fixtures[1])

        eq_(1, len(problems), 'Config file should lower error count.')

    @requires_image('nodejs')
    def test_process_files_with_config_with_shell_injection(self):
        config = {
            'ignore': '`cat /etc/passwd`'
        }
        tool = Csslint(self.problems, config, root_dir)
        tool.process_files([self.fixtures[1]])

        problems = self.problems.all(self.fixtures[1])
        assert len(problems) > 0, 'Shell injection fale'
