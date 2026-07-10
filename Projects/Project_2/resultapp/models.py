from django.db import models


class StudentClass(models.Model):
    class_name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['class_name']

    def __str__(self):
        return self.class_name


class Subject(models.Model):
    subject_name = models.CharField(max_length=100)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE, related_name='subjects')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['subject_name']
        unique_together = ('subject_name', 'student_class')

    def __str__(self):
        return f"{self.subject_name} ({self.student_class.class_name})"


class Student(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    roll_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE, related_name='students')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    guardian_name = models.CharField(max_length=150)
    contact_number = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='students/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.roll_number})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE, related_name='results')
    exam_name = models.CharField(max_length=150)
    exam_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('student', 'exam_name')

    def __str__(self):
        return f"{self.student.full_name} - {self.exam_name}"

    @property
    def total_marks_obtained(self):
        return sum(detail.marks_obtained for detail in self.details.all())

    @property
    def total_max_marks(self):
        return sum(detail.max_marks for detail in self.details.all())

    @property
    def percentage(self):
        total_max = self.total_max_marks
        if total_max == 0:
            return 0
        return round((self.total_marks_obtained / total_max) * 100, 2)

    @property
    def grade(self):
        pct = self.percentage
        if pct >= 90:
            return 'A+'
        elif pct >= 80:
            return 'A'
        elif pct >= 70:
            return 'B'
        elif pct >= 60:
            return 'C'
        elif pct >= 50:
            return 'D'
        else:
            return 'F'

    @property
    def result_status(self):
        return 'Pass' if self.grade != 'F' else 'Fail'


class ResultDetail(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name='details')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2)
    max_marks = models.DecimalField(max_digits=6, decimal_places=2, default=100)

    class Meta:
        unique_together = ('result', 'subject')

    def __str__(self):
        return f"{self.result} - {self.subject.subject_name}"


class Notice(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title