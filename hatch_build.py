import os
import sys
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
import json
import os
import sys

from jupyter_client.kernelspec import KernelSpecManager
from tempfile import TemporaryDirectory

kernel_json = {
    "argv": [sys.executable, "-m", "ijava", "-f", "{connection_file}"],
    "display_name": "IJava",
    "language": "java",
}

class CustomHook(BuildHookInterface):
    def initialize(self, version, build_data):

        here = os.path.abspath(os.path.dirname(__file__))
        sys.path.insert(0, here)
        prefix = os.path.join(here, 'data_kernelspec')

        with TemporaryDirectory() as td:
            os.chmod(td, 0o755) # Starts off as 700, not user readable
            with open(os.path.join(td, 'kernel.json'), 'w') as f:
                json.dump(kernel_json, f, sort_keys=True)
            print('Installing Jupyter kernel spec')

            KernelSpecManager().install_kernel_spec(td, 'ijava', user=True)
