from django import forms
from .models import Profile


class ProfileForm(forms.ModelForm):
    # 슬롯은 1~3만 선택하도록 드롭다운
    slot = forms.ChoiceField(
        choices=[(1, "슬롯 1"), (2, "슬롯 2"), (3, "슬롯 3")],
        label="슬롯",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    # 성별도 드롭다운
    gender = forms.ChoiceField(
        choices=[("남자", "남자"), ("여자", "여자")],
        label="성별",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Profile
        fields = [
            "slot",
            "name",
            "gender",
            "age",
            "face_text",
            "body_text",
            "vibe_text",
        ]
        labels = {
            "name": "이름",
            "age": "나이",
            "face_text": "외모(얼굴/인상)",
            "body_text": "체형(피지컬)",
            "vibe_text": "분위기(아우라)",
        }
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "예: 천무현"}
            ),
            "age": forms.NumberInput(
                attrs={"class": "form-control", "min": 1, "max": 120}
            ),
            "face_text": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "예: 차가운 인상, 또렷한 이목구비",
                }
            ),
            "body_text": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "예: 탄탄한 근육질, 큰 체격",
                }
            ),
            "vibe_text": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "예: 여유롭고 자신감 있는 분위기",
                }
            ),
        }
