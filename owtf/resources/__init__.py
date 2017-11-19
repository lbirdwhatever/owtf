from owtf.config.config import get_profile_path

from .service import load_resources_from_file


load_resources_from_file(get_profile_path("RESOURCES_PROFILE"))
