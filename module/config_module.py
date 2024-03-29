"""
Config Manager
"""
import configparser
from utils.file_utils import check_file_valid
from utils.exception import ConfigLoaderError


class ConfigLoader:
    """
    config loading helper
    """

    def __init__(self, config_dir: str):
        if check_file_valid(config_dir):
            self.config = configparser.ConfigParser()
            self.config.read(config_dir)
        else:
            raise ConfigLoaderError("cannot open config file")

    def game_save(self) -> dict:
        """
        get game_memory config

        @return: game_memory config
        """
        return dict(self.config["GameSave"])

    def engine(self) -> dict:
        """
        get kernel config

        @return: kernel config
        """
        return dict(self.config["Engine"])

    def log_file(self) -> dict:
        """
        get log_file config

        @return: log_file config
        """
        return dict(self.config["LogFile"])

    def resources(self) -> dict:
        """
        get resources config

        @return: resources config
        """
        return dict(self.config["Resources"])

    def project(self) -> dict:
        """
        get project config

        @return: project config
        """
        return dict(self.config["Project"])

    def version(self) -> dict:
        """
        get version config

        @return: version config
        """
        return dict(self.config["Version"])

    def cors(self) -> dict:
        """
        get CORS config

        @return: cors config
        """
        return dict(self.config["CORS"])

    def get_all_section(self) -> list:
        """
        get all sections in config file

        @return: all sections in config file
        """
        return list(self.config.sections())
