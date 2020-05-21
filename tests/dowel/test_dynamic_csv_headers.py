#from unittest import mock
import os

import pytest
from flaky import flaky


class TestDynamicHeaders:

    def clean_start(self):
        try:
            os.remove('out.csv')
            os.remove('out_temp.csv')
        except OSError:
            pass

    def test_static_headers(self):
        self.clean_start()
        import dowel
        from dowel import logger, tabular
        logger.add_output(dowel.StdOutput())
        logger.add_output(dowel.CsvOutput('out.csv'))

        for i in range(15):
            logger.push_prefix('itr {} '.format(i))
            
            tabular.record('itr', i)
            tabular.record('loss', 100.0 / (2 + i))

            logger.log(tabular)

            logger.pop_prefix()
            logger.dump_all()

        tabular.clear()
        logger.remove_all()


    @flaky(max_runs=3)
    def test_dynamic_single_increase_end(self):
        self.clean_start()
        import dowel
        from dowel import logger, tabular
        logger.add_output(dowel.StdOutput())
        logger.add_output(dowel.CsvOutput('out.csv'))

        for i in range(15):
            logger.push_prefix('itr {} '.format(i))
            
            tabular.record('itr', i)
            tabular.record('loss', 100.0 / (2 + i))

            if i > 0:
                tabular.record('new_data', i)

            logger.log(tabular)

            logger.pop_prefix()
            logger.dump_all()

        tabular.clear()
        logger.remove_all()
        
        
    @flaky(max_runs=3)
    def test_dynamic_multi_increase_end(self):
        self.clean_start()
        import dowel
        from dowel import logger, tabular
        logger.add_output(dowel.StdOutput())
        logger.add_output(dowel.CsvOutput('out.csv'))

        for i in range(15):
            logger.push_prefix('itr {} '.format(i))
            
            tabular.record('itr', i)
            tabular.record('loss', 100.0 / (2 + i))

            if i > 0:
                tabular.record('n1_data', i)
            if i > 10:
                tabular.record('n2_data', i)
                tabular.record('n3_data', i)

            logger.log(tabular)

            logger.pop_prefix()
            logger.dump_all()

        tabular.clear()
        logger.remove_all()


    @flaky(max_runs=3)
    def test_dynamic_single_increase_with_decrease(self):
        self.clean_start()
        import dowel
        from dowel import logger, tabular
        logger.add_output(dowel.StdOutput())
        logger.add_output(dowel.CsvOutput('out.csv'))

        for i in range(15):
            logger.push_prefix('itr {} '.format(i))
            
            tabular.record('itr', i)
            tabular.record('loss', 100.0 / (2 + i))

            if i > 0 and i < 7:
                tabular.record('new_data', i)

            logger.log(tabular)

            logger.pop_prefix()
            logger.dump_all()
        
        tabular.clear()
        logger.remove_all()


    @flaky(max_runs=3)
    def test_dynamic_multi_increase_with_decrease(self):
        self.clean_start()
        import dowel
        from dowel import logger, tabular
        logger.add_output(dowel.StdOutput())
        logger.add_output(dowel.CsvOutput('out.csv'))

        for i in range(15):
            logger.push_prefix('itr {} '.format(i))
            
            tabular.record('itr', i)
            tabular.record('loss', 100.0 / (2 + i))

            if i > 0 and i < 7:
                tabular.record('n1_data', i)
            if i > 12:
                tabular.record('n2_data', i)
                tabular.record('n3_data', i)

            logger.log(tabular)

            logger.pop_prefix()
            logger.dump_all()

        tabular.clear()
        logger.remove_all()


    @flaky(max_runs=3)
    def test_dynamic_overlap_increase_decrease(self):
        self.clean_start()
        import dowel
        from dowel import logger, tabular
        logger.add_output(dowel.StdOutput())
        logger.add_output(dowel.CsvOutput('out.csv'))

        for i in range(15):
            logger.push_prefix('itr {} '.format(i))
            
            tabular.record('itr', i)
            tabular.record('loss', 100.0 / (2 + i))

            if i > 0 and i < 8:
                tabular.record('n1_data', i)
            if i > 4:
                tabular.record('n2_data', i)

            logger.log(tabular)

            logger.pop_prefix()
            logger.dump_all()

        tabular.clear()
        logger.remove_all()


    @flaky(max_runs=3)
    def test_static_tensorboard_compatibility(self):
        self.clean_start()
        import dowel
        from dowel import logger, tabular
        logger.add_output(dowel.StdOutput())
        logger.add_output(dowel.CsvOutput('out.csv'))
        logger.add_output(dowel.TensorBoardOutput('tensorboard_logdir'))

        for i in range(15):
            logger.push_prefix('itr {} '.format(i))
            
            tabular.record('itr', i)
            tabular.record('loss', 100.0 / (2 + i))

            logger.log(tabular)

            logger.pop_prefix()
            logger.dump_all()

        tabular.clear()
        logger.remove_all()


    @flaky(max_runs=3)
    def test_dynamic_tensorboard_compatibility(self):
        self.clean_start()
        import dowel
        from dowel import logger, tabular
        logger.add_output(dowel.StdOutput())
        logger.add_output(dowel.CsvOutput('out.csv'))
        logger.add_output(dowel.TensorBoardOutput('tensorboard_logdir'))

        for i in range(15):
            logger.push_prefix('itr {} '.format(i))
            
            tabular.record('itr', i)
            tabular.record('loss', 100.0 / (2 + i))

            if i > 1:
                tabular.record('new_data', i)

            logger.log(tabular)

            logger.pop_prefix()
            logger.dump_all()

        tabular.clear()
        logger.remove_all()

    @flaky(max_runs=3)
    def test_no_log(self):
        self.clean_start()
        import dowel
        from dowel import logger, tabular
        logger.add_output(dowel.StdOutput())
        logger.add_output(dowel.CsvOutput('out.csv'))

        for i in range(4):
            logger.push_prefix('itr {} '.format(i))

            if i < 2:
                tabular.record('itr', i)
                tabular.record('loss', 100.0 / (2 + i))

            logger.log(tabular)
            logger.pop_prefix()
            logger.dump_all()

        tabular.clear()
        logger.remove_all()
