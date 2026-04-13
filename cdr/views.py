from datetime import datetime, time, timedelta
from io import BytesIO

from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils import timezone
from django.views import View
from django.views.generic import ListView
from openpyxl import Workbook

from .forms import CdrFilterForm
from .models import CdrRecord


class CdrQueryMixin(LoginRequiredMixin):
    displayed_fields = [
        "date_time_origination",
        "calling_party_number",
        "calling_party_unicode_login_user_id",
        "original_called_party_number",
        "final_called_party_number",
        "final_called_party_unicode_login_user_id",
        "dest_cause_location",
        "dest_cause_value",
        "date_time_connect",
        "date_time_disconnect",
        "last_redirect_dn",
        "duration",
    ]
    login_url = "login"

    def get_form(self) -> CdrFilterForm:
        return CdrFilterForm(self.request.GET or None)

    def get_filtered_queryset(self):
        queryset = (
            CdrRecord.objects.only(
                "global_call_id_call_id",
                *self.displayed_fields,
            )
            .order_by("-date_time_origination", "-global_call_id_call_id")
        )

        self.form = self.get_form()
        if not self.form.is_valid():
            return queryset

        phone_number = self.form.cleaned_data.get("phone_number")
        start_date = self.form.cleaned_data.get("start_date")
        end_date = self.form.cleaned_data.get("end_date")

        if phone_number:
            queryset = queryset.filter(
                Q(calling_party_number__icontains=phone_number)
                | Q(original_called_party_number__icontains=phone_number)
                | Q(final_called_party_number__icontains=phone_number)
                | Q(last_redirect_dn__icontains=phone_number)
            )

        current_tz = timezone.get_current_timezone()

        if start_date:
            start_dt = timezone.make_aware(
                datetime.combine(start_date, time.min),
                current_tz,
            )
            queryset = queryset.filter(date_time_origination__gte=start_dt)

        if end_date:
            end_dt = timezone.make_aware(
                datetime.combine(end_date + timedelta(days=1), time.min),
                current_tz,
            )
            queryset = queryset.filter(date_time_origination__lt=end_dt)

        return queryset

    def get_query_string(self) -> str:
        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        return query_params.urlencode()


class CdrListView(CdrQueryMixin, ListView):
    model = CdrRecord
    template_name = "cdr/cdr_list.html"
    context_object_name = "records"
    paginate_by = 100

    def get_queryset(self):
        return self.get_filtered_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = getattr(self, "form", self.get_form())

        context["form"] = form
        context["query_string"] = self.get_query_string()
        context["displayed_fields"] = self.displayed_fields
        return context


class CdrExportView(CdrQueryMixin, View):
    column_headers = [
        "Date/Time Origination",
        "Calling Party Number",
        "Calling Party User ID",
        "Original Called Party Number",
        "Final Called Party Number",
        "Final Called Party User ID",
        "Dest Cause Location",
        "Dest Cause Value",
        "Date/Time Connect",
        "Date/Time Disconnect",
        "Last Redirect DN",
        "Duration",
    ]

    def get(self, request, *args, **kwargs):
        queryset = self.get_filtered_queryset().values_list(*self.displayed_fields)

        workbook = Workbook(write_only=True)
        worksheet = workbook.create_sheet(title="CDRs")
        worksheet.append(self.column_headers)

        current_tz = timezone.get_current_timezone()
        datetime_fields = {
            "date_time_origination",
            "date_time_connect",
            "date_time_disconnect",
        }

        for row in queryset.iterator(chunk_size=2000):
            export_row = []
            for field_name, value in zip(self.displayed_fields, row):
                if value is not None and field_name in datetime_fields:
                    value = timezone.localtime(value, current_tz).replace(tzinfo=None)
                export_row.append(value)
            worksheet.append(export_row)

        content = BytesIO()
        workbook.save(content)
        content.seek(0)

        timestamp = timezone.localtime(timezone.now(), current_tz).strftime("%Y%m%d_%H%M%S")
        response = HttpResponse(
            content.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f'attachment; filename="cdr_export_{timestamp}.xlsx"'
        return response
