from django.conf import settings
from django.db import models


class Profile(models.Model):
    # 각 유저는 최대 3개의 프로필 슬롯을 가짐 (slot = 1~3)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profiles",
    )
    slot = models.PositiveSmallIntegerField()  # 1~3

    # 기본 정보
    name = models.CharField(max_length=20)
    gender = models.CharField(max_length=10)  # "남", "여" 등
    age = models.PositiveSmallIntegerField()

    # 외모/체형/분위기: 유저 입력 텍스트
    face_text = models.CharField(max_length=200, blank=True)
    body_text = models.CharField(max_length=200, blank=True)
    vibe_text = models.CharField(max_length=200, blank=True)

    # 내부 등급: S/A/B/C/D (유저에게는 숨김)
    face_grade = models.CharField(max_length=1, default="C")
    body_grade = models.CharField(max_length=1, default="C")
    vibe_grade = models.CharField(max_length=1, default="C")

    # 소프트 삭제(휴지통): 삭제 버튼 누르면 바로 삭제가 아니라 표시만
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # 한 유저는 같은 슬롯 번호를 중복으로 못 씀
        constraints = [
            models.UniqueConstraint(fields=["user", "slot"], name="unique_user_slot")
        ]

    def __str__(self) -> str:
        return f"{self.user}#{self.slot} - {self.name}"
