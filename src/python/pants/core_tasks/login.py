# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

import getpass

from colors import cyan, green, red

from pants.auth.basic_auth import BasicAuth, BasicAuthCreds, Challenged
from pants.base.deprecated import deprecated_conditional
from pants.base.exceptions import TaskError
from pants.task.console_task import ConsoleTask


class Login(ConsoleTask):
  """Task to auth against some identity provider.

  :API: public
  """

  _register_console_transitivity_option = False

  @classmethod
  def subsystem_dependencies(cls):
    return super().subsystem_dependencies() + (BasicAuth,)

  @classmethod
  def supports_passthru_args(cls):
    return True

  @classmethod
  def register_options(cls, register):
    super().register_options(register)
    register(
      '--to', type=str, fingerprint=True,
      help='Log in to the given provider from the `--basic-auth-providers` option. For '
           'example, if you had defined in `--basic-auth-providers` that the provider `prod` '
           'points to the URL `https://app.pantsbuild.org/auth`, then you '
           'could here use the option `--login-to=prod` to login at '
           '`https://app.pantsbuild.org/auth`.'
    )
    register(
      '--transitive', type=bool, default=True, fingerprint=True,
      removal_version="1.27.0.dev0",
      removal_hint="This option has no impact on the goal `login`.",
    )

  def console_output(self, targets):
    if targets:
      raise TaskError('The login task does not take any target arguments.')

    deprecated_conditional(
      lambda: self.get_passthru_args(),
      removal_version='1.26.0.dev1',
      entity_description='Using passthrough args with `./pants login`',
      hint_message="Instead of passing the provider through `--login-passthrough-args` or the "
                   "style `./pants login -- prod`, use the option `--login-to`, such as "
                   "`./pants login --to=prod`.",
    )

    # TODO: When we have other auth methods (e.g., OAuth2), select one by provider name.
    requested_providers = list(filter(None, [self.get_options().to] + self.get_passthru_args()))
    if len(requested_providers) != 1:
      raise TaskError('Must specify exactly one provider.')
    provider = requested_providers[0]
    try:
      BasicAuth.global_instance().authenticate(provider)
      return ['', 'Logged in successfully using .netrc credentials.']
    except Challenged as e:
      creds = self._ask_for_creds(provider, e.url, e.realm)
      BasicAuth.global_instance().authenticate(provider, creds=creds)
    return ['', 'Logged in successfully.']

  @staticmethod
  def _ask_for_creds(provider, url, realm):
    print(green('\nEnter credentials for:\n'))
    print('{} {}'.format(green('Provider:'), cyan(provider)))
    print('{} {}'.format(green('Realm:   '), cyan(realm)))
    print('{} {}'.format(green('URL:     '), cyan(url)))
    print(red('\nONLY ENTER YOUR CREDENTIALS IF YOU TRUST THIS SITE!\n'))
    username = input(green('Username: '))
    password = getpass.getpass(green('Password: '))
    return BasicAuthCreds(username, password)
