from django.shortcuts import render


def home(request):
    games = [
        {
            "id": 1,
            "title": "무림: 돌아온 당신",
            "desc": "강호의 바람이 다시 분다. 선택이 쌓여 너만의 전설이 된다.",
            "tag": "무협",
            "thumb": "images/thumbs/game1.jpg",
        },
        {
            "id": 2,
            "title": "혈검: 천하제일",
            "desc": "복수와 명예 사이, 칼날 위를 걷는 자의 이야기.",
            "tag": "무협",
            "thumb": "images/thumbs/game2.jpg",
        },
        {
            "id": 3,
            "title": "SF: 잃어버린 행성",
            "desc": "광활한 우주에서 살아남고 진실을 찾아라.",
            "tag": "SF",
            "thumb": "images/thumbs/game3.jpg",
        },
        {
            "id": 4,
            "title": "계절의 끝에서",
            "desc": "다시 만난 너, 고백하지 못한 말들이 아직 남아 있다.",
            "tag": "로맨스",
            "thumb": "images/thumbs/game4.jpg",
        },
        {
            "id": 5,
            "title": "용의 시대",
            "desc": "마법과 검이 공존하는 왕국. 봉인된 고대 신을 깨워라.",
            "tag": "판타지",
            "thumb": "images/thumbs/game5.jpg",
        },
        {
            "id": 6,
            "title": "마지막 도시",
            "desc": "문명이 무너진 세계. 살아남은 자들의 최후의 선택.",
            "tag": "아포칼립스",
            "thumb": "images/thumbs/game6.jpg",
        },
        {
            "id": 7,
            "title": "도시: 미스터리 의뢰",
            "desc": "단서를 모아 사건의 진실을 파헤쳐라. 누가 거짓말을 하고 있는가.",
            "tag": "현대",
            "thumb": "images/thumbs/game7.jpg",
        },
    ]

    return render(request, "main/home.html", {"games": games})
