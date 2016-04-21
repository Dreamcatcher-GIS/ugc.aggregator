from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.distutils")

use_plugin("python.coverage")
use_plugin("python.pycharm")
# use_plugin("python.unittest")

name = "ugc.aggregator"
default_task = "publish"


@init
def set_properties(project):
    project.build_depends_on('mockito')
    project.set_property('unittest_module_glob', '*_test')
    project.version = "1.0"
    pass