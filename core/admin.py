from django.contrib import admin
from django.http import HttpResponse
import csv

from .models import Room, Teacher, Class, Student, Enrollment, Attendance

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'capacity']
    search_fields = ['name']

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'phone']
    search_fields = ['first_name', 'last_name', 'email']

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'room', 'teacher', 'weekday', 'start_time', 'end_time', 'capacity_override']
    list_filter = ['room', 'teacher', 'weekday']
    search_fields = ['name', 'teacher__first_name', 'teacher__last_name']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'dni']
    search_fields = ['first_name', 'last_name', 'email', 'dni']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'clazz', 'status', 'created']
    list_filter = ['clazz', 'status']
    search_fields = ['student__first_name', 'student__last_name', 'clazz__name']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'clazz', 'date', 'check_in', 'check_out', 'method']
    list_filter = ['clazz', 'student', 'date', 'method']
    search_fields = ['student__first_name', 'student__last_name', 'clazz__name']
    readonly_fields = ['check_in']

    actions = ["export_as_csv"]

    def export_as_csv(self, request, queryset):
        """
        Exportar asistencias seleccionadas a un archivo CSV
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=asistencias.csv'
        writer = csv.writer(response)
        writer.writerow(['Clase', 'Alumno', 'DNI', 'Fecha', 'Check-in', 'Check-out', 'Método'])
        for a in queryset.select_related("student", "clazz"):
            writer.writerow([
                a.clazz.name,
                f"{a.student.first_name} {a.student.last_name}",
                a.student.dni,
                a.date,
                a.check_in.strftime("%Y-%m-%d %H:%M"),
                a.check_out.strftime("%Y-%m-%d %H:%M") if a.check_out else "",
                a.method,
            ])
        return response

    export_as_csv.short_description = "Exportar asistencias seleccionadas a CSV"
