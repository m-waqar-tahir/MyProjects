from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from resultapp.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),

    path('admin-login/', admin_login, name='admin-login'),
    path('admin-logout/', admin_logout, name='admin-logout'),
    path('admin-dashboard/', admin_dashboard, name='admin-dashboard'),
    path('change-password/', change_password, name='change-password'),

    path('manage-class/', manage_class, name='manage-class'),
    path('add-class/', add_class, name='add-class'),
    path('edit-class/<int:class_id>/', edit_class, name='edit-class'),
    path('delete-class/<int:class_id>/', delete_class, name='delete-class'),

    path('manage-subject/', manage_subject, name='manage-subject'),
    path('add-subject/', add_subject, name='add-subject'),
    path('edit-subject/<int:subject_id>/', edit_subject, name='edit-subject'),
    path('delete-subject/<int:subject_id>/', delete_subject, name='delete-subject'),

    path('manage-student/', manage_student, name='manage-student'),
    path('add-student/', add_student, name='add-student'),
    path('edit-student/<int:student_id>/', edit_student, name='edit-student'),
    path('delete-student/<int:student_id>/', delete_student, name='delete-student'),

    path('manage-result/', manage_result, name='manage-result'),
    path('add-result/', add_result, name='add-result'),
    path('get-students-subjects/', get_students_subjects, name='get-students-subjects'),
    path('edit-result/<int:result_id>/', edit_result, name='edit-result'),
    path('delete-result/<int:result_id>/', delete_result, name='delete-result'),
    path('view-result/<int:result_id>/', view_result, name='view-result'),
    path('print-result/<int:result_id>/', print_result, name='print-result'),
    path('search-result/', search_result, name='search-result'),
    path('notice-detail/<int:notice_id>/', notice_detail, name='notice-detail'),

    path('manage-notice/', manage_notice, name='manage-notice'),
    path('add-notice/', add_notice, name='add-notice'),
    path('edit-notice/<int:notice_id>/', edit_notice, name='edit-notice'),
    path('delete-notice/<int:notice_id>/', delete_notice, name='delete-notice'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)