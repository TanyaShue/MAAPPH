import json
from dataclasses import dataclass, asdict

@dataclass
class AdbConfig:
    adb_path: str
    adb_address: str
    screencap_methods: int
    input_methods: int
    config: dict

@dataclass
class Config:
    adb_config: AdbConfig
    log_level: str
    maa_user_path: str
    maa_resource_path: str


    @classmethod
    def from_file(cls, file_path):
        """从 JSON 文件读取配置"""
        with open(file_path, 'r', encoding='utf-8') as file:
            config_data = json.load(file)
        return cls(
            adb_config=AdbConfig(**config_data['adb_config']),
            log_level=config_data.get('log_level', 'INFO'),
            maa_user_path=config_data.get('maa_user_path', './'),
            maa_resource_path=config_data.get('maa_resource_path', './sample/resource')
        )

    def to_file(self, file_path):
        data = {'adb_config': asdict(self.adb_config), 'log_level': self.log_level, 'maa_user_path': self.maa_user_path, 'maa_resource_path': self.maa_resource_path}
        json.dump(data, open(file_path, 'w'), indent=4)