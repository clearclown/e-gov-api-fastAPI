"""
キャッシュ管理

Redisを使用した法令データのキャッシング機能を提供します。
"""

from redis import asyncio as aioredis
from typing import Optional, Any
import json
import hashlib
import logging
from app.core.config import settings
from app.core.exceptions import CacheError

logger = logging.getLogger(__name__)


class LawCache:
    """法令データキャッシュ

    Redisを使用して法令データおよび検索結果をキャッシュします。

    Attributes:
        redis: Redisクライアント
        enabled: キャッシュの有効/無効
    """

    def __init__(self, redis_url: Optional[str] = None, enabled: Optional[bool] = None):
        """
        Args:
            redis_url: RedisサーバーURL（Noneの場合は設定から取得）
            enabled: キャッシュの有効/無効（Noneの場合は設定から取得）
        """
        self.redis_url = redis_url or settings.redis_url
        self.enabled = enabled if enabled is not None else settings.redis_enabled
        self.redis: Optional[aioredis.Redis] = None

    async def connect(self) -> None:
        """Redisサーバーに接続"""
        if not self.enabled:
            logger.info("キャッシュが無効化されています")
            return

        try:
            self.redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis.ping()
            logger.info(f"Redisに接続しました: {self.redis_url}")
        except Exception as e:
            logger.error(f"Redis接続エラー: {e}")
            self.enabled = False
            self.redis = None

    async def disconnect(self) -> None:
        """Redisサーバーから切断"""
        if self.redis:
            await self.redis.close()
            logger.info("Redisから切断しました")

    async def get_law(self, law_id: str) -> Optional[dict]:
        """キャッシュから法令取得

        Args:
            law_id: 法令ID

        Returns:
            キャッシュされた法令データ、存在しない場合はNone

        Raises:
            CacheError: キャッシュ取得時のエラー
        """
        if not self.enabled or not self.redis:
            return None

        try:
            data = await self.redis.get(f"law:{law_id}")
            if data:
                logger.debug(f"キャッシュヒット: law:{law_id}")
                return json.loads(data)
            logger.debug(f"キャッシュミス: law:{law_id}")
            return None
        except Exception as e:
            logger.error(f"キャッシュ取得エラー: {e}")
            return None

    async def set_law(
        self,
        law_id: str,
        data: dict,
        ttl: Optional[int] = None
    ) -> bool:
        """法令をキャッシュに保存

        Args:
            law_id: 法令ID
            data: 保存する法令データ
            ttl: キャッシュの有効期限（秒）、Noneの場合はデフォルト値を使用

        Returns:
            保存成功時True、失敗時False

        Raises:
            CacheError: キャッシュ保存時のエラー
        """
        if not self.enabled or not self.redis:
            return False

        try:
            ttl = ttl or settings.cache_ttl_law_detail
            await self.redis.setex(
                f"law:{law_id}",
                ttl,
                json.dumps(data, ensure_ascii=False, default=str)
            )
            logger.debug(f"キャッシュ保存: law:{law_id} (TTL: {ttl}秒)")
            return True
        except Exception as e:
            logger.error(f"キャッシュ保存エラー: {e}")
            return False

    async def get_search_results(self, query_params: dict) -> Optional[list]:
        """検索結果をキャッシュから取得

        Args:
            query_params: 検索パラメータ（辞書形式）

        Returns:
            キャッシュされた検索結果、存在しない場合はNone
        """
        if not self.enabled or not self.redis:
            return None

        try:
            cache_key = self._generate_search_cache_key(query_params)
            data = await self.redis.get(f"search:{cache_key}")
            if data:
                logger.debug(f"検索キャッシュヒット: {cache_key}")
                return json.loads(data)
            logger.debug(f"検索キャッシュミス: {cache_key}")
            return None
        except Exception as e:
            logger.error(f"検索キャッシュ取得エラー: {e}")
            return None

    async def set_search_results(
        self,
        query_params: dict,
        results: list,
        ttl: Optional[int] = None
    ) -> bool:
        """検索結果をキャッシュに保存

        Args:
            query_params: 検索パラメータ
            results: 検索結果リスト
            ttl: キャッシュの有効期限（秒）

        Returns:
            保存成功時True、失敗時False
        """
        if not self.enabled or not self.redis:
            return False

        try:
            cache_key = self._generate_search_cache_key(query_params)
            ttl = ttl or settings.cache_ttl_search
            await self.redis.setex(
                f"search:{cache_key}",
                ttl,
                json.dumps(results, ensure_ascii=False, default=str)
            )
            logger.debug(f"検索キャッシュ保存: {cache_key} (TTL: {ttl}秒)")
            return True
        except Exception as e:
            logger.error(f"検索キャッシュ保存エラー: {e}")
            return False

    async def invalidate_law(self, law_id: str) -> bool:
        """法令キャッシュを無効化

        Args:
            law_id: 法令ID

        Returns:
            無効化成功時True
        """
        if not self.enabled or not self.redis:
            return False

        try:
            await self.redis.delete(f"law:{law_id}")
            logger.info(f"キャッシュ無効化: law:{law_id}")
            return True
        except Exception as e:
            logger.error(f"キャッシュ無効化エラー: {e}")
            return False

    async def clear_all(self) -> bool:
        """すべてのキャッシュをクリア

        Returns:
            クリア成功時True
        """
        if not self.enabled or not self.redis:
            return False

        try:
            await self.redis.flushdb()
            logger.info("すべてのキャッシュをクリアしました")
            return True
        except Exception as e:
            logger.error(f"キャッシュクリアエラー: {e}")
            return False

    def _generate_search_cache_key(self, query_params: dict) -> str:
        """検索パラメータからキャッシュキーを生成

        Args:
            query_params: 検索パラメータ

        Returns:
            ハッシュ化されたキャッシュキー
        """
        # パラメータを正規化してソート
        normalized = json.dumps(query_params, sort_keys=True, ensure_ascii=False)
        # SHA256ハッシュを生成
        return hashlib.sha256(normalized.encode()).hexdigest()


# グローバルキャッシュインスタンス
law_cache = LawCache()
