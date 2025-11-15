"""Batch script for fetching recent cases from Courts website."""

import asyncio
from datetime import date, timedelta

from app.db.session import AsyncSessionLocal
from app.repositories.case_repository import CaseRepository
from app.services.case_scraper import CaseScraperService


async def fetch_recent_cases(days: int = 7) -> None:
    """最近の判例を取得して保存

    Args:
        days: 過去何日分の判例を取得するか（デフォルト: 7日）
    """
    print(f"判例取得バッチを開始します（過去{days}日分）")

    date_from = date.today() - timedelta(days=days)
    scraper = CaseScraperService()

    try:
        # Search for recent cases
        print(f"判例検索中... (開始日: {date_from})")
        cases = await scraper.search_cases(date_from=date_from, limit=1000)

        print(f"検索結果: {len(cases)}件の判例が見つかりました")

        if not cases:
            print("取得する判例がありません")
            return

        # Save cases to database
        async with AsyncSessionLocal() as session:
            repo = CaseRepository(session)
            saved_count = 0

            for case_result in cases:
                try:
                    # Fetch full case details
                    print(f"判例詳細取得中: {case_result.case_id}")
                    detail = await scraper.fetch_case_detail(case_result.case_id)

                    # Save to database
                    await repo.save_case(detail)
                    saved_count += 1

                    print(f"保存完了: {detail.case_name} ({detail.case_id})")

                except Exception as e:
                    print(f"エラー（判例ID: {case_result.case_id}）: {e}")
                    continue

            # Commit all changes
            await session.commit()
            print(f"\n取得完了: {saved_count}件の判例を保存しました")

    except Exception as e:
        print(f"バッチ処理エラー: {e}")
        raise

    finally:
        await scraper.close()


async def main() -> None:
    """Main entry point for batch processing."""
    import argparse

    parser = argparse.ArgumentParser(description="判例取得バッチ処理")
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="過去何日分の判例を取得するか（デフォルト: 7）",
    )
    args = parser.parse_args()

    await fetch_recent_cases(days=args.days)


if __name__ == "__main__":
    asyncio.run(main())
