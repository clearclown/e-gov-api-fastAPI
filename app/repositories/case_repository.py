"""判例データリポジトリ"""

from typing import List, Optional
from app.models.case import CaseDetail, CaseReference


class CaseRepository:
    """判例データアクセスクラス（Phase 4用モックリポジトリ）"""

    def __init__(self) -> None:
        # Phase 4実装: 実際のデータベース接続はPhase 2で実装予定
        # ここではモックデータを使用
        self._mock_cases = self._create_mock_cases()
        self._mock_references = self._create_mock_references()

    async def get_case_by_id(self, case_id: str) -> Optional[CaseDetail]:
        """判例IDで判例を取得"""
        return self._mock_cases.get(case_id)

    async def get_all_cases(self) -> List[CaseDetail]:
        """全判例を取得"""
        return list(self._mock_cases.values())

    async def get_all_references(self) -> List[CaseReference]:
        """全引用関係を取得"""
        return self._mock_references

    def _create_mock_cases(self) -> dict[str, CaseDetail]:
        """モック判例データを作成"""
        from datetime import date

        return {
            "CASE-2024-001": CaseDetail(
                case_id="CASE-2024-001",
                case_name="契約解除に関する事件",
                court_name="最高裁判所",
                decision_date=date(2024, 1, 15),
                case_number="令和5年(オ)第1234号",
                case_type="民事",
                holdings="契約解除の可否について",
                case_summary="債務不履行による契約解除の要件を満たすか否かが争点となった事案",
                main_text="主文 1. 原判決を破棄する。2. ...",
                outcome="上告棄却",
            ),
            "CASE-2024-002": CaseDetail(
                case_id="CASE-2024-002",
                case_name="不法行為損害賠償請求事件",
                court_name="東京高等裁判所",
                decision_date=date(2024, 2, 20),
                case_number="令和5年(ネ)第5678号",
                case_type="民事",
                holdings="不法行為の成立要件について",
                case_summary="過失の認定基準が問題となった事案",
                main_text="主文 1. 控訴を棄却する。2. ...",
                outcome="控訴棄却",
            ),
            "CASE-2024-003": CaseDetail(
                case_id="CASE-2024-003",
                case_name="所有権確認請求事件",
                court_name="大阪地方裁判所",
                decision_date=date(2024, 3, 10),
                case_number="令和5年(ワ)第9012号",
                case_type="民事",
                holdings="時効取得の成否について",
                case_summary="占有の継続性が争点となった事案",
                main_text="主文 1. 原告の請求を認容する。2. ...",
                outcome="請求認容",
            ),
        }

    def _create_mock_references(self) -> List[CaseReference]:
        """モック引用関係データを作成"""
        return [
            CaseReference(
                case_id="CASE-2024-001",
                referenced_law_id="405AC0000000087",  # 民法
                reference_type="cites",
                context="民法第541条に基づく契約解除",
            ),
            CaseReference(
                case_id="CASE-2024-002",
                referenced_law_id="405AC0000000087",  # 民法
                reference_type="cites",
                context="民法第709条不法行為",
            ),
            CaseReference(
                case_id="CASE-2024-002",
                referenced_case_id="CASE-2024-001",
                reference_type="follows",
                context="前掲判例の判断基準に従い",
            ),
            CaseReference(
                case_id="CASE-2024-003",
                referenced_law_id="405AC0000000087",  # 民法
                reference_type="cites",
                context="民法第162条時効取得",
            ),
        ]
