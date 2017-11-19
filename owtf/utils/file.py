class FileOperations(object):
    
    @staticmethod
    @catch_io_errors
    def create_missing_dirs(path):
        """Creates missing directories if not already present

        :param path: Path of the directory to create
        :type path: `str`
        :return:
        :rtype: None
        """
        # truncate filepath to 255 char (*nix limit)
        # See issue #521
        directory = path[:255]
        if os.path.isfile(directory):
            directory = os.path.dirname(directory)
        if not os.path.exists(directory):
            # Create any missing directories.
            FileOperations.make_dirs(directory)

    @staticmethod
    @catch_io_errors
    def codecs_open(*args, **kwargs):
        """ A wrapper for Python codes with additional argument support"""
        return codecs.open(*args, **kwargs)

    @staticmethod
    @catch_io_errors
    def dump_file(filename, contents, directory):
        """Create a file with user supplied contents

        :param filename: File to be created
        :type filename: `str`
        :param contents: Contents to write to the file
        :type contents: `str`
        :param directory: Directory where the file will be saved
        :type directory: `str`
        :return: The final full path of the created file
        :rtype: `str`
        """
        save_path = os.path.join(directory, wipe_bad_chars(filename))
        FileOperations.create_missing_dirs(directory)
        with FileOperations.codecs_open(save_path, 'wb', 'utf-8') as f:
            f.write(contents.decode('utf-8', 'replace'))
        return save_path

    @staticmethod
    @catch_io_errors
    def make_dirs(*args, **kwargs):
        return os.makedirs(*args, **kwargs)

    @staticmethod
    @catch_io_errors
    def open(*args, **kwargs):
        return open(*args, **kwargs)

    @staticmethod
    @catch_io_errors
    def rm_tree(*args, **kwargs):
        return shutil.rmtree(*args, **kwargs)

    @staticmethod
    @catch_io_errors
    def mkdir(*args, **kwargs):
        return os.mkdir(*args, **kwargs)


def directory_access(path, mode):
    """Check if a directory can be accessed in the specified mode by the current user.

    :param str path: Directory path.
    :param str mode: Access type.

    :return: Valid access rights
    :rtype: `str`
    """
    try:
        temp_file = tempfile.NamedTemporaryFile(
            mode=mode, dir=path, delete=True)
    except (IOError, OSError):
        return False
    return True


def catch_io_errors(func):
    """Decorator on I/O functions.

    If an error is detected, force OWTF to quit properly.
    """
    def io_error(*args, **kwargs):
        """Call the original function while checking for errors.

        If `owtf_clean` parameter is not explicitely passed or if it is
        set to `True`, it force OWTF to properly exit.

        """
        owtf_clean = kwargs.pop('owtf_clean', True)
        try:
            return func(*args, **kwargs)
        except (OSError, IOError) as e:
            if owtf_clean:
                error_handler = ServiceLocator.get_component("error_handler")
                if error_handler:
                    error_handler.abort_framework(
                        "Error when calling '%s'! %s." % (func.__name__, str(e)))
            raise e
    return io_error


def get_file_as_list(filename):
    """Get file contents as a list

    :param filename: File path
    :type filename: `str`
    :return: Output list of the content
    :rtype: `list`
    """
    try:
        with open(filename, 'r') as f:
            output = f.read().split("\n")
            cprint("Loaded file: %s" % filename)
    except IOError:
        log("Cannot open file: %s (%s)" % (filename, str(sys.exc_info())))
        output = []
    return output
