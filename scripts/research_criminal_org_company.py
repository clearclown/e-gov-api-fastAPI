"""
犯罪組織と会社設立に関する法令・判例調査スクリプト

このスクリプトは以下を行います:
1. e-gov APIから法令を取得し、犯罪組織関連の法律をフィルタリング
2. Playwright MCPを使用して裁判所ウェブサイトから実際の判例を取得
3. 関連法令と判例をまとめて表示
"""

import asyncio
import httpx
import json
from typing import List, Dict, Any


async def get_all_laws() -> List[Dict[str, Any]]:
    """e-gov APIから法令一覧を取得"""
    print("📚 法令データを取得中...")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/v1/laws/search",
            params={"q": "法律", "limit": 100},
            timeout=30.0
        )

        if response.status_code == 200:
            data = response.json()
            print(f"   取得完了: {data['total']}件")
            return data['results']
        else:
            print(f"   エラー: {response.status_code}")
            return []


def filter_criminal_org_laws(laws: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """犯罪組織関連の法令をフィルタリング"""
    print("\n🔍 犯罪組織関連の法令をフィルタリング中...")

    # 検索キーワード
    keywords = [
        "組織的",
        "組織犯罪",
        "暴力団",
        "犯罪収益",
        "マネーロンダリング",
        "資金洗浄",
        "テロ資金",
        "反社会的勢力",
    ]

    filtered = []

    for law in laws:
        law_name = law.get('law_name', '')

        # いずれかのキーワードが含まれるかチェック
        if any(keyword in law_name for keyword in keywords):
            filtered.append(law)

    print(f"   フィルタ結果: {len(filtered)}件")
    return filtered


def filter_company_related_laws(laws: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """会社設立関連の法令をフィルタリング"""
    print("\n🏢 会社設立関連の法令をフィルタリング中...")

    keywords = [
        "会社法",
        "商業登記",
        "会社",
        "株式会社",
        "法人",
    ]

    filtered = []

    for law in laws:
        law_name = law.get('law_name', '')

        if any(keyword in law_name for keyword in keywords):
            filtered.append(law)

    print(f"   フィルタ結果: {len(filtered)}件")
    return filtered


async def search_court_cases(keywords: str) -> List[Dict[str, Any]]:
    """裁判所ウェブサイトから判例を検索"""
    print(f"\n⚖️  判例を検索中: '{keywords}'...")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/v1/cases/search",
            params={"keywords": keywords, "limit": 10},
            timeout=30.0
        )

        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"   検索完了: {len(results)}件")
            return results
        else:
            print(f"   エラー: {response.status_code}")
            return []


def print_law_info(law: Dict[str, Any], index: int):
    """法令情報を表示"""
    print(f"\n{index}. {law.get('law_name', '不明')}")
    print(f"   法令番号: {law.get('law_number', '不明')}")
    print(f"   種別: {law.get('law_type', '不明')}")
    print(f"   公布日: {law.get('promulgation_date', '不明')}")
    if law.get('enforcement_date'):
        print(f"   施行日: {law.get('enforcement_date', '不明')}")


def print_case_info(case: Dict[str, Any], index: int):
    """判例情報を表示"""
    print(f"\n{index}. {case.get('case_name', '不明')}")
    print(f"   事件番号: {case.get('case_number', '不明')}")
    print(f"   裁判所: {case.get('court_name', '不明')}")
    print(f"   判決日: {case.get('case_date', '不明')}")
    print(f"   事件種別: {case.get('case_type', '不明')}")
    if case.get('summary'):
        print(f"   要旨: {case.get('summary', '')[:100]}...")


async def main():
    """メイン処理"""
    print("=" * 80)
    print("犯罪組織と会社設立に関する法令・判例調査")
    print("=" * 80)

    # 1. 法令の取得とフィルタリング
    all_laws = await get_all_laws()

    # 犯罪組織関連法令
    criminal_laws = filter_criminal_org_laws(all_laws)

    # 会社関連法令
    company_laws = filter_company_related_laws(all_laws)

    # 2. 判例の検索
    case_keywords = [
        "暴力団 会社設立",
        "組織的犯罪 法人",
        "反社会的勢力 会社",
    ]

    all_cases = []
    for keywords in case_keywords:
        cases = await search_court_cases(keywords)
        all_cases.extend(cases)

    # 重複除去
    unique_cases = []
    seen_ids = set()
    for case in all_cases:
        case_id = case.get('case_id')
        if case_id and case_id not in seen_ids:
            unique_cases.append(case)
            seen_ids.add(case_id)

    # 3. 結果の表示
    print("\n" + "=" * 80)
    print("📋 調査結果サマリー")
    print("=" * 80)

    print(f"\n✅ 犯罪組織関連法令: {len(criminal_laws)}件")
    print(f"✅ 会社設立関連法令: {len(company_laws)}件")
    print(f"✅ 関連判例: {len(unique_cases)}件")

    # 犯罪組織関連法令の詳細
    print("\n" + "=" * 80)
    print("📚 犯罪組織関連法令の詳細")
    print("=" * 80)

    for i, law in enumerate(criminal_laws[:10], 1):  # 最大10件
        print_law_info(law, i)

    if len(criminal_laws) > 10:
        print(f"\n   ... 他 {len(criminal_laws) - 10}件")

    # 会社設立関連法令の詳細（主要なもののみ）
    print("\n" + "=" * 80)
    print("🏢 会社設立関連法令の詳細（主要なもの）")
    print("=" * 80)

    for i, law in enumerate(company_laws[:5], 1):  # 最大5件
        print_law_info(law, i)

    if len(company_laws) > 5:
        print(f"\n   ... 他 {len(company_laws) - 5}件")

    # 判例の詳細
    print("\n" + "=" * 80)
    print("⚖️  関連判例の詳細")
    print("=" * 80)

    if unique_cases:
        for i, case in enumerate(unique_cases, 1):
            print_case_info(case, i)
    else:
        print("\n   判例が見つかりませんでした")

    # 重要な法令の特定
    print("\n" + "=" * 80)
    print("🔑 重要な法令")
    print("=" * 80)

    important_keywords = {
        "組織的な犯罪の処罰及び犯罪収益の規制等に関する法律": "組織的犯罪処罰法",
        "暴力団員による不当な行為の防止等に関する法律": "暴力団対策法",
        "犯罪による収益の移転防止に関する法律": "犯罪収益移転防止法",
        "会社法": "会社法",
    }

    for full_name, short_name in important_keywords.items():
        found = [law for law in all_laws if full_name in law.get('law_name', '')]
        if found:
            print(f"\n✓ {short_name} ({full_name})")
            for law in found:
                print(f"  法令番号: {law.get('law_number', '不明')}")
                print(f"  法令ID: {law.get('law_id', '不明')}")
        else:
            print(f"\n✗ {short_name} - 見つかりませんでした")

    print("\n" + "=" * 80)
    print("✅ 調査完了")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
