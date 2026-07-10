from django.contrib import admin
from .models import StudentClass, Subject, Student, Result, ResultDetail, Notice


class ResultDetailInline(admin.TabularInline):
    model = ResultDetail
    extra = 1


class ResultAdmin(admin.ModelAdmin):
    inlines = [ResultDetailInline]
    list_display = ('student', 'exam_name', 'exam_date', 'student_class')


admin.site.register(StudentClass)
admin.site.register(Subject)
admin.site.register(Student)
admin.site.register(Result, ResultAdmin)
admin.site.register(Notice)