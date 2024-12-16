from pydantic import (
    BaseSettings,
)


class Settings(BaseSettings):
    log_interval: int = 1
    """日志记录间隔,单位:秒"""
    link_check_interval: int = 2
    """连接检测间隔,单位:秒"""
    cpu_warning: float = 100.0
    """cpu检测报警百分比,单位%"""
    memory_warning: float = 100.0
    """memory检测报警百分比,单位%"""
    upload_speed_warning: int = 1024 * 1024 * 1024
    """上传速度警报百分比,单位B"""
    download_speed_warning: int = 1024 * 1024 * 1024
    """下载速度警报百分比,单位B"""

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
