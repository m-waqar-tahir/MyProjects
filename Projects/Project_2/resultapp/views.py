from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import StudentClass, Subject, Student, Result, ResultDetail, Notice
from .forms import (
    StudentClassForm, SubjectForm, StudentForm, StudentEditForm,
    ResultForm, ResultEditForm, ResultDetailFormSet, SearchResultForm,
    NoticeForm, ChangePasswordForm
)


def index(request):
    search_form = SearchResultForm()
    notices = Notice.objects.all()[:10]
    context = {'search_form': search_form, 'notices': notices}
    return render(request, 'index.html', context)


def admin_login(request):
    if request.user.is_authenticated:
        return redirect('admin-dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, 'Logged in successfully')
            return redirect('admin-dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions')
            return redirect('admin-login')

    return render(request, 'admin_login.html')


@login_required(login_url='admin-login')
def admin_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('admin-login')


@login_required(login_url='admin-login')
def admin_dashboard(request):
    context = {
        'total_classes': StudentClass.objects.count(),
        'total_subjects': Subject.objects.count(),
        'total_students': Student.objects.count(),
        'total_results': Result.objects.count(),
        'total_notices': Notice.objects.count(),
        'recent_results': Result.objects.select_related('student', 'student_class').all()[:5],
    }
    return render(request, 'admin_dashboard.html', context)


@login_required(login_url='admin-login')
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            if request.user.check_password(old_password):
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password changed successfully')
                return redirect('admin-dashboard')
            else:
                messages.error(request, 'Current password is incorrect')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = ChangePasswordForm()
    context = {'form': form}
    return render(request, 'change_password.html', context)


# ---------------- Class management ----------------

@login_required(login_url='admin-login')
def manage_class(request):
    classes_qs = StudentClass.objects.all()
    paginator = Paginator(classes_qs, 10)
    classes = paginator.get_page(request.GET.get('page'))
    context = {'classes': classes, 'extra_qs': ''}
    return render(request, 'manage_class.html', context)


@login_required(login_url='admin-login')
def add_class(request):
    if request.method == 'POST':
        form = StudentClassForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class added successfully')
            return redirect('manage-class')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = StudentClassForm()
    context = {'form': form}
    return render(request, 'add_class.html', context)


@login_required(login_url='admin-login')
def edit_class(request, class_id):
    student_class = get_object_or_404(StudentClass, id=class_id)
    if request.method == 'POST':
        form = StudentClassForm(request.POST, instance=student_class)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class updated successfully')
            return redirect('manage-class')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = StudentClassForm(instance=student_class)
    context = {'form': form, 'student_class': student_class}
    return render(request, 'edit_class.html', context)


@login_required(login_url='admin-login')
def delete_class(request, class_id):
    student_class = get_object_or_404(StudentClass, id=class_id)
    student_class.delete()
    messages.success(request, 'Class deleted successfully')
    return redirect('manage-class')


# ---------------- Subject management ----------------

@login_required(login_url='admin-login')
def manage_subject(request):
    subjects_qs = Subject.objects.select_related('student_class').all()
    class_id = request.GET.get('class_id', '')
    if class_id:
        subjects_qs = subjects_qs.filter(student_class_id=class_id)
    paginator = Paginator(subjects_qs, 10)
    subjects = paginator.get_page(request.GET.get('page'))
    classes = StudentClass.objects.all()
    extra_qs = f'class_id={class_id}' if class_id else ''
    context = {
        'subjects': subjects,
        'classes': classes,
        'selected_class': class_id,
        'extra_qs': extra_qs,
    }
    return render(request, 'manage_subject.html', context)


@login_required(login_url='admin-login')
def add_subject(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject added successfully')
            return redirect('manage-subject')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = SubjectForm()
    context = {'form': form}
    return render(request, 'add_subject.html', context)


@login_required(login_url='admin-login')
def edit_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject updated successfully')
            return redirect('manage-subject')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = SubjectForm(instance=subject)
    context = {'form': form, 'subject': subject}
    return render(request, 'edit_subject.html', context)


@login_required(login_url='admin-login')
def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    subject.delete()
    messages.success(request, 'Subject deleted successfully')
    return redirect('manage-subject')


# ---------------- Student management ----------------

@login_required(login_url='admin-login')
def manage_student(request):
    students_qs = Student.objects.select_related('student_class').all()
    class_id = request.GET.get('class_id', '')
    if class_id:
        students_qs = students_qs.filter(student_class_id=class_id)
    paginator = Paginator(students_qs, 10)
    students = paginator.get_page(request.GET.get('page'))
    classes = StudentClass.objects.all()
    extra_qs = f'class_id={class_id}' if class_id else ''
    context = {
        'students': students,
        'classes': classes,
        'selected_class': class_id,
        'extra_qs': extra_qs,
    }
    return render(request, 'manage_student.html', context)


@login_required(login_url='admin-login')
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student added successfully')
            return redirect('manage-student')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = StudentForm()
    context = {'form': form}
    return render(request, 'add_student.html', context)


@login_required(login_url='admin-login')
def edit_student(request, student_id):
    student_obj = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        form = StudentEditForm(request.POST, request.FILES, instance=student_obj)
        try:
            if form.is_valid():
                form.save()
                messages.success(request, 'Student updated successfully')
                return redirect('manage-student')
            else:
                messages.error(request, 'Please correct the errors below')
        except Exception:
            messages.error(request, 'Something went wrong while updating the student')
    else:
        form = StudentEditForm(instance=student_obj)
    context = {'form': form, 'student': student_obj}
    return render(request, 'edit_student.html', context)


@login_required(login_url='admin-login')
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.delete()
    messages.success(request, 'Student deleted successfully')
    return redirect('manage-student')


# ---------------- Result management ----------------

@login_required(login_url='admin-login')
def manage_result(request):
    results_qs = Result.objects.select_related('student', 'student_class').all()
    class_id = request.GET.get('class_id', '')
    if class_id:
        results_qs = results_qs.filter(student_class_id=class_id)
    paginator = Paginator(results_qs, 10)
    results = paginator.get_page(request.GET.get('page'))
    classes = StudentClass.objects.all()
    extra_qs = f'class_id={class_id}' if class_id else ''
    context = {
        'results': results,
        'classes': classes,
        'selected_class': class_id,
        'extra_qs': extra_qs,
    }
    return render(request, 'manage_result.html', context)


@login_required(login_url='admin-login')
def add_result(request):
    classes = StudentClass.objects.all()

    if request.method == 'POST':
        class_id = request.POST.get('student_class')
        student_id = request.POST.get('student')
        exam_name = request.POST.get('exam_name')
        exam_date = request.POST.get('exam_date')

        marks_data = {
            key.split('_')[1]: value
            for key, value in request.POST.items()
            if key.startswith('marks_') and value
        }

        try:
            result = Result.objects.create(
                student_id=student_id,
                student_class_id=class_id,
                exam_name=exam_name,
                exam_date=exam_date,
            )
            for subject_id, marks in marks_data.items():
                ResultDetail.objects.create(
                    result=result,
                    subject_id=subject_id,
                    marks_obtained=marks,
                )
            messages.success(request, 'Result info added successfully')
            return redirect('add-result')
        except Exception:
            messages.error(request, 'Something went wrong while adding the result')

    context = {'classes': classes}
    return render(request, 'add_result.html', context)


@login_required(login_url='admin-login')
def get_students_subjects(request):
    """
    AJAX endpoint used by the Add Result page. Given a class_id GET
    parameter, returns the students enrolled in that class and the
    subjects assigned to that class, so the frontend can populate
    the dependent student dropdown and the dynamic marks fields
    without a full page reload.
    """
    class_id = request.GET.get('class_id')

    if class_id:
        students_qs = Student.objects.filter(
            student_class_id=class_id, is_active=True
        ).values('id', 'first_name', 'last_name', 'roll_number')

        students = [
            {
                'id': s['id'],
                'name': f"{s['first_name']} {s['last_name']}",
                'roll_number': s['roll_number'],
            }
            for s in students_qs
        ]

        subjects_qs = Subject.objects.filter(student_class_id=class_id)
        subjects = [
            {'id': subject.id, 'subject_name': subject.subject_name}
            for subject in subjects_qs
        ]
    else:
        students = []
        subjects = []

    return JsonResponse({'students': students, 'subjects': subjects})


@login_required(login_url='admin-login')
def edit_result(request, result_id):
    result = get_object_or_404(Result, id=result_id)
    if request.method == 'POST':
        form = ResultEditForm(request.POST, instance=result)
        formset = ResultDetailFormSet(request.POST, instance=result)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Result updated successfully')
            return redirect('edit-result', result_id=result.id)
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = ResultEditForm(instance=result)
        formset = ResultDetailFormSet(instance=result)
    context = {'form': form, 'formset': formset, 'result': result}
    return render(request, 'edit_result.html', context)


@login_required(login_url='admin-login')
def delete_result(request, result_id):
    result = get_object_or_404(Result, id=result_id)
    result.delete()
    messages.success(request, 'Result deleted successfully')
    return redirect('manage-result')


@login_required(login_url='admin-login')
def view_result(request, result_id):
    result = get_object_or_404(Result, id=result_id)
    details = result.details.select_related('subject').all()
    context = {'result': result, 'details': details}
    return render(request, 'view_result.html', context)


def print_result(request, result_id):
    result = get_object_or_404(Result, id=result_id)
    details = result.details.select_related('subject').all()
    context = {'result': result, 'details': details}
    return render(request, 'print_result.html', context)


def search_result(request):
    """
    Public "check your result" page. A visitor enters their roll
    number (and optionally an exam name) and is shown every matching
    result with a link to a printable copy.

    Three outcomes are distinguished so the visitor gets an accurate
    message instead of a single generic "not found" line:
      1. No student exists with that roll number at all.
      2. The student exists, but no result has been declared for
         them yet (or none matches the exam name filter).
      3. One or more matching results were found.
    """
    results = None
    searched = False
    student_found = None

    if request.method == 'POST':
        form = SearchResultForm(request.POST)
        searched = True
        if form.is_valid():
            roll_number = form.cleaned_data['roll_number']
            exam_name = form.cleaned_data['exam_name']
            student = Student.objects.filter(roll_number__iexact=roll_number).first()
            student_found = student is not None
            if student:
                results = Result.objects.filter(student=student)
                if exam_name:
                    results = results.filter(exam_name__icontains=exam_name)
            else:
                messages.error(request, 'No student found with this roll number')
    else:
        form = SearchResultForm()

    context = {
        'form': form,
        'results': results,
        'searched': searched,
        'student_found': student_found,
    }
    return render(request, 'search_result.html', context)


def notice_detail(request, notice_id):
    """
    Public notice detail page. Clicked from the scrolling notice
    board on the home page (opens in a new tab), it shows the full
    title, posting date and description for a single notice. No
    login is required since this is visitor-facing, the same as the
    result search/print pages.
    """
    notice = get_object_or_404(Notice, id=notice_id)
    context = {'notice': notice}
    return render(request, 'notice_detail.html', context)


# ---------------- Notice board management ----------------

@login_required(login_url='admin-login')
def manage_notice(request):
    notices_qs = Notice.objects.all()
    paginator = Paginator(notices_qs, 10)
    notices = paginator.get_page(request.GET.get('page'))
    context = {'notices': notices, 'extra_qs': ''}
    return render(request, 'manage_notice.html', context)


@login_required(login_url='admin-login')
def add_notice(request):
    if request.method == 'POST':
        form = NoticeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notice added successfully')
            return redirect('manage-notice')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = NoticeForm()
    context = {'form': form}
    return render(request, 'add_notice.html', context)


@login_required(login_url='admin-login')
def edit_notice(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)
    if request.method == 'POST':
        form = NoticeForm(request.POST, instance=notice)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notice updated successfully')
            return redirect('manage-notice')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = NoticeForm(instance=notice)
    context = {'form': form, 'notice': notice}
    return render(request, 'edit_notice.html', context)


@login_required(login_url='admin-login')
def delete_notice(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)
    notice.delete()
    messages.success(request, 'Notice deleted successfully')
    return redirect('manage-notice')