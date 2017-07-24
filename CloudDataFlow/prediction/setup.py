import subprocess
from distutils.command.build import build as _build
import setuptools

class build(_build): 
  sub_commands = _build.sub_commands + [('CustomCommands', None)]

class CustomCommands(setuptools.Command):

  def initialize_options(self):
    pass

  def finalize_options(self):
    pass

  def RunCustomCommand(self, command_list):
    print('Running command: %s' % command_list)
    p = subprocess.Popen(
        command_list,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout_data, _ = p.communicate()
    print('Command output: %s' % stdout_data)
    if p.returncode != 0:
      raise RuntimeError(
          'Command %s failed: exit code: %s' % (command_list, p.returncode))

  def run(self):
    for command in CUSTOM_COMMANDS:
      self.RunCustomCommand(command)
CUSTOM_COMMANDS = [
  
  #Get cmake and git
  ['git','clone', 'https://github.com/bw4sz/CameraMeerkat.git', '--depth', '1']]

REQUIRED_PACKAGES = ['numpy']

setuptools.setup(
    name='CameraMeerkat',
    version='0.0.1',
    description='Running CameraMeerkat in the Cloud',
    packages=setuptools.find_packages())
