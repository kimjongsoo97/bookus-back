from django.urls import path
from . import views

app_name="contents"
urlpatterns = [
    # 기본 컨텐츠 엔드포인트
    path('', views.content_list, name='content-list'),  # 전체 컨텐츠 조회
    path('detail/<int:content_id>/', views.content_detail, name='content-detail'),  # 컨텐츠 상세 조회
    path('create/', views.content_create, name='content-create'),  # 컨텐츠 생성
    path('delete/<int:content_id>/', views.content_delete, name='content-delete'),  # 컨텐츠 삭제
    # 토론 답글
    path('<int:content_id>/discussion/replies/', views.discussion_reply_create, name='discussion-reply-create'),
    # 퀴즈 답글
    path('<int:content_id>/quiz/replies/', views.quiz_reply_create, name='quiz-reply-create'),
    # 독후감
    path('<int:content_id>/book-reviews/', views.book_review_create, name='book-review-create'),
    path('<int:content_id>/book-reviews/compilation/', views.book_review_compilation, name='book-review-compilation'),
    path('<int:content_id>/quiz/replies/delete/<int:reply_id>/',views.quiz_reply_delete,name='quiz-reply-delete'),
    path('<int:content_id>/book-review/delete/<int:reply_id>/',views.book_review_delete,name='book-review-delete'),
    path('<int:content_id>/discussion/replies/delete/<int:reply_id>/',views.discussion_reply_delete,name='discussion-reply-delete')
]