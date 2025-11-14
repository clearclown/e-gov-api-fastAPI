"""e-gov API クライアント（モック実装）"""

from typing import List, Optional
from app.models.law import LawDetail


class EGovAPIClient:
    """e-gov API クライアント（Phase 4用モック実装）"""

    def __init__(self) -> None:
        # Phase 4実装: 実際のAPIクライアントはPhase 1で実装予定
        self._mock_laws = self._create_mock_laws()

    async def get_law_detail(self, law_id: str) -> Optional[LawDetail]:
        """法令詳細を取得"""
        return self._mock_laws.get(law_id)

    async def get_all_laws(self) -> List[LawDetail]:
        """全法令を取得（モック）"""
        return list(self._mock_laws.values())

    def _create_mock_laws(self) -> dict[str, LawDetail]:
        """モック法令データを作成"""
        from datetime import date

        return {
            "405AC0000000087": LawDetail(
                law_id="405AC0000000087",
                law_name="民法",
                law_number="明治二十九年法律第八十九号",
                promulgation_date=date(1896, 4, 27),
                enforcement_date=date(1898, 7, 16),
                category="民事",
                full_text="""第一編 総則
第一章 通則
（基本原則）
第一条 私権は、公共の福祉に適合しなければならない。
...
第五編 相続
第五百四十一条（催告による解除）
当事者の一方がその債務を履行しない場合において、相手方が相当の期間を定めてその履行の催告をし、その期間内に履行がないときは、相手方は、契約の解除をすることができる。ただし、その期間を経過した時における債務の不履行がその契約及び取引上の社会通念に照らして軽微であるときは、この限りでない。
...
第七百九条（不法行為による損害賠償）
故意又は過失によって他人の権利又は法律上保護される利益を侵害した者は、これによって生じた損害を賠償する責任を負う。
""",
                updated_at=date(2024, 1, 1),
            ),
            "405AC0000000089": LawDetail(
                law_id="405AC0000000089",
                law_name="商法",
                law_number="明治三十二年法律第四十八号",
                promulgation_date=date(1899, 3, 9),
                enforcement_date=date(1899, 6, 16),
                category="商事",
                full_text="第一編 総則\n...",
                updated_at=date(2023, 12, 1),
            ),
        }
