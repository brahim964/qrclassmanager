from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RoomViewSet,
    TeacherViewSet,
    ClassViewSet,
    StudentViewSet,
    EnrollmentViewSet,
    AttendanceViewSet,
    attendance_checkin_qr,
    attendance_export_excel,
)

# Router de DRF para los ViewSets (CRUD automático)
router = DefaultRouter()
router.register(r"rooms", RoomViewSet)
router.register(r"teachers", TeacherViewSet)
router.register(r"classes", ClassViewSet)
router.register(r"students", StudentViewSet)
router.register(r"enrollments", EnrollmentViewSet)
router.register(r"attendance", AttendanceViewSet)

# Rutas finales para la app core
urlpatterns = [
    path("", include(router.urls)),  # Todas las rutas de los ViewSets
    path("attendance/checkin_qr/", attendance_checkin_qr, name="attendance-checkin-qr"),
    path("attendance/export_excel/", attendance_export_excel, name="attendance-export-excel"),
]
