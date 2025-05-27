import requests
from .models import Book, Category
import time
from openai import OpenAI

def fetch_aladin_books():
    url = "http://www.aladin.co.kr/ttb/api/ItemList.aspx"
    ttbkey = ""

    # 다양한 QueryType 설정
    query_types = [
        "Bestseller",
        "ItemNewSpecial",     # 주목할 만한 신간
        "ItemEditorChoice",   # 편집자 추천
        "BlogBest",           # 블로그 인기
        "ItemNewAll",         # 모든 신간
    ]

    total_count = 0

    for query_type in query_types:
        for start in range(1, 1000, 50):  # 50개씩 반복해서 요청 (start는 1부터 시작)
            params = {
                "ttbkey": ttbkey,
                "QueryType": query_type,
                "MaxResults": 50,
                "start": start,
                "SearchTarget": "Book",
                "output": "js",
                "Version": "20131101"
            }

            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f" 요청 실패: {query_type}, start={start}")
                break

            data = response.json()
            items = data.get("item", [])
            print(f"📚 {query_type} {start}번부터 {len(items)}권 수집")

            if not items:
                break

            for item in items:
                title = item.get("title")
                author = item.get("author")
                content = item.get("description")
                link = item.get("link")
                img = item.get("cover")
                rank = item.get("customerReviewRank", 0)
                aladin_category = item.get("categoryName", "")

                # 카테고리 매칭
                category_keywords = {
                    "소설": "소설/시/희곡",
                    "경제": "경제/경영",
                    "자기계발": "자기계발",
                    "인문": "인문/교양",
                    "실용": "취미/실용",
                    "어린이": "어린이/청소년",
                    "과학": "과학"
                }

                matched_category = None
                for keyword, cat_name in category_keywords.items():
                    if keyword in aladin_category:
                        matched_category, _ = Category.objects.get_or_create(name=cat_name)
                        break

                if matched_category is None:
                    matched_category, _ = Category.objects.get_or_create(name="기타")

                if Book.objects.filter(title=title).exists():
                    continue

                Book.objects.create(
                    title=title,
                    author=author,
                    content=content,
                    link=link,
                    img=img,
                    best_seller_rank=str(rank),
                    category=matched_category
                )
                total_count += 1
                print(f"저장 완료: {title}")

            time.sleep(0.3)  # API rate limit 대응을 위한 약간의 딜레이

    print(f"\n✅ 전체 저장 완료: {total_count}권")
    


client = OpenAI(api_key="")

def summarize_top10_books():
    books = Book.objects.exclude(best_seller_rank="").order_by('best_seller_rank')[:2]
    print(f"📚 총 후보 책 수: {len(books)}")
    for book in books:
        if not book.content or book.summary:
            continue

        prompt = f"""
다음은 책 소개입니다. 아래 내용을 바탕으로 핵심 주제나 특징을 한 문장으로 간결하게 요약해 주세요.

[책 소개]
{book.content}

[요약]
"""

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            summary = response.choices[0].message.content.strip()
            book.summary = summary
            book.save()
            print(f"요약 완료: {book.title}")
        except Exception as e:
            print(f"요약 실패: {book.title}, 이유: {e}")