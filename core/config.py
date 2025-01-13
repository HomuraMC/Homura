import os

from omegaconf import DictConfig, OmegaConf


class Config:
    _instance = None
    default_config = {
        "detail": {
            "name": "HomuraMC",
            "motd": "A HomuraMC server",
        },
        "server": {
            "max_players": 20,
            "online_mode": True,
            "compression_threshold": 256,
        },
        "listen": {
            "ip": "0.0.0.0",
            "port": 25565,
        },
    }
    config: DictConfig = None

    def __new__(cls, file_path="homura.yml"):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.config = cls.load_config(file_path)
        return cls._instance

    @classmethod
    def load_config(cls, file_path):
        if not os.path.exists(file_path):
            cls.write_default_config(file_path)
        config = OmegaConf.load(file_path)
        return config

    @classmethod
    def write_default_config(cls, file_path):
        default_conf = OmegaConf.create(cls.default_config)
        with open(file_path, "w") as f:
            OmegaConf.save(config=default_conf, f=f.name)
