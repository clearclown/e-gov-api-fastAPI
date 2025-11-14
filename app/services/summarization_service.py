"""法的文書要約サービス"""

from typing import Dict, Optional, Any
import re
from datetime import datetime
from app.models.case import CaseDetail
from app.models.law import LawDetail


class SummarizationService:
    """法的文書要約サービス"""

    def __init__(self, anthropic_api_key: Optional[str] = None) -> None:
        """
        Args:
            anthropic_api_key: Anthropic APIキー（Phase 3で実装予定）
        """
        self.api_key = anthropic_api_key
        # Phase 4: 実際のClaude API統合はPhase 3で実装

    async def summarize_case(
        self, case: CaseDetail, style: str = "brief"
    ) -> Dict[str, Any]:
        """
        判例を要約

        Args:
            case: 判例データ
            style: 要約スタイル
                - brief: 簡潔（200文字程度）
                - detailed: 詳細（500文字程度）
                - plain: 平易な言葉（一般向け）

        Returns:
            要約テキストと各セクション
        """
        # Phase 4: モック実装
        # 実際のClaude API呼び出しはPhase 3で実装予定

        summaries = {
            "brief": self._generate_brief_summary(case),
            "detailed": self._generate_detailed_summary(case),
            "plain": self._generate_plain_summary(case),
        }

        summary = summaries.get(style, summaries["brief"])

        return {
            "case_id": case.case_id,
            "case_name": case.case_name,
            "summary": summary,
            "style": style,
            "generated_at": datetime.now().isoformat(),
        }

    def _generate_brief_summary(self, case: CaseDetail) -> str:
        """簡潔な要約を生成（モック）"""
        return f"""【簡潔要約】
{case.case_name}（{case.court_name}、{case.decision_date}）

判示事項: {case.holdings or '（記載なし）'}

判決: {case.outcome or '詳細は全文参照'}

※ これはPhase 4のモック実装です。実際のAI要約はPhase 3で実装予定です。
"""

    def _generate_detailed_summary(self, case: CaseDetail) -> str:
        """詳細な要約を生成（モック）"""
        return f"""【詳細要約】
事件名: {case.case_name}
裁判所: {case.court_name}
判決日: {case.decision_date}
事件番号: {case.case_number or '（記載なし）'}

■ 判示事項
{case.holdings or '（記載なし）'}

■ 裁判要旨
{case.case_summary or '（記載なし）'}

■ 判決結果
{case.outcome or '詳細は全文参照'}

■ 実務への影響
本判決は{case.case_type or '民事'}事件における重要な判断基準を示しています。

※ これはPhase 4のモック実装です。実際のAI要約はPhase 3で実装予定です。
"""

    def _generate_plain_summary(self, case: CaseDetail) -> str:
        """平易な言葉での要約を生成（モック）"""
        return f"""【一般向け解説】
この裁判は「{case.case_name}」という事件で、{case.decision_date}に{case.court_name}が判断を下しました。

どんな事件？
{case.holdings or case.case_summary or '詳細な事案の概要は記載されていません。'}

裁判所の判断
{case.outcome or '判決の詳細は全文をご確認ください。'}

この判決の意味
この判決は、同じような問題に直面した時の参考になります。
具体的な状況によって判断は異なる可能性がありますので、
詳しくは法律の専門家にご相談ください。

※ これはPhase 4のモック実装です。実際のAI要約はPhase 3で実装予定です。
"""

    async def explain_law_article(
        self, law: LawDetail, article_number: str
    ) -> Dict[str, Any]:
        """
        法令の特定条文を平易に説明

        Args:
            law: 法令データ
            article_number: 条文番号（例: "第309条" または "309"）

        Returns:
            説明文
        """
        # 条文番号を正規化
        normalized_article = article_number
        if not article_number.startswith("第"):
            normalized_article = f"第{article_number}条"

        # 条文を抽出
        article_text = self._extract_article(law.full_text, normalized_article)

        if not article_text:
            return {"error": f"条文 {normalized_article} が見つかりません"}

        # Phase 4: モック実装
        explanation = f"""【条文解説】
法令名: {law.law_name}
条文: {normalized_article}

■ 条文の内容
{article_text}

■ 分かりやすい説明
この条文は、{law.law_name}の重要な規定の一つです。
具体的な解釈については、個別の状況によって異なる場合があります。
詳しくは法律の専門家にご相談ください。

※ これはPhase 4のモック実装です。実際のAI解説はPhase 3で実装予定です。
"""

        return {
            "law_id": law.law_id,
            "law_name": law.law_name,
            "article_number": normalized_article,
            "original_text": article_text,
            "explanation": explanation,
        }

    def _extract_article(self, full_text: str, article_number: str) -> Optional[str]:
        """条文を抽出（簡易実装）"""
        # 条文番号でテキストを分割して該当部分を抽出
        pattern = rf"{re.escape(article_number)}[^\n]*\n([^第]+)"
        match = re.search(pattern, full_text)

        if match:
            return f"{article_number}\n{match.group(1).strip()}"

        # フォールバック: 条文番号を含む段落を返す
        lines = full_text.split("\n")
        for i, line in enumerate(lines):
            if article_number in line:
                # 次の条文または編まで取得
                result = [line]
                for next_line in lines[i + 1 :]:
                    if next_line.startswith("第") and "条" in next_line:
                        break
                    if next_line.startswith("第") and "編" in next_line:
                        break
                    result.append(next_line)
                return "\n".join(result).strip()

        return None

    async def generate_comparative_summary(
        self, law_id_1: str, law_id_2: str
    ) -> Dict[str, str]:
        """
        2つの法令を比較要約（モック実装）

        Args:
            law_id_1: 比較対象法令1
            law_id_2: 比較対象法令2

        Returns:
            比較要約
        """
        # Phase 4: モック実装
        return {
            "law_id_1": law_id_1,
            "law_id_2": law_id_2,
            "comparison": f"""【法令比較】

法令1: {law_id_1}
法令2: {law_id_2}

この機能は Phase 3 で実装予定です。
2つの法令の主な違いや関連性をAIが自動的に分析します。

※ これはPhase 4のモック実装です。
""",
        }
