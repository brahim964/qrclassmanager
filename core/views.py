from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q

from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Room, Teacher, Class, Student, Enrollment, Attendance
from .serializers import (
    RoomSerializer, TeacherSerializer, ClassSerializer,
    StudentSerializer, EnrollmentSerializer, AttendanceSerializer,
)

import csv

# -------------------------------
# ViewSets
# -------------------------------

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer


class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.all().select_related("teacher")
    serializer_class = ClassSerializer

    @extend_schema(
        summary="Check-in manual (web)",
        description="Registra manualmente la asistencia de un alumno a una clase específica.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "student_id": {"type": "integer", "example": 1}
                },
                "required": ["student_id"]
            }
        },
        responses={
            200: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"}
                },
                "example": {"success": True}
            },
            400: {
                "type": "object",
                "properties": {
                    "error": {"type": "string"}
                },
                "example": {"error": "student_id requerido"}
            }
        }
    )
    @action(detail=True, methods=["post"], permission_classes=[AllowAny])
    def checkin(self, request, pk=None):
        student_id = request.data.get("student_id")
        if not student_id:
            return Response({"error": "student_id requerido"}, status=400)

        student = get_object_or_404(Student, pk=student_id)
        clazz = self.get_object()

        Attendance.objects.create(student=student, clazz=clazz, method="web")
        return Response({"success": True})


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

# -------------------------------
# API Functions
# -------------------------------

@extend_schema(
    summary="Check-in/check-out por QR",
    description="Permite al estudiante hacer check-in o check-out escaneando un QR. "
                "Si ya existe un check-in hoy, se marca como check-out.",
    parameters=[
        OpenApiParameter(name="token", location=OpenApiParameter.QUERY, required=True, description="Token QR de la clase")
    ],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "student_id": {"type": "integer", "example": 1}
            },
            "required": ["student_id"]
        }
    },
    responses={
        200: {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "action": {"type": "string", "enum": ["check_in", "check_out"]}
            },
            "example": {"success": True, "action": "check_in"}
        },
        400: {"description": "Faltan datos requeridos"}
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def attendance_checkin_qr(request):
    token = request.GET.get("token")
    student_id = request.data.get("student_id")

    if not token or not student_id:
        return Response({"error": "token y student_id requeridos"}, status=400)

    clazz = get_object_or_404(Class, qr_token=token)
    student = get_object_or_404(Student, pk=student_id)

    today = timezone.now().date()
    att = Attendance.objects.filter(
        student=student,
        clazz=clazz,
        date=today,
        check_out__isnull=True
    ).first()

    if att:
        att.check_out = timezone.now()
        att.save()
        return Response({"success": True, "action": "check_out"})
    else:
        Attendance.objects.create(student=student, clazz=clazz, method="qr")
        return Response({"success": True, "action": "check_in"})


@extend_schema(
    summary="Exportar asistencias a CSV",
    description="Devuelve un archivo CSV con asistencias filtradas por alumno, clase y rango de fechas.",
    parameters=[
        OpenApiParameter(name="student", location=OpenApiParameter.QUERY, required=False, description="Nombre o apellido del alumno"),
        OpenApiParameter(name="class", location=OpenApiParameter.QUERY, required=False, description="Nombre de la clase"),
        OpenApiParameter(name="from", location=OpenApiParameter.QUERY, required=False, description="Fecha desde (YYYY-MM-DD)"),
        OpenApiParameter(name="to", location=OpenApiParameter.QUERY, required=False, description="Fecha hasta (YYYY-MM-DD)"),
    ],
    responses={
        200: {"description": "Archivo CSV con asistencias"},
        400: {"description": "Error de parámetros (si se agregan validaciones futuras)"},
    }
)
@api_view(['GET'])
def attendance_export_excel(request):
    student_name = request.GET.get("student")
    class_name   = request.GET.get("class")
    date_from    = request.GET.get("from")
    date_to      = request.GET.get("to")

    qs = Attendance.objects.select_related("student", "clazz")

    if student_name:
        qs = qs.filter(
            Q(student__first_name__icontains=student_name) |
            Q(student__last_name__icontains=student_name)
        )
    if class_name:
        qs = qs.filter(clazz__name__icontains=class_name)
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=asistencias.csv'
    writer = csv.writer(response)
    writer.writerow(['Clase', 'Alumno', 'Check-in', 'Check-out', 'Método'])

    for a in qs:
        writer.writerow([
            a.clazz.name,
            f"{a.student.first_name} {a.student.last_name}",
            a.check_in,
            a.check_out or "",
            a.method
        ])

    return response
