from Versions import testVersions
testVersions()
import sys

from MonoMultiViewClassifiers import ExecClassif

ExecClassif.execClassif(sys.argv[1:])
