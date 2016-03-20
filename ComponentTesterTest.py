import time
from hamcrest import *
from subprocess import call
from os.path import isfile
import unittest

from ComponentTester import ComponentTester


class TestComponentTester(unittest.TestCase):
    def setUp(self):
        self.defaultFileName = 'test_tasks/test_task.xml'
        if isfile(self.defaultFileName):
            call(['rm', self.defaultFileName])

    def test_component_tester_running(self):
        assert_that(ComponentTester(), is_not(None))

    def test_should_save_to_default_file_on_init(self):
        tester = ComponentTester()

        assert_that(isfile(self.defaultFileName), is_(True))

    def test_should_create_task_template_on_init(self):
        tester = ComponentTester()

        with open(self.defaultFileName) as file:
            contents = file.read()
        assert_that(contents, starts_with('<Task>'))
        assert_that(contents, ends_with('</Task>\n'))
        assert_that(contents, contains_string('<Subtasks>'))
        assert_that(contents, contains_string('</Subtasks>'))
        assert_that(contents, contains_string('<Subtask name="Main"'))
        assert_that(contents, contains_string('<DataStreams/>'))

    def test_should_create_task_with_default_executor_on_init(self):
        tester = ComponentTester()

        with open(self.defaultFileName) as file:
            contents = file.read()
        assert_that(contents, contains_string('<Executor name="Processing" period="1"/>'))

    def test_should_add_proper_component_to_task(self):
        tester = ComponentTester()

        tester.setComponent('Summator', 'CvBasic:Sum')

        with open(self.defaultFileName) as file:
            contents = file.read()
        assert_that(contents, contains_string('<Component bump="0" name="Summator" priority="1" type="CvBasic:Sum"/>'))

    def test_should_add_generator_to_components(self):
        tester = ComponentTester()

        tester.addGenerator('SampleGenerators:CvMatGenerator')

        with open(self.defaultFileName) as file:
            contents = file.read()
        assert_that(contents, contains_string(
                '<Component bump="0" name="Generator" priority="1" type="SampleGenerators:CvMatGenerator"/>'))

    def test_should_add_generator_with_specific_name_to_components(self):
        tester = ComponentTester()

        tester.addGenerator('SampleGenerators:CvMatGenerator', 'AnotherGenerator')

        with open(self.defaultFileName) as file:
            contents = file.read()
        assert_that(contents, contains_string(
            '<Component bump="0" name="AnotherGenerator" priority="1" type="SampleGenerators:CvMatGenerator"/>'))

    def test_should_add_sink(self):
        tester = ComponentTester()
        tester.addSink('SampleGenerators:CvMatSink')

        with open(self.defaultFileName) as file:
            contents = file.read()
        assert_that(contents, contains_string(
                '<Component bump="0" name="Sink" priority="1" type="SampleGenerators:CvMatSink"/>'))

    def test_should_add_new_datastream(self):
        tester = ComponentTester()

        tester.addDataStream('First', 'out_data', 'Second', 'in_data')

        with open(self.defaultFileName) as file:
            contents = file.read()
        assert_that(contents, contains_string('<Source name="First.out_data">\n\t\t\t<sink>Second.in_data</sink>'))

    def test_should_run_discode(self):
        tester = ComponentTester()
        if isfile(self.defaultFileName):
            call(['rm', self.defaultFileName])

        tester.start()

        output = tester.getOutput()
        assert_that(output, contains_string('\x1b[33mWARNING: \x1b[00mConfiguration file config.xml not found.\n'))

    def test_should_run_task_with_default_name(self):
        tester = ComponentTester()
        if isfile(self.defaultFileName):
            call(['rm', self.defaultFileName])

        tester.start()

        output = tester.getOutput()
        assert_that(output, contains_string('Configuration: File \'' + self.defaultFileName + '\' doesn\'t exist.'))

    # @unittest.skip('integration test skipped!')
    def test_should_run_specific_task(self):
        tester = ComponentTester()
        tester.taskName = 'SequenceViewer.xml'

        tester.start()
        time.sleep(.500)
        tester.runner.kill()

        output = tester.getOutput()
        assert_that(output, contains_string('Kopiowanie TASKA!'))

    # @unittest.skip('integration test skipped!')
    def test_should_stop_discode_manually(self):
        tester = ComponentTester()
        tester.start()
        time.sleep(5)

        tester.stop()

        output = tester.getOutput()
        assert_that(output, contains_string('Finishing DisCODe.'))
        assert_that(output, contains_string('Server stoped.'))

    # @unittest.skip('integration test skipped!')
    def test_should_stop_on_termination_statement(self):
        tester = ComponentTester()
        tester.taskName = 'SequenceViewer.xml'
        tester.setTerminationStatement('ERROR')
        tester.start()
        time.sleep(.500)

        output = tester.getOutput()
        assert_that(output, contains_string('Finishing DisCODe.'))
        assert_that(output, contains_string('Server stoped.'))

    # @unittest.skip('integration test skipped!')
    def test_should_check_component_output(self):
        tester = ComponentTester()
        # print('adding generator...')
        tester.addGenerator('SampleGenerators:CvMatGenerator', 'Generator1')
        tester.addGenerator('SampleGenerators:CvMatGenerator', 'Generator2')
        # print('adding component...')
        tester.setComponent('Summator', 'CvBasic:Sum')
        # print('adding component...')
        tester.addSink('SampleGenerators:CvMatSink')
        tester.addDataStream('Generator1', 'out_img', 'Summator', 'in_img1')
        tester.addDataStream('Generator2', 'out_img', 'Summator', 'in_img2')
        tester.addDataStream('Summator', 'out_img', 'Sink', 'in_img')
        tester.setTerminationStatement('END OF SEQUENCE')
        # print('Task body:')
        # print(tester.taskBuilder.getTaskBody())

        tester.start()

        output = tester.getOutput()
        # print(output)
        # print('finished printing output')
        assert_that(output, contains_string('[2, 2, 2, 2;\n  2, 2, 2, 2;\n  2, 2, 2, 2]'))


if __name__ == '__main__':
    unittest.main(warnings='ignore', verbosity=2)
