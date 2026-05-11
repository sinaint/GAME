from django.conf import settings
from django.db import models


class UserSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_settings",
    )
    nickname = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"{self.user} settings"


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


class UserMemo(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_memos",
    )
    title = models.CharField(max_length=200)
    content = models.TextField(max_length=2000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.title}"


class UserPersona(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_personas",
    )
    title = models.CharField(max_length=100)          # 캐릭터 이름
    age = models.CharField(max_length=30, blank=True)         # 예: 23세 남성
    appearance = models.TextField(max_length=500, blank=True) # 외모
    personality = models.TextField(max_length=500, blank=True)# 성격
    talent = models.TextField(max_length=500, blank=True)     # 재능/특기
    content = models.TextField(max_length=1000, blank=True)   # 추가 메모
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.title}"
