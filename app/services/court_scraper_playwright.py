"""Court case scraper using Playwright MCP for courts.go.jp

This service uses the Playwright MCP server to scrape case law data from the
Japanese courts website (courts.go.jp).
"""

import hashlib
import re
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from app.models.case import CaseDetail, CaseSearchResult


class PlaywrightCourtScraper:
    """判例検索サービス (Playwright MCP使用)

    Playwright MCPを使用して裁判所ウェブサイトから判例を取得します。
    """

    BASE_URL = "https://www.courts.go.jp"
    SEARCH_URL = f"{BASE_URL}/hanrei/search1/index.html"

    def __init__(self, playwright_tools: Any):
        """Initialize with Playwright MCP tools.

        Args:
            playwright_tools: Object containing Playwright MCP tool functions
                (browser_navigate, browser_snapshot, browser_type, browser_click, etc.)
        """
        self.pw = playwright_tools

    async def search_cases(
        self,
        keywords: str,
        court_type: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        limit: int = 10,
    ) -> List[CaseSearchResult]:
        """判例を検索

        Args:
            keywords: 検索キーワード
            court_type: 裁判所タイプ (最高, 高等, 地方, etc.)
            date_from: 判決日の開始日
            date_to: 判決日の終了日
            limit: 最大取得件数

        Returns:
            検索結果のリスト
        """
        try:
            # Navigate to search page
            await self.pw.browser_navigate(self.SEARCH_URL)

            # Enter search keywords
            await self.pw.browser_type(keywords, "キーワード")

            # TODO: Add date range and court type filtering if specified

            # Click search button
            await self.pw.browser_click("検索")

            # Get search results
            snapshot = await self.pw.browser_snapshot()

            # Parse results from snapshot
            results = self._parse_search_results(snapshot, limit)

            return results

        except Exception as e:
            print(f"Error searching cases: {e}")
            return []

    async def get_case_detail(self, case_id: str, detail_url: str) -> Optional[CaseDetail]:
        """判例詳細を取得

        Args:
            case_id: 判例ID
            detail_url: 詳細ページURL

        Returns:
            判例詳細データ
        """
        try:
            # Navigate to detail page
            full_url = f"{self.BASE_URL}{detail_url}" if detail_url.startswith("/") else detail_url
            await self.pw.browser_navigate(full_url)

            # Get page snapshot
            snapshot = await self.pw.browser_snapshot()

            # Parse case details
            case_detail = self._parse_case_detail(case_id, snapshot)

            return case_detail

        except Exception as e:
            print(f"Error fetching case detail: {e}")
            return None

    def _parse_search_results(self, snapshot: str, limit: int) -> List[CaseSearchResult]:
        """検索結果のスナップショットを解析

        Args:
            snapshot: Playwrightスナップショット (YAML text)
            limit: 最大取得件数

        Returns:
            検索結果のリスト
        """
        results = []

        # Parse YAML snapshot - look for table rows with case information
        # Expected pattern in YAML:
        # - row "事件番号 事件名 判決日 裁判所" [ref=...]:
        #     - cell "裁判例種別" [ref=...]:
        #     - cell "令和X(X)XXX 事件名 令和X年X月X日 裁判所名" [ref=...]:
        #         - paragraph [ref=...]: 令和X(X)XXX 事件名
        #         - paragraph [ref=...]: 令和X年X月X日 裁判所名

        # Simple regex-based parsing for demonstration
        # In production, use proper YAML parser
        import re

        # Extract case rows (simplified pattern matching)
        row_pattern = r'row "([^"]+)" \[ref=([^\]]+)\]:'
        para_pattern = r'paragraph \[ref=[^\]]+\]: (.+)'

        lines = snapshot.split('\n')
        current_case = {}

        for i, line in enumerate(lines):
            # Look for table rows that contain case data
            if 'row' in line and '裁判例' in line:
                # Extract case info from subsequent paragraphs
                case_info = []
                for j in range(i+1, min(i+15, len(lines))):
                    para_match = re.search(para_pattern, lines[j])
                    if para_match:
                        case_info.append(para_match.group(1))

                if len(case_info) >= 2:
                    # First paragraph: case number and name
                    # Second paragraph: date and court
                    case_number_line = case_info[0]
                    date_court_line = case_info[1]

                    # Parse case number (e.g., "令和2(ワ)4255 損害賠償請求事件")
                    case_number_match = re.search(r'(令和|平成|昭和)\d+\([^)]+\)\d+', case_number_line)
                    case_number = case_number_match.group(0) if case_number_match else ""

                    # Extract case name (text after case number)
                    case_name = case_number_line.replace(case_number, "").strip()

                    # Parse date and court (e.g., "令和7年5月15日 横浜地方裁判所")
                    date_match = re.search(r'(令和|平成|昭和)\d+年\d+月\d+日', date_court_line)
                    date_str = date_match.group(0) if date_match else ""
                    case_date = self._parse_japanese_date(date_str)

                    # Extract court name (text after date)
                    court_name = date_court_line.replace(date_str, "").strip()

                    if case_number and case_name and case_date:
                        case_id = self._generate_case_id(case_number, court_name, case_date)
                        case_type = self._determine_case_type(case_number)

                        result = CaseSearchResult(
                            case_id=case_id,
                            case_number=case_number,
                            court_name=court_name,
                            case_date=case_date,
                            case_name=case_name,
                            case_type=case_type,
                            summary="",
                        )
                        results.append(result)

                        if len(results) >= limit:
                            break

        return results[:limit]

    def _parse_case_detail(self, case_id: str, snapshot: str) -> CaseDetail:
        """判例詳細ページのスナップショットを解析

        Args:
            case_id: 判例ID
            snapshot: Playwrightスナップショット

        Returns:
            判例詳細データ
        """
        # Extract structured data from detail page snapshot
        # The detail page has definition lists with:
        # - 事件番号 (Case number)
        # - 事件名 (Case name)
        # - 裁判年月日 (Judgment date)
        # - 裁判所名・部 (Court name/division)
        # - 結果 (Result)
        # - 判示事項の要旨 (Summary of issues)
        # - 全文 (Full text link)

        # Parse from snapshot YAML
        case_number = self._extract_field(snapshot, "事件番号") or "不明"
        case_name = self._extract_field(snapshot, "事件名") or "不明"
        date_str = self._extract_field(snapshot, "裁判年月日") or ""
        court_name = self._extract_field(snapshot, "裁判所名・部") or "不明"
        result = self._extract_field(snapshot, "結果")
        summary = self._extract_field(snapshot, "判示事項の要旨")

        # Parse date (format: 令和X年X月X日)
        decision_date = self._parse_japanese_date(date_str) or date.today()

        # Determine court type from court name
        court_type = self._determine_court_type(court_name)

        # Determine case type from case number
        case_type = self._determine_case_type(case_number)

        return CaseDetail(
            case_id=case_id,
            case_number=case_number,
            court_name=court_name,
            case_date=decision_date,
            case_name=case_name,
            case_type=case_type,
            summary=summary or "",
            full_text=result or "",
            references=[],
            metadata={
                "source": "courts.go.jp",
                "last_updated": date.today().isoformat(),
            },
        )

    def _extract_field(self, snapshot: str, field_name: str) -> Optional[str]:
        """Extract field value from snapshot YAML structure.

        Args:
            snapshot: Playwright snapshot (YAML text)
            field_name: Field name to extract (e.g., "事件番号")

        Returns:
            Extracted field value or None
        """
        import re

        # Look for definition lists with field names
        # Pattern: term [ref=...]: {field_name}
        #          definition [ref=...]:
        #            paragraph [ref=...]: {value}

        pattern = f'term \\[ref=[^\\]]+\\]: {re.escape(field_name)}.*?paragraph \\[ref=[^\\]]+\\]: ([^\n]+)'
        match = re.search(pattern, snapshot, re.DOTALL)

        if match:
            value = match.group(1).strip()
            # Remove empty marker if present
            if value and value != "":
                return value

        return None

    def _parse_japanese_date(self, date_str: str) -> Optional[date]:
        """Parse Japanese date format (令和X年X月X日) to Python date.

        Args:
            date_str: Japanese date string

        Returns:
            Python date object or None
        """
        if not date_str:
            return None

        try:
            # Parse 令和X年X月X日, 平成X年X月X日, 昭和X年X月X日
            pattern = r"(令和|平成|昭和)(\d+)年(\d+)月(\d+)日"
            match = re.search(pattern, date_str)

            if match:
                era, year, month, day = match.groups()

                # Convert Japanese era year to Western year
                era_start = {
                    "令和": 2019,  # Reiwa started May 1, 2019
                    "平成": 1989,  # Heisei: 1989-2019
                    "昭和": 1926,  # Showa: 1926-1989
                }

                western_year = era_start[era] + int(year) - 1

                return date(western_year, int(month), int(day))
        except Exception as e:
            print(f"Error parsing date '{date_str}': {e}")

        return None

    def _determine_court_type(self, court_name: str) -> str:
        """Determine court type from court name.

        Args:
            court_name: Name of the court

        Returns:
            Court type string
        """
        if "最高裁判所" in court_name:
            return "最高裁判所"
        elif "高等裁判所" in court_name:
            return "高等裁判所"
        elif "地方裁判所" in court_name:
            return "地方裁判所"
        elif "家庭裁判所" in court_name:
            return "家庭裁判所"
        elif "簡易裁判所" in court_name:
            return "簡易裁判所"
        else:
            return "その他"

    def _determine_case_type(self, case_number: str) -> str:
        """Determine case type from case number.

        Args:
            case_number: Case number (e.g., 令和2(ワ)4255)

        Returns:
            Case type string
        """
        # Case type codes in Japanese case numbers:
        # (ワ) - Civil (民事)
        # (刑) - Criminal (刑事)
        # (行) - Administrative (行政)
        # etc.

        if "(ワ)" in case_number or "(民)" in case_number:
            return "民事"
        elif "(刑)" in case_number or "(わ)" in case_number:
            return "刑事"
        elif "(行)" in case_number:
            return "行政"
        else:
            return "民事"  # Default

    def _generate_case_id(self, case_number: str, court_name: str, decision_date: date) -> str:
        """Generate unique case ID from case information.

        Args:
            case_number: Case number
            court_name: Court name
            decision_date: Decision date

        Returns:
            Unique case ID (20 character hash)
        """
        content = f"{case_number}_{court_name}_{decision_date.isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:20]
