# books/utils.py

import requests
from .models import Book, Category

def fetch_aladin_books():
    url = "http://www.aladin.co.kr/ttb/api/ItemList.aspx"
    params = {
        "ttbkey": "API입력하세요요",  
        "QueryType": "Bestseller",
        "MaxResults": 20,
        "start": 1,
        "SearchTarget": "Book",
        "output": "js",
        "Version": "20131101"
    }

    response = requests.get(url, params=params)
    data = response.json()

    for item in data.get("item", []):
        title = item.get("title")
        author = item.get("author")
        content = item.get("description")
        link = item.get("link")
        img = item.get("cover")
        rank = item.get("customerReviewRank", 0)
        aladin_category = item.get("categoryName", "")  # 알라딘 카테고리명

        # 🧠 너의 DB 카테고리 이름과 포함 매칭
        matched_category = None
        category_keywords = {
            "소설": "소설/시/희곡",
            "경제": "경제/경영",
            "자기계발": "자기계발",
            "인문": "인문/교양",
            "실용": "취미/실용",
            "어린이": "어린이/청소년",
            "과학": "과학"
        }

        for keyword, cat_name in category_keywords.items():
            if keyword in aladin_category:
                matched_category, _ = Category.objects.get_or_create(name=cat_name)
                break

        # 매칭 안 되면 기본 카테고리로 처리
        if matched_category is None:
            matched_category, _ = Category.objects.get_or_create(name="기타")

        # 중복 방지
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