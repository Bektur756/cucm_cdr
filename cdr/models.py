from django.db import models


class CdrRecord(models.Model):
    # Django ORM needs a primary key even for unmanaged tables.
    # Update this field if your imported CUCM table uses a different unique key.
    global_call_id_call_id = models.BigIntegerField(primary_key=True)
    date_time_origination = models.DateTimeField()
    calling_party_number = models.CharField(max_length=64, blank=True, null=True)
    calling_party_unicode_login_user_id = models.CharField(
        max_length=256, blank=True, null=True
    )
    original_called_party_number = models.CharField(
        max_length=64, blank=True, null=True
    )
    final_called_party_number = models.CharField(max_length=64, blank=True, null=True)
    final_called_party_unicode_login_user_id = models.CharField(
        max_length=256, blank=True, null=True
    )
    dest_cause_location = models.IntegerField(blank=True, null=True)
    dest_cause_value = models.IntegerField(blank=True, null=True)
    date_time_connect = models.DateTimeField(blank=True, null=True)
    date_time_disconnect = models.DateTimeField(blank=True, null=True)
    last_redirect_dn = models.CharField(max_length=64, blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "cucm_cdr"
        ordering = ["-date_time_origination"]

