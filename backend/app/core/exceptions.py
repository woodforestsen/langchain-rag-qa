"""自定义异常类"""


class AppException(Exception):
    """应用基础异常"""
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


class UnauthorizedException(AppException):
    """未认证异常"""
    def __init__(self, message: str = "请先登录"):
        super().__init__(message, code=401)


class ForbiddenException(AppException):
    """无权限异常"""
    def __init__(self, message: str = "您没有权限执行此操作"):
        super().__init__(message, code=403)


class NotFoundException(AppException):
    """资源未找到异常"""
    def __init__(self, message: str = "请求的资源不存在"):
        super().__init__(message, code=404)


class ConflictException(AppException):
    """资源冲突异常"""
    def __init__(self, message: str = "资源已存在"):
        super().__init__(message, code=409)
