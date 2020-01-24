# Copyright 2015 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).


from colors import blue, cyan, green

from pants.help.build_dictionary_info_extracter import BuildDictionaryInfoExtracter
from pants.task.console_task import ConsoleTask


class TargetsHelp(ConsoleTask):
  """List available target types."""

  _register_console_transitivity_option = False

  @classmethod
  def register_options(cls, register):
    super().register_options(register)
    register('--details', help='Show details about this target type.')
    register(
      '--transitive', type=bool, default=True, fingerprint=True,
      removal_version="1.27.0.dev0",
      removal_hint="This option has no impact on the goal `targets`.",
    )

  def console_output(self, targets):
    buildfile_aliases = self.context.build_configuration.registered_aliases()
    extracter = BuildDictionaryInfoExtracter(buildfile_aliases)

    alias = self.get_options().details
    if alias:
      tti = next(x for x in extracter.get_target_type_info() if x.symbol == alias)
      yield blue('\n{}\n'.format(tti.description))
      yield blue('{}('.format(alias))

      for arg in tti.args:
        default = green('(default: {})'.format(arg.default) if arg.has_default else '')
        yield '{:<30} {}'.format(
          cyan('  {} = ...,'.format(arg.name)),
          ' {}{}{}'.format(arg.description, ' ' if arg.description else '', default))

      yield blue(')')
    else:
      for tti in extracter.get_target_type_info():
        yield '{} {}'.format(cyan('{:>30}:'.format(tti.symbol)), tti.description)
