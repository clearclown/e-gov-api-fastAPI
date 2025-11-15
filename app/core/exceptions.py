"""
カスタム例外クラス

e-gov API連携におけるエラーハンドリング用の例外クラスを定義します。
"""


class EGovAPIError(Exception):
    """e-gov API エラー基底クラス

    すべてのe-gov API関連エラーの基底クラス。
    """

    def __init__(self, message: str, status_code: int = 500):
        """
        Args:
            message: エラーメッセージ
            status_code: HTTPステータスコード
        """
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class LawNotFoundError(EGovAPIError):
    """法令が見つからないエラー

    指定された法令IDに対応する法令が存在しない場合に発生。
    """

    def __init__(self, law_id: str):
        """
        Args:
            law_id: 存在しない法令ID
        """
        message = f"法令が見つかりません: {law_id}"
        super().__init__(message, status_code=404)
        self.law_id = law_id


class EGovAPITimeoutError(EGovAPIError):
    """e-gov API タイムアウトエラー

    e-gov APIへのリクエストがタイムアウトした場合に発生。
    """

    def __init__(self, timeout: int):
        """
        Args:
            timeout: タイムアウト秒数
        """
        message = f"e-gov APIへのリクエストがタイムアウトしました（{timeout}秒）"
        super().__init__(message, status_code=504)
        self.timeout = timeout


class EGovAPIRateLimitError(EGovAPIError):
    """e-gov API レート制限エラー

    API呼び出しのレート制限を超えた場合に発生。
    """

    def __init__(self, retry_after: int = 60):
        """
        Args:
            retry_after: 再試行までの待機秒数
        """
        message = f"API呼び出しのレート制限を超えました。{retry_after}秒後に再試行してください"
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class EGovAPIConnectionError(EGovAPIError):
    """e-gov API 接続エラー

    e-gov APIへの接続に失敗した場合に発生。
    """

    def __init__(self, original_error: Exception):
        """
        Args:
            original_error: 元の例外
        """
        message = f"e-gov APIへの接続に失敗しました: {str(original_error)}"
        super().__init__(message, status_code=503)
        self.original_error = original_error


class InvalidParameterError(EGovAPIError):
    """無効なパラメータエラー

    APIリクエストパラメータが不正な場合に発生。
    """

    def __init__(self, parameter: str, reason: str):
        """
        Args:
            parameter: 不正なパラメータ名
            reason: エラーの理由
        """
        message = f"無効なパラメータ '{parameter}': {reason}"
        super().__init__(message, status_code=400)
        self.parameter = parameter
        self.reason = reason


class CacheError(Exception):
    """キャッシュエラー基底クラス

    Redis等のキャッシュ操作に関するエラー。
    """

    def __init__(self, message: str):
        """
        Args:
            message: エラーメッセージ
        """
        self.message = message
        super().__init__(self.message)
