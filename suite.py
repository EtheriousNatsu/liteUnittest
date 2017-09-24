#!/usr/bin/env python
# encoding: utf-8


"""
@version: 2.7
@author: 'john'
@time: 2017/9/24 上午2:14
@contact: zhouqiang847@gmail.com
"""
import case


class BaseTestSuite(object):
    """A simple test suite that doesn't provide class or module shared fixtures.
    """

    def __init__(self, tests=()):
        self._tests = []
        self.addTests(tests)

    def addTests(self, tests):
        if isinstance(tests, basestring):
            raise TypeError("tests must be an iterable of tests, not a string")
        for test in tests:
            self.addTest(test)

    def addTest(self, test):
        # sanity checks
        if not hasattr(test, '__call__'):
            raise TypeError("{} is not callable".format(repr(test)))
        if isinstance(test, type) and issubclass(test,
                                                 (case.TestCase, TestSuite)):
            raise TypeError("TestCases and TestSuites must be instantiated "
                            "before passing them to addTest()")
        self._tests.append(test)

    def __iter__(self):
        return iter(self._tests)

    def __call__(self, *args, **kwds):
        return self.run(*args, **kwds)

    # def run(self, result):
    #     raise NotImplementedError




class TestSuite(BaseTestSuite):
    """A test suite is a composite test consisting of a number of TestCases.

        For use, create an instance of TestSuite, then add test case instances.
        When all tests have been added, the suite can be passed to a test
        runner, such as TextTestRunner. It will run the individual test cases
        in the order in which they were added, aggregating the results. When
        subclassing, do not forget to call the base class constructor.
    """

    def run(self, result):
        # topLevel = False
        # if getattr(result, '_testRunEntered', False) is False:
        #     result._testRunEntered = topLevel = True
        for test in self:
            if result.shouldStop:
                break
            if _isnotsuite(test):
                self._tearDownPreviousClass(test, result)
                # self._handleModuleFixture(test, result)
                self._handleClassSetUp(test, result)
                result._previousTestClass = test.__class__

                # if (getattr(test.__class__, '_classSetupFailed', False) or
                #     getattr(result, '_moduleSetUpFailed', False)):
                #     continue

                if (getattr(test.__class__, '_classSetupFailed', False)):
                    continue

            # run test
            test(result)
        # if topLevel:
        self._tearDownPreviousClass(None, result)
        # self._handleModuleTearDown(result)
        # result._testRunEntered = False
        return result



    def _tearDownPreviousClass(self, test, result):
        previousClass = getattr(result, '_previousTestClass', None)
        currentClass = test.__class__
        if currentClass == previousClass:
            return
        if getattr(previousClass, '_classSetupFailed', False):
            return
        # if getattr(result, '_moduleSetUpFailed', False):
        #     return
        if getattr(previousClass, "__unittest_skip__", False):
            return

        tearDownClass = getattr(previousClass, 'tearDownClass', None)
        if tearDownClass is not None:
            # _call_if_exists(result, '_setupStdout')
            try:
                tearDownClass()
            except Exception, e:
                pass
                # if isinstance(result, _DebugResult):
                #     raise
                # className = util.strclass(previousClass)
                # errorName = 'tearDownClass (%s)' % className
                # self._addClassOrModuleLevelException(result, e, errorName)
            finally:
                pass
                # _call_if_exists(result, '_restoreStdout')


    def _handleClassSetUp(self, test, result):
        previousClass = getattr(result, '_previousTestClass', None)
        currentClass = test.__class__
        if currentClass == previousClass:
            return
        # if result._moduleSetUpFailed:
        #     return
        if getattr(currentClass, "__unittest_skip__", False):
            return

        try:
            currentClass._classSetupFailed = False
        except TypeError:
            # test may actually be a function
            # so its class will be a builtin-type
            pass

        setUpClass = getattr(currentClass, 'setUpClass', None)
        if setUpClass is not None:
            # _call_if_exists(result, '_setupStdout')
            try:
                setUpClass()
            except Exception as e:
                pass
                # if isinstance(result, _DebugResult):
                #     raise
                currentClass._classSetupFailed = True
                # className = util.strclass(currentClass)
                # errorName = 'setUpClass (%s)' % className
                # self._addClassOrModuleLevelException(result, e, errorName)
            finally:
                pass
                # _call_if_exists(result, '_restoreStdout')



def _isnotsuite(test):
    "A crude way to tell apart testcases and suites with duck-typing"
    try:
        iter(test)
    except TypeError:
        return True
    return False