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

    # Construct upload path
    return os.path.join(
        'service_requests', 'itr', service_request_id, 'tax_paid_details_file', document_type, filename
    )


def salary_income_details_file(instance, filename):
    # instance is of TaxPaidDetailsFile
    service_request_id = str(instance.income.service_request.id)
    document_type = instance.document_type or "unknown_type"

    # Construct upload path
    return os.path.join(
        'service_requests', 'itr', service_request_id, 'salary_income_details_file', document_type, filename
    )