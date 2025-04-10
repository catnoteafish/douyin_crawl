import threading
import time
import random
import uuid
from loguru import logger


# 生成随机睡眠时间
def random_sleep(min_time=1, max_time=3):
    """
    随机睡眠指定的时间范围，单位为秒。
    :param min_time: 最小睡眠时间（默认为1秒）
    :param max_time: 最大睡眠时间（默认为3秒）
    """
    sleep_time = random.randint(min_time, max_time)
    logger.info(f"随机睡眠 {sleep_time} 秒...")
    time.sleep(sleep_time)


def sanitize_filename(filename, max_len=100, ellipsis_str='...'):
    """
    去除操作系统不支持的文件名字符，并处理过长的文件名。
    :param filename: 原始文件名
    :param max_len: 文件名最大长度（默认为100）
    :param ellipsis_str: 省略符号（默认为'...'）
    :return: 处理后的文件名
    """
    if len(filename) == 0:
        logger.warning("文件名为空，生成随机UUID作为文件名。")
        return str(uuid.uuid4())
    
    invalid_chars = '<>:"/\\|?*\n\t\r'
    sanitized_filename = ''.join('' if c in invalid_chars else c for c in filename)
    sanitized_filename = sanitized_filename.strip(' .')
    
    if len(sanitized_filename) > max_len:
        if len(ellipsis_str) >= max_len:
            raise ValueError("省略符号长度不能大于或等于最大文件名长度。")
        head_len = (max_len - len(ellipsis_str)) // 2
        tail_len = max_len - len(ellipsis_str) - head_len
        sanitized_filename = (sanitized_filename[:head_len] + ellipsis_str +
                              sanitized_filename[-tail_len:])
    
    if len(sanitized_filename) == 0:
        logger.warning("处理后文件名为空，生成随机UUID作为文件名。")
        return str(uuid.uuid4())
    
    return sanitized_filename


class IDGenerator:
    # 类变量，作为全局自增ID的计数器
    _last_id: int = 0
    # 锁，确保线程安全
    _lock: threading.Lock = threading.Lock()

    @classmethod
    def generate_unique_id(cls) -> int:
        """线程安全地生成并返回一个新的全局自增ID"""
        with cls._lock:
            cls._last_id += 1
            logger.debug(f"生成新的唯一ID: {cls._last_id}")
            return cls._last_id


if __name__ == '__main__':
    print(IDGenerator.generate_unique_id())

