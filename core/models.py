from django.db import models
import uuid

class Room(models.Model):
    name = models.CharField(max_length=120, unique=True)
    capacity = models.PositiveSmallIntegerField(default=40)
    def __str__(self):
        return self.name

class Teacher(models.Model):
    first_name = models.CharField(max_length=60)
    last_name  = models.CharField(max_length=60)
    email      = models.EmailField(unique=True)
    phone      = models.CharField(max_length=20, blank=True)
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Class(models.Model):
    WEEKDAYS = [
        (0, "Lunes"), (1, "Martes"), (2, "Miércoles"),
        (3, "Jueves"), (4, "Viernes"), (5, "Sábado"), (6, "Domingo"),
    ]
    name         = models.CharField(max_length=120)
    room         = models.ForeignKey(Room, on_delete=models.PROTECT, related_name="classes")
    teacher      = models.ForeignKey(Teacher, on_delete=models.PROTECT, related_name="classes")
    weekday      = models.IntegerField(choices=WEEKDAYS)
    start_time   = models.TimeField()
    end_time     = models.TimeField()
    capacity_override = models.PositiveSmallIntegerField(null=True, blank=True)
    qr_image     = models.ImageField(upload_to="class_qr/", blank=True)
    qr_token     = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True)  # Sin unique

    @property
    def capacity(self):
        return self.capacity_override or self.room.capacity or 40

    def __str__(self):
        return self.name

class Student(models.Model):
    first_name = models.CharField(max_length=60)
    last_name  = models.CharField(max_length=60)
    email      = models.EmailField(unique=True)
    dni        = models.CharField(max_length=20, unique=True)
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Enrollment(models.Model):
    class Meta:
        unique_together = ("student", "clazz")
    ACTIVE   = "A"
    CANCELED = "C"
    STATUS_CHOICES = [(ACTIVE, "Activo"), (CANCELED, "Baja")]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments")
    clazz   = models.ForeignKey(Class,   on_delete=models.CASCADE, related_name="enrollments")
    status  = models.CharField(max_length=1, choices=STATUS_CHOICES, default=ACTIVE)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.student} → {self.clazz}"

class Attendance(models.Model):
    clazz    = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="attendances")
    student  = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendances")
    date     = models.DateField(auto_now_add=True)
    check_in = models.DateTimeField(auto_now_add=True)
    check_out = models.DateTimeField(null=True, blank=True)
    method = models.CharField(max_length=10, default="web", blank=True)  # Para distinguir QR/web
    def __str__(self):
        return f"{self.student} @ {self.clazz} ({self.date})"
