from conans.errors import AuthenticationException
from conans.client.conan_api import Conan

try:
    import keyring
except ImportError:
    raise ImportError('keyring Module not available. \
                         Please install it using pip.')

try:
    import getpass
except ImportError:
    raise ImportError('getpass Module not available. \
                        Please install it using pip.')


def pre_download(output, reference, remote, **kwargs):
    _register_using_native_keyring(output, remote)


def pre_download_recipe(output, reference, remote, **kwargs):
    _register_using_native_keyring(output, remote)


def pre_download_package(output, reference, remote, **kwargs):
    _register_using_native_keyring(output, remote)


def pre_upload(output, reference, remote, **kwargs):
    _register_using_native_keyring(output, remote)


def pre_upload_recipe(output, reference, remote, **kwargs):
    _register_using_native_keyring(output, remote)


def pre_upload_package(output, reference, remote, **kwargs):
    _register_using_native_keyring(output, remote)


def _register_using_native_keyring(output, remote):    
    conan, _, _ = Conan.factory()
    user_list = conan.users_list(remote.name)
    authenticated, user_name = _get_default_remote_user(user_list)
    if user_name is None:
        output.info(
            "Anonymous login for remote '{}'. Set a user with 'conan user' command."
            .format(str(remote.name)))
        return
    if authenticated:
        return  # Already authenticated

    _check_keyring_backend_availability()
    passwd = keyring.get_password(remote.name, user_name)
    if passwd is None:
        passwd = unicode(getpass.getpass("Password for {} at {}:"
                         .format(user_name, remote.name)), 'utf8')
    valid = False
    while not valid:
        try:
            conan.authenticate(user_name, passwd, remote.name)
            keyring.set_password(remote.name, user_name, passwd)
            valid = True
        except AuthenticationException:
            output.info(
                "Credentials are invalid. Please, type credentials for {}."
                .format(remote.name))
            user_name = raw_input("Username: ")
            passwd = unicode(
                getpass.getpass("Password for {} at {}:"
                                .format(user_name, remote.name)), 'utf8')


def _check_keyring_backend_availability():
    kr = keyring.get_keyring()
    assert type(kr) != keyring.backends.fail.Keyring, \
        "There is no Keyring backend available. Install \
         the 'keyrings.alt' package via pip."


def _get_default_remote_user(user_list):
    return user_list['remotes'][0]['authenticated'], \
            user_list['remotes'][0]['user_name']
