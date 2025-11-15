"""
e-gov法令APIクライアント

e-gov法令API (https://elaws.e-gov.go.jp/) との連携を行うクライアント実装。
法令の検索、詳細取得、改正履歴の取得機能を提供します。
"""

import httpx
import logging
from typing import List, Optional, Dict, Any
from datetime import date, datetime
import xml.etree.ElementTree as ET

from app.models.law import LawSearchResult, LawDetail, LawAmendment
from app.core.config import settings
from app.core.exceptions import (
    LawNotFoundError,
    EGovAPITimeoutError,
    EGovAPIRateLimitError,
    EGovAPIConnectionError,
    InvalidParameterError,
)

logger = logging.getLogger(__name__)


class EGovAPIClient:
    """e-gov法令APIクライアント

    e-gov APIとの通信を担当するクライアントクラス。
    非同期HTTPクライアント（httpx）を使用してAPIリクエストを行います。

    Attributes:
        base_url: e-gov APIのベースURL
        timeout: リクエストタイムアウト時間（秒）
        client: HTTPクライアント
    """

    # e-gov APIのエンドポイントパス
    SEARCH_ENDPOINT = "/api/1/lawlists/1"
    DETAIL_ENDPOINT = "/api/1/lawdata/{law_id}"

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None
    ):
        """
        Args:
            base_url: e-gov APIのベースURL
            timeout: タイムアウト秒数
        """
        self.base_url = base_url or settings.egov_api_base_url
        self.timeout = timeout or settings.egov_api_timeout
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """非同期コンテキストマネージャー開始"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同期コンテキストマネージャー終了"""
        await self.disconnect()

    async def connect(self) -> None:
        """HTTPクライアントを初期化"""
        if not self.client:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={
                    "User-Agent": f"{settings.app_name}/{settings.app_version}",
                    "Accept": "application/xml"
                }
            )
            logger.info(f"e-gov APIクライアント初期化: {self.base_url}")

    async def disconnect(self) -> None:
        """HTTPクライアントをクローズ"""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("e-gov APIクライアント切断")

    async def search_laws(
        self,
        query: str,
        law_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[LawSearchResult]:
        """法令検索

        Args:
            query: 検索キーワード
            law_type: 法令種別（law: 法律、ordinance: 政令、ministerial_order: 省令）
            limit: 取得件数（最大100）
            offset: オフセット

        Returns:
            検索結果のリスト

        Raises:
            InvalidParameterError: 無効なパラメータ
            EGovAPITimeoutError: タイムアウト
            EGovAPIConnectionError: 接続エラー
            EGovAPIRateLimitError: レート制限
        """
        if not self.client:
            await self.connect()

        # パラメータバリデーション
        if not query or not query.strip():
            raise InvalidParameterError("query", "検索キーワードは必須です")

        if limit < 1 or limit > 100:
            raise InvalidParameterError("limit", "limitは1から100の範囲で指定してください")

        if offset < 0:
            raise InvalidParameterError("offset", "offsetは0以上の値を指定してください")

        # リクエストパラメータ構築
        params: Dict[str, Any] = {
            "query": query.strip(),
            "limit": limit,
            "offset": offset
        }

        if law_type:
            params["type"] = self._map_law_type(law_type)

        try:
            logger.info(f"法令検索リクエスト: query={query}, limit={limit}, offset={offset}")
            response = await self.client.get(self.SEARCH_ENDPOINT, params=params)

            # ステータスコードチェック
            if response.status_code == 404:
                return []
            elif response.status_code == 429:
                raise EGovAPIRateLimitError()
            elif response.status_code >= 400:
                logger.error(f"e-gov APIエラー: {response.status_code} - {response.text}")
                return []

            # XMLレスポンスをパース
            results = self._parse_search_response(response.text)
            logger.info(f"法令検索完了: {len(results)}件")
            return results

        except httpx.TimeoutException as e:
            logger.error(f"タイムアウトエラー: {e}")
            raise EGovAPITimeoutError(self.timeout)
        except httpx.ConnectError as e:
            logger.error(f"接続エラー: {e}")
            raise EGovAPIConnectionError(e)
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            raise EGovAPIConnectionError(e)

    async def get_law_detail(self, law_id: str) -> LawDetail:
        """法令詳細取得

        Args:
            law_id: 法令ID

        Returns:
            法令詳細

        Raises:
            LawNotFoundError: 法令が見つからない
            EGovAPITimeoutError: タイムアウト
            EGovAPIConnectionError: 接続エラー
        """
        if not self.client:
            await self.connect()

        if not law_id or not law_id.strip():
            raise InvalidParameterError("law_id", "法令IDは必須です")

        endpoint = self.DETAIL_ENDPOINT.format(law_id=law_id.strip())

        try:
            logger.info(f"法令詳細取得リクエスト: law_id={law_id}")
            response = await self.client.get(endpoint)

            if response.status_code == 404:
                raise LawNotFoundError(law_id)
            elif response.status_code == 429:
                raise EGovAPIRateLimitError()
            elif response.status_code >= 400:
                logger.error(f"e-gov APIエラー: {response.status_code}")
                raise LawNotFoundError(law_id)

            # XMLレスポンスをパース
            detail = self._parse_detail_response(response.text, law_id)
            logger.info(f"法令詳細取得完了: {detail.law_name}")
            return detail

        except httpx.TimeoutException as e:
            logger.error(f"タイムアウトエラー: {e}")
            raise EGovAPITimeoutError(self.timeout)
        except httpx.ConnectError as e:
            logger.error(f"接続エラー: {e}")
            raise EGovAPIConnectionError(e)
        except LawNotFoundError:
            raise
        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            raise EGovAPIConnectionError(e)

    async def get_law_history(self, law_id: str) -> List[LawAmendment]:
        """法令改正履歴取得

        Args:
            law_id: 法令ID

        Returns:
            改正履歴のリスト

        Raises:
            LawNotFoundError: 法令が見つからない
            EGovAPITimeoutError: タイムアウト
        """
        if not self.client:
            await self.connect()

        if not law_id or not law_id.strip():
            raise InvalidParameterError("law_id", "法令IDは必須です")

        # 注: 実際のe-gov APIの改正履歴エンドポイントの仕様に応じて実装を調整
        # ここでは法令詳細に含まれる改正情報を取得すると仮定
        try:
            logger.info(f"改正履歴取得リクエスト: law_id={law_id}")
            detail = await self.get_law_detail(law_id)

            # 詳細データから改正履歴を抽出（実装は仮）
            # 実際のAPIレスポンス構造に応じて調整が必要
            amendments = self._extract_amendments(detail)
            logger.info(f"改正履歴取得完了: {len(amendments)}件")
            return amendments

        except LawNotFoundError:
            raise
        except Exception as e:
            logger.error(f"改正履歴取得エラー: {e}")
            return []

    def _map_law_type(self, law_type: str) -> str:
        """法令種別を e-gov API形式にマッピング

        Args:
            law_type: 法令種別（law, ordinance, ministerial_order）

        Returns:
            e-gov API用の法令種別コード
        """
        type_mapping = {
            "law": "1",  # 法律
            "ordinance": "2",  # 政令
            "ministerial_order": "3",  # 省令
        }
        return type_mapping.get(law_type, "1")

    def _parse_search_response(self, xml_text: str) -> List[LawSearchResult]:
        """検索結果のXMLをパース

        Args:
            xml_text: XMLレスポンステキスト

        Returns:
            法令検索結果のリスト

        Note:
            実際のe-gov APIのXML構造に応じて実装を調整する必要があります
        """
        results = []

        try:
            # XML解析（実際のAPIレスポンス構造に応じて調整）
            root = ET.fromstring(xml_text)

            # サンプル実装 - 実際のXML構造に応じて変更
            for law_elem in root.findall(".//LawNameListInfo"):
                try:
                    law_id = law_elem.findtext("LawId", "")
                    law_number = law_elem.findtext("LawNo", "")
                    law_name = law_elem.findtext("LawName", "")
                    law_type = law_elem.findtext("LawType", "法律")

                    # 日付のパース
                    prom_date_str = law_elem.findtext("PromulgationDate", "")
                    enf_date_str = law_elem.findtext("EnforcementDate", "")

                    promulgation_date = self._parse_date(prom_date_str) if prom_date_str else date.today()
                    enforcement_date = self._parse_date(enf_date_str) if enf_date_str else None

                    result = LawSearchResult(
                        law_id=law_id,
                        law_number=law_number,
                        law_name=law_name,
                        law_type=law_type,
                        promulgation_date=promulgation_date,
                        enforcement_date=enforcement_date
                    )
                    results.append(result)
                except Exception as e:
                    logger.warning(f"検索結果パースエラー（スキップ）: {e}")
                    continue

        except ET.ParseError as e:
            logger.error(f"XML解析エラー: {e}")

        return results

    def _parse_detail_response(self, xml_text: str, law_id: str) -> LawDetail:
        """法令詳細のXMLをパース

        Args:
            xml_text: XMLレスポンステキスト
            law_id: 法令ID

        Returns:
            法令詳細

        Note:
            実際のe-gov APIのXML構造に応じて実装を調整する必要があります
        """
        try:
            root = ET.fromstring(xml_text)

            # 基本情報取得（実際のXML構造に応じて調整）
            law_number = root.findtext(".//LawNo", "")
            law_name = root.findtext(".//LawName", "")
            law_type = root.findtext(".//LawType", "法律")

            prom_date_str = root.findtext(".//PromulgationDate", "")
            enf_date_str = root.findtext(".//EnforcementDate", "")

            promulgation_date = self._parse_date(prom_date_str) if prom_date_str else date.today()
            enforcement_date = self._parse_date(enf_date_str) if enf_date_str else None

            # 全文取得
            full_text_elem = root.find(".//LawBody")
            full_text = ET.tostring(full_text_elem, encoding="unicode", method="text") if full_text_elem is not None else ""

            # 目次構造を抽出
            toc = self._extract_toc(root)

            # メタデータ
            metadata = {
                "last_updated": datetime.now().isoformat(),
                "source": "e-gov"
            }

            return LawDetail(
                law_id=law_id,
                law_number=law_number,
                law_name=law_name,
                law_type=law_type,
                promulgation_date=promulgation_date,
                enforcement_date=enforcement_date,
                full_text=full_text.strip(),
                toc=toc,
                metadata=metadata
            )

        except ET.ParseError as e:
            logger.error(f"XML解析エラー: {e}")
            raise LawNotFoundError(law_id)

    def _extract_toc(self, root: ET.Element) -> List[Dict[str, Any]]:
        """XML から目次構造を抽出

        Args:
            root: XMLルート要素

        Returns:
            目次構造のリスト
        """
        toc = []

        try:
            # 実際のXML構造に応じて調整
            for chapter in root.findall(".//Chapter"):
                chapter_info = {
                    "chapter": chapter.findtext("ChapterTitle", ""),
                    "title": chapter.findtext("ChapterLabel", ""),
                    "articles": []
                }

                for article in chapter.findall(".//Article"):
                    article_num = article.findtext("ArticleNo", "")
                    if article_num:
                        chapter_info["articles"].append(article_num)

                if chapter_info["chapter"] or chapter_info["articles"]:
                    toc.append(chapter_info)
        except Exception as e:
            logger.warning(f"目次抽出エラー: {e}")

        return toc

    def _extract_amendments(self, detail: LawDetail) -> List[LawAmendment]:
        """法令詳細から改正履歴を抽出

        Args:
            detail: 法令詳細

        Returns:
            改正履歴のリスト

        Note:
            実際のe-gov APIの改正情報構造に応じて実装を調整
        """
        # 仮実装 - 実際のAPIレスポンスに応じて調整
        return []

    def _parse_date(self, date_str: str) -> date:
        """日付文字列をdate型に変換

        Args:
            date_str: 日付文字列（YYYY-MM-DD形式想定）

        Returns:
            date型オブジェクト
        """
        try:
            # 複数の日付フォーマットに対応
            for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"]:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue

            # パースできない場合は今日の日付を返す
            logger.warning(f"日付パース失敗: {date_str}")
            return date.today()
        except Exception as e:
            logger.warning(f"日付変換エラー: {e}")
            return date.today()
