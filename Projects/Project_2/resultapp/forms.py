from django import forms
from django.forms import inlineformset_factory
from .models import StudentClass, Subject, Student, Result, ResultDetail, Notice


class StudentClassForm(forms.ModelForm):
    class Meta:
        model = StudentClass
        fields = ['class_name']
        widgets = {
            'class_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter class name'
            }),
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['subject_name', 'student_class']
        widgets = {
            'subject_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter subject name'
            }),
            'student_class': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'roll_number', 'first_name', 'last_name', 'student_class',
            'gender', 'date_of_birth', 'guardian_name', 'contact_number',
            'address', 'profile_picture', 'is_active'
        ]
        widgets = {
            'roll_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter roll number'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'}),
            'student_class': forms.Select(attrs={'class': 'form-select'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'guardian_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter guardian name'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter contact number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter address'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class StudentEditForm(StudentForm):
    """
    Same as StudentForm, except the class is locked once a student
    record exists. Changing a student's class after subjects and
    results have been recorded against the old class would break
    result generation, so the class must be fixed at creation time.
    If a student genuinely moves class, deactivate this record and
    add a fresh one instead.
    """

    class Meta(StudentForm.Meta):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student_class'].disabled = True
        self.fields['student_class'].widget.attrs['class'] = 'form-select bg-light'


class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ['student', 'student_class', 'exam_name', 'exam_date']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'student_class': forms.Select(attrs={'class': 'form-select'}),
            'exam_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter exam name'}),
            'exam_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class ResultEditForm(ResultForm):
    """
    Same as ResultForm, except student and class are locked once a
    result exists. The marks recorded already belong to a specific
    student in a specific class's subject set, so reassigning either
    on the edit page would desynchronize the marks from who/what
    they were declared for. Only the exam details and marks should
    change here; delete and re-add the result if the student/class
    was wrong.
    """

    class Meta(ResultForm.Meta):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].disabled = True
        self.fields['student_class'].disabled = True
        self.fields['student'].widget.attrs['class'] = 'form-select bg-light'
        self.fields['student_class'].widget.attrs['class'] = 'form-select bg-light'


class ResultDetailForm(forms.ModelForm):
    class Meta:
        model = ResultDetail
        fields = ['subject', 'marks_obtained', 'max_marks']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'marks_obtained': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'max_marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }


ResultDetailFormSet = inlineformset_factory(
    Result,
    ResultDetail,
    form=ResultDetailForm,
    extra=1,
    can_delete=True
)


class SearchResultForm(forms.Form):
    roll_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter roll number'
        })
    )
    exam_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter exam name (optional)'
        })
    )


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter notice title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter notice details'}),
        }


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter current password'})
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError('New password and confirm password do not match')
        return cleaned_data