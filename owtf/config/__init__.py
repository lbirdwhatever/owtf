from .service import load_config_db_file, get_profile_path, load_config_from_file, \
    framework_config_file_path


REPLACEMENT_DELIMITER = "@@@"
REPLACEMENT_DELIMITER_LENGTH = len(REPLACEMENT_DELIMITER)
CONFIG_TYPES = ['string', 'other']

target = None
initialize_attributes()
# key can consist alphabets, numbers, hyphen & underscore.
search_regex = re.compile('%s([a-zA-Z0-9-_]*?)%s' %
                          (REPLACEMENT_DELIMITER, REPLACEMENT_DELIMITER))
# Available profiles = g -> General configuration, n -> Network plugin
# order, w -> Web plugin order, r -> Resources file


def initialize_attributes():
    """Initializes the attributes for the config dictionary

    :return: None
    :rtype: None
    """
    config = defaultdict(list)  # General configuration information.
    for type in CONFIG_TYPES:
        config[type] = {}


load_config_db_file(get_profile_path('GENERAL_PROFILE'))
load_config_from_file(framework_config_file_path())

