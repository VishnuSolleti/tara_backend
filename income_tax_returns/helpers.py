import os
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework import status
from usermanagement.models import Context, ServiceRequest  # Update this import as per your project


def personal_information_pan(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request_id)
    # Construct the upload path
    return os.path.join('service_requests', 'itr', service_request_id, 'personal_information_pan', filename)


def personal_information_aadhar(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request_id)
    # Construct the upload path
    return os.path.join('service_requests', 'itr', service_request_id, 'personal_information_aadhar', filename)


def tax_paid_details_file(instance, filename):
    # instance is of TaxPaidDetailsFile
    service_request_id = str(instance.tax_paid.service_request.id)
    document_type = instance.document_type or "unknown_type"

    # Construct an upload path
    return os.path.join(
        'service_requests', 'itr', service_request_id, 'tax_paid_details_file', document_type, filename
    )


def salary_income_details_file(instance, filename):
    # instance is of TaxPaidDetailsFile
    service_request_id = str(instance.income.service_request.id)
    document_type = instance.document_type or "unknown_type"

    # Construct an upload path
    return os.path.join(
        'service_requests', 'itr', service_request_id, 'salary_income_details_file', document_type, filename
    )


def outcome_income_details_file(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request_id)
    # Construct the upload path
    return os.path.join('service_requests', 'itr', service_request_id, 'outcome_income_details_file', filename)


def foreign_emp_salary_details_file(instance, filename):
    # instance is of ForeignEmpSalaryDetailsFile
    service_request_id = str(instance.foreign_emp_salary_details.service_request.id)
    document_type = instance.document_type or "unknown_type"

    # Construct an upload path
    return os.path.join(
        'service_requests', 'itr', service_request_id, 'foreign_emp_salary_details_file', document_type, filename
    )


def house_property_details_municipal_tax_receipt(instance, filename):
    # instance is of HousePropertyDetailsMunicipalTaxReceipt
    service_request_id = str(instance.service_request_id)

    # Construct an upload path
    return os.path.join(
        'service_requests', 'itr', service_request_id, 'house_property_details_municipal_tax_receipt', filename)


def house_property_details_loan_statement(instance, filename):
    # instance is of HousePropertyDetailsOwnershipDocument
    service_request_id = str(instance.service_request_id)

    # Construct an upload path
    return os.path.join(
        'service_requests', 'itr', service_request_id, 'house_property_details_loan_statement', filename)


def house_property_details_loan_interest_certificate(instance, filename):
    # instance is of HousePropertyDetailsOwnershipDocument
    service_request_id = str(instance.service_request_id)

    # Construct an upload path
    return os.path.join(
        'service_requests', 'itr', service_request_id, 'house_property_details_loan_interest_certificate', filename)


def interest_income_details_file(instance, filename):
    # instance is of InterestIncomeDetailsFile
    service_request_id = str(instance.interest_income.service_request.id)
    interest_type = instance.interest_type or "unknown_type"

    # Construct an upload path
    return os.path.join(
        'service_requests', 'itr', service_request_id, 'interest_income_details_file', interest_type, filename
    )


def dividend_income_file(instance, filename):
    # instance is of DividendIncomeFile
    service_request_id = str(instance.dividend_income.service_request_id)

    # Construct an upload path
    return os.path.join(
        'service_requests', 'itr', service_request_id, 'dividend_income_file', filename
    )


def review_filing_certificate(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request_id)
    # Construct the upload path
    return os.path.join('service_requests', 'itr', service_request_id, 'review_filing_certificate', filename)


def section_80g_file(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request_id)
    # Construct the upload path
    return os.path.join('service_requests', 'deductions', service_request_id, 'section_80g_file', filename)


def section_80ettattbu_file(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request_id)
    # Construct the upload path
    return os.path.join('service_requests', 'deductions', service_request_id, 'section_80ettattbu_file', filename)


def section_80d_file(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = str(instance.service_request_id)
    # Construct the upload path
    return os.path.join('service_requests', 'deductions', service_request_id, 'section_80d_file', filename)


