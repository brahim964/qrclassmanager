import io, json, qrcode
from django.core.files import File
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Class

@receiver(post_save, sender=Class)
def generate_qr(sender, instance, created, **kwargs):
    """
    Crea o regenera el QR y lo guarda en qr_image.
    La segunda llamada a save() usa update_fields para no disparar la señal de nuevo.
    """
    # --- genera el payload (ajústalo a gusto) ---
    payload = json.dumps({
        "class_id": instance.id,
        "ts": timezone.now().isoformat(),
    })

    # --- crea la imagen ---
    img = qrcode.make(payload)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    filename = f"class_{instance.id}.png"

    # --- asigna al campo FileField sin disparar save() automáticamente ---
    instance.qr_image.save(filename, File(buffer), save=False)

    # --- persiste solo el campo qr_image ---
    sender.objects.filter(pk=instance.pk).update(qr_image=instance.qr_image.name)
