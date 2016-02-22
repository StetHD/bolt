import unittest

import bolt._btconfig as config
import bolt._btregistry as registry

import bolt._btrunner as runner


class TestTaskRunner(unittest.TestCase):

    def setUp(self):
        self.setUpRegistry()
        self.setUpConfig()
        self.subject = runner.TaskRunner(self.config_mgr, self.registry)
        self.executed_tasks = []
        return super(TestTaskRunner, self).setUp()


    def setUpRegistry(self):
        self.registry = registry.TaskRegistry()
        self.registry.register_task('task_1', self.task_1_callback)
        self.registry.register_task('task_2', self.task_2_callback)
        self.registry.register_task('invalid', self.invalid_task)
        self.registry.register_task('multi_task', ['task_1', 'task_2'])
        self.registry.register_task('configurable', self.configurable_task)


    def setUpConfig(self):
        self.config = {
                'configurable': {
                    'param': 'value'
                }
            }
        self.config_mgr = config.ConfigurationManager(self.config)
    

    def test_raises_runs_the_specified_task(self):
        self.given('task_1')
        self.expect_executed('task_1')


    def test_configuration_is_passed_to_task_by_named_parameter(self):
        self.given('task_2')
        self.expect_executed('task_2')


    def test_raises_if_task_definition_does_not_meet_spec(self):
        with self.assertRaises(Exception):
            self.given('invalid')


    def test_executes_all_tasks_in_multi_task(self):
        self.given('multi_task')
        self.expect_executed('task_1')
        self.expect_executed('task_2')


    def test_task_is_executed_with_correct_configuration(self):
        self.given('configurable')
        self.expect_executed('configurable')


    def test_build_is_enforced_before_run(self):
        with self.assertRaises(Exception):
            subject = runner.TaskRunner(self.config_mgr, self.registry)
            subject.run()


    def test_build_fails_if_a_task_is_not_registered(self):
        with self.assertRaises(Exception):
            self.subject.build('inexistent')


    def given(self, task_name):
        self.subject.build(task_name)
        self.subject.run()


    def expect_executed(self, task_name):
        self.assertIn(task_name, self.executed_tasks)


    def task_1_callback(self, config):
        self.executed_tasks.append('task_1')


    def task_2_callback(self, **kwargs):
        config = kwargs.get('config')
        self.executed_tasks.append('task_2')


    def invalid_task(self, noconfig):
        pass


    def configurable_task(self, config):
        param = config.get('param')
        self.assertEqual(param, 'value')
        self.executed_tasks.append('configurable')



if __name__=='__main__':
    unittest.main()