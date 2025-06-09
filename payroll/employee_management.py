import pandas as pd
from io import BytesIO
from datetime import date
from openpyxl import load_workbook
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter
from rest_framework.permissions import AllowAny
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from .models import PayrollOrg, WorkLocations, Departments, Designation


@api_view(['GET'])
@permission_classes([AllowAny])
def generate_employee_upload_template(request, payroll_id):
    payroll = get_object_or_404(PayrollOrg, id=payroll_id)

    # Column headers only — no sample data
    columns = [
        'first_name', 'middle_name', 'last_name', 'associate_id', 'doj', 'work_email',
        'mobile_number', 'gender', 'work_location', 'designation', 'department',
        'enable_portal_access',
        'epf_enabled', 'pf_account_number', 'uan',
        'esi_enabled', 'esi_number', 'professional_tax',
        'employee_status'
    ]

    df = pd.DataFrame(columns=columns)

    # Create base Excel file in memory
    output = BytesIO()
    df.to_excel(output, index=False, sheet_name='EmployeeUpload')
    output.seek(0)

    # Load workbook and add dropdown sheet
    wb = load_workbook(output)
    ws = wb['EmployeeUpload']
    dropdowns_ws = wb.create_sheet(title='Dropdowns')

    # Gather dropdown values
    genders = ['male', 'female', 'others']
    work_locations = [str(wl) for wl in WorkLocations.objects.filter(payroll=payroll)]
    departments = [str(dept) for dept in Departments.objects.filter(payroll=payroll)]
    designations = [str(desig) for desig in Designation.objects.filter(payroll=payroll)]
    boolean_values = ['TRUE', 'FALSE']

    dropdowns_ws.append(['Genders', 'WorkLocations', 'Departments', 'Designations', 'Boolean'])

    max_len = max(len(genders), len(work_locations), len(departments), len(designations), len(boolean_values))

    for i in range(max_len):
        dropdowns_ws.append([
            genders[i] if i < len(genders) else None,
            work_locations[i] if i < len(work_locations) else None,
            departments[i] if i < len(departments) else None,
            designations[i] if i < len(designations) else None,
            boolean_values[i] if i < len(boolean_values) else None,
        ])

    # Helper to apply dropdown
    def apply_dropdown(field_name, formula_range):
        for col in ws.iter_cols(1, ws.max_column):
            if col[0].value == field_name:
                col_letter = get_column_letter(col[0].column)
                dv = DataValidation(type="list", formula1=f"={formula_range}", allow_blank=True)
                ws.add_data_validation(dv)
                dv.add(f"{col_letter}2:{col_letter}1000")
                break

    # Apply dropdowns
    apply_dropdown("gender", "Dropdowns!$A$2:$A$10")
    apply_dropdown("work_location", "Dropdowns!$B$2:$B$100")
    apply_dropdown("department", "Dropdowns!$C$2:$C$100")
    apply_dropdown("designation", "Dropdowns!$D$2:$D$100")

    for boolean_field in ['enable_portal_access', 'epf_enabled', 'esi_enabled', 'professional_tax', 'employee_status']:
        apply_dropdown(boolean_field, "Dropdowns!$E$2:$E$3")

    final_output = BytesIO()
    wb.save(final_output)
    final_output.seek(0)

    response = HttpResponse(
        final_output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="employee_upload_template.xlsx"'
    return response
