# -*- coding:utf-8 -*-

import sys
import logging

class mylog(object):
    """
    用于记录客户端登录的日志
    """

    def __init__(self,file=None):
        """
        初始化
        设置格式、以及向控制台和文件输出
        """
        
        self.logger=logging.getLogger("server_log")
        #设置格式
        log_format="[%(levelname)s] - [%(asctime)s] - %(message)s"
        formattter=logging.Formatter(fmt=log_format,datefmt='%d/%b/%Y-%H:%M:%S')
        #向控制台输出
        stream_handler=logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formattter)
        self.logger.addHandler(stream_handler)
        
        #如果设置了文件，就向文件输出
        if file is not None:
            file_handler=logging.FileHandler(filename=file,encoding="utf-8")
            file_handler.setFormatter(formattter)
            self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)

    def error_log(self,info):
        """
        错误日志
        """
        self.logger.error(info)
    
    def info_log(self,info):
        """
        正常消息
        """
        self.logger.info(info)
