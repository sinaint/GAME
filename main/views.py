# main/views.py
from django.shortcuts import render


def home(request):
    # 홈에서 보여줄 게임 카드 목록(지금은 하드코딩, 나중에 DB로 변경 가능)
    games = [
        {
            "id": 1,
            "title": "무림: 돌아온 당신",
            "desc": "선택이 쌓여 너만의 이야기가 된다.",
            "tag": "무협",
            "thumb": "images/thumbs/game1.jpg",
        },
        {
            "id": 2,
            "title": "도시: 미스터리 의뢰",
            "desc": "단서를 모아 사건의 진실을 파헤쳐라.",
            "tag": "현대",
            "thumb": "images/thumbs/game2.jpg",
        },
        {
            "id": 3,
            "title": "SF: 잃어버린 행성",
            "desc": "우주에서 살아남고 탈출하라.",
            "tag": "SF",
            "thumb": "images/thumbs/game3.jpg",
        },
    ]

    # 실제로는 게임 선택 -> 프로필 선택이 자연스러우니,
    # 카드 클릭 시 profiles:list로 보내는 흐름으로 시작해도 된다.
    return render(request, "main/home.html", {"games": games})
