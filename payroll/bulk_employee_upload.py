import json
import pandas as pd
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

# Import your models accordingly
from .models import (
    EmployeeManagement,
    EmployeePersonalDetails,
    EmployeeBankDetails,
    WorkLocations,
    Designation,
    Departments,
)
from datetime import datetime


def parse_excel_date(date_str):
    try:
        return datetime.strptime(date_str.strip(), "%m/%d/%Y").date()
    except Exception:
        try:
            return datetime.strptime(date_str.strip(), "%d/%m/%Y").date()
        except Exception:
            try:
                return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
            except Exception:
                try:
                    if isinstance(date_str, datetime):
                        return date_str.date()
                except Exception:
                    return None



@api_view(['POST'])
@permission_classes([AllowAny])
def upload_employee_excel(request):
    payroll_id = request.data.get('payroll_id')
    file_obj = request.FILES.get('file')

    if not payroll_id:
        return Response({"error": "payroll_id parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        payroll_obj_id = int(payroll_id)
    except ValueError:
        return Response({"error": "Invalid payroll_id parameter."}, status=status.HTTP_400_BAD_REQUEST)

    if not file_obj:
        return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

    file_name = file_obj.name.lower()
    try:
        if file_name.endswith('.xlsx'):
            df = pd.read_excel(file_obj, sheet_name='EmployeeUpload', engine='openpyxl')
        elif file_name.endswith('.xls'):
            df = pd.read_excel(file_obj, sheet_name='EmployeeUpload', engine='xlrd')
        elif file_name.endswith('.csv'):
            df = pd.read_csv(file_obj)
        else:
            return Response({"error": "Unsupported file format. Please upload .xlsx, .xls or .csv"}, status=400)
    except Exception as e:
        return Response({"error": f"Failed to read Excel file: {str(e)}"}, status=400)

    # Required columns except payroll_id (removed from Excel)
    required_columns = [
        'first_name', 'last_name', 'associate_id', 'doj', 'work_email', 'gender', 'work_location', 'designation',
        'department',
        'enable_portal_access', 'epf_enabled', 'pf_account_number', 'uan',
        'esi_enabled', 'esi_number', 'professional_tax', 'employee_status',
        'dob', 'age', 'guardian_name', 'pan', 'aadhar', 'address_line1',
        'address_city', 'address_state', 'address_pinCode',
        'alternate_contact_number', 'marital_status', 'blood_group',
        'account_holder_name', 'bank_name', 'account_number', 'ifsc_code', 'branch_name',
    ]

    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        return Response({"error": f"Missing required columns: {missing_cols}"}, status=status.HTTP_400_BAD_REQUEST)

    # Mandatory fields except pan and uan
    mandatory_fields = [
        'first_name', 'last_name', 'associate_id', 'doj', 'work_email', 'gender', 'work_location', 'designation',
        'department',
        'enable_portal_access', 'epf_enabled',
        'esi_enabled', 'professional_tax', 'employee_status',
        'dob', 'age', 'guardian_name', 'aadhar', 'address_line1',
        'address_city', 'address_state', 'address_pinCode',
        'marital_status', 'blood_group',
        'account_holder_name', 'bank_name', 'account_number', 'ifsc_code',
    ]

    errors = []

    # Check missing mandatory fields with vectorized pandas
    for field in mandatory_fields:
        missing_idx = df[df[field].isna() | (df[field].astype(str).str.strip() == '')].index + 2
        if len(missing_idx) > 0:
            errors.append(f"Mandatory field '{field}' missing or empty in rows: {missing_idx.tolist()}")

    if errors:
        return Response({"error": errors}, status=status.HTTP_400_BAD_REQUEST)

    # Check duplicates inside the file for unique fields (work_email, uan, pan, aadhar, account_number)
    unique_fields = ['work_email', 'uan', 'pan', 'account_number']
    for field in unique_fields:
        non_empty = df[field].dropna().astype(str).str.strip()
        duplicates = non_empty[non_empty.duplicated(keep=False)].index + 2
        if len(duplicates) > 0:
            errors.append(f"Duplicate values found in upload file for '{field}' in rows: {duplicates.tolist()}")

    if errors:
        return Response({"error": errors}, status=status.HTTP_400_BAD_REQUEST)

    # Strip and filter unique values to check against DB
    def clean_unique_vals(series):
        return list(set(series.dropna().astype(str).str.strip()))

    work_emails = clean_unique_vals(df['work_email'])
    uans = [val for val in clean_unique_vals(df['uan']) if val]
    pans = [val for val in clean_unique_vals(df['pan']) if val]
    aadhars = clean_unique_vals(df['aadhar'])
    account_numbers = clean_unique_vals(df['account_number'])
    associate_ids = clean_unique_vals(df['associate_id'])

    # Batch DB lookups for existing unique fields
    existing_work_emails = set(EmployeeManagement.objects.filter(work_email__in=work_emails, payroll=payroll_id).values_list('work_email', flat=True))
    existing_pans = set(EmployeePersonalDetails.objects.filter(pan__in=pans).values_list('pan', flat=True)) if pans else set()
    existing_aadhars = set(EmployeePersonalDetails.objects.filter(aadhar__in=aadhars).values_list('aadhar', flat=True))
    existing_account_numbers = set(EmployeeBankDetails.objects.filter(account_number__in=account_numbers).values_list('account_number', flat=True))
    existing_associate_ids = set(EmployeeManagement.objects.filter(associate_id__in=associate_ids, payroll=payroll_id).values_list('associate_id', flat=True))

    # Check conflicts with DB existing data
    for idx, row in df.iterrows():
        row_num = idx + 2
        if row['work_email'] in existing_work_emails:
            errors.append(f"Row {row_num}: work_email '{row['work_email']}' already exists in database.")
        if str(row.get('pan', '')).strip() and str(row['pan']).strip() in existing_pans:
            errors.append(f"Row {row_num}: pan '{row['pan']}' already exists in database.")
        if row['aadhar'] in existing_aadhars:
            errors.append(f"Row {row_num}: aadhar '{row['aadhar']}' already exists in database.")
        if row['account_number'] in existing_account_numbers:
            errors.append(f"Row {row_num}: account_number '{row['account_number']}' already exists in database.")
        if row['associate_id'] in existing_associate_ids:
            errors.append(f"Row {row_num}: associate_id '{row['associate_id']}' already exists in database.")

    if errors:
        return Response({"error": errors}, status=status.HTTP_400_BAD_REQUEST)

    # Cache all related FK objects by name to reduce DB hits
    work_location_names = df['work_location'].dropna().astype(str).str.strip().unique().tolist()
    designation_names = df['designation'].dropna().astype(str).str.strip().unique().tolist()
    department_names = df['department'].dropna().astype(str).str.strip().unique().tolist()

    work_locations_map = {wl.location_name.strip().lower(): wl for wl in WorkLocations.objects.filter(location_name__in=work_location_names, payroll=payroll_id)}
    designations_map = {d.designation_name.strip().lower(): d for d in Designation.objects.filter(designation_name__in=designation_names, payroll=payroll_id)}
    departments_map = {dep.dept_name.strip().lower(): dep for dep in Departments.objects.filter(dept_name__in=department_names, payroll=payroll_id)}

    success_count = 0

    for idx, row in df.iterrows():
        row_num = idx + 2

        # Validate address JSON
        address_json = {
            "address_line1": row.get('address_line1', '').strip(),
            "address_line2": row.get('address_line2', '').strip() if not pd.isna(row.get('address_line2')) else "",
            "address_city": row.get('address_city', '').strip(),
            "address_state": row.get('address_state', '').strip(),
            "address_pinCode": str(row.get('address_pinCode', '')).strip()
        }

        missing_address_fields = [k for k, v in address_json.items() if k != "address_line2" and not v]
        if missing_address_fields:
            errors.append(f"Row {row_num}: Missing required address fields: {missing_address_fields}")
            continue

        try:
            # FK validation from cached maps by name (case-insensitive)
            work_location_obj = work_locations_map.get(str(row['work_location']).strip().lower())
            designation_obj = designations_map.get(str(row['designation']).strip().lower())
            department_obj = departments_map.get(str(row['department']).strip().lower())

            if not work_location_obj:
                errors.append(f"Row {row_num}: WorkLocation '{row['work_location']}' not found.")
                continue
            if not designation_obj:
                errors.append(f"Row {row_num}: Designation '{row['designation']}' not found.")
                continue
            if not department_obj:
                errors.append(f"Row {row_num}: Department '{row['department']}' not found.")
                continue

            with transaction.atomic():
                def get_numeric_or_none(value):
                    try:
                        val = str(int(value))
                        return val if val else None
                    except (ValueError, TypeError):
                        return None

                statutory_components = {
                    "epf_enabled": bool(row.get('epf_enabled')),
                    "esi_enabled": bool(row.get('esi_enabled')),
                    "professional_tax": bool(row.get('professional_tax')),
                    "employee_provident_fund": {
                        "uan": get_numeric_or_none(row.get('uan')),
                        "pf_account_number":  get_numeric_or_none(row.get('pf_account_number'))
                    },
                    "employee_state_insurance": {
                        "esi_number": get_numeric_or_none(row.get('esi_number'))
                    }
                }

                epf = {
                    k: v for k, v in {
                        "pf_account_number": get_numeric_or_none(row.get('pf_account_number')),
                        "uan": get_numeric_or_none(row.get('uan'))
                    }.items() if v is not None
                }
                if epf:
                    statutory_components["employee_provident_fund"] = epf

                esi = {
                    k: v for k, v in {
                        "esi_number": get_numeric_or_none(row.get('esi_number'))
                    }.items() if v is not None
                }
                if esi:
                    statutory_components["employee_state_insurance"] = esi

                employee, _ = EmployeeManagement.objects.update_or_create(
                    associate_id=row['associate_id'],
                    payroll_id=payroll_obj_id,
                    defaults={
                        'first_name': row['first_name'],
                        'middle_name': None if pd.isna(row.get('middle_name')) or str(
                            row.get('middle_name')).strip().lower() == 'nan' or None else row.get('middle_name'),
                        'last_name': row['last_name'],
                        'doj': parse_excel_date(row.get('doj')),
                        'work_email': row['work_email'],
                        'mobile_number': str(row['mobile_number']),
                        'gender': row['gender'],
                        'work_location_id': work_location_obj.id,
                        'designation_id': designation_obj.id,
                        'department_id': department_obj.id,
                        'enable_portal_access': bool(row['enable_portal_access']),
                        'statutory_components': statutory_components,
                        'employee_status': bool(row.get('employee_status', True)),
                    }
                )

                EmployeePersonalDetails.objects.update_or_create(
                    employee=employee,
                    defaults={
                        'dob': parse_excel_date(row.get('dob')),
                        'age': int(row['age']),
                        'guardian_name': row['guardian_name'],
                        'pan': row.get('pan', '') or '',
                        'aadhar': row['aadhar'],
                        'address': address_json,
                        'alternate_contact_number': row.get('alternate_contact_number', '') or '',
                        'marital_status': row['marital_status'],
                        'blood_group': row['blood_group']
                    }
                )

                EmployeeBankDetails.objects.update_or_create(
                    employee=employee,
                    defaults={
                        'account_holder_name': row['account_holder_name'],
                        'bank_name': row['bank_name'],
                        'account_number': str(row['account_number']),
                        'ifsc_code': row['ifsc_code'],
                        'branch_name': row.get('branch_name', '') or '',
                        "is_active": True
                    }
                )

                success_count += 1

        except Exception as e:
            errors.append(f"Row {row_num}: Error saving record - {str(e)}")

    return Response({
        "success_count": success_count,
        "error_count": len(errors),
        "errors": errors,
    }, status=status.HTTP_200_OK if success_count > 0 else status.HTTP_400_BAD_REQUEST)
