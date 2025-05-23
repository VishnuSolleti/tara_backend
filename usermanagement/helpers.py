import os


def gst_document_upload_path(instance, filename):
    # Get the name of the business, replace spaces with underscores
    business_name = instance.business.nameOfBusiness.replace(' ', '_')
    # Construct the upload path
    return os.path.join(business_name, 'gst_documents', filename)


def license_document_upload_path(instance, filename):
    # Get the name of the business, replace spaces with underscores
    business_name = instance.business.nameOfBusiness.replace(' ', '_')
    # Construct the upload path
    return os.path.join(business_name, 'license_documents', filename)

def logo_upload_path(instance, filename):
    # Get the name of the business, replace spaces with underscores
    business_name = instance.business.nameOfBusiness.replace(' ', '_')
    # Construct the upload path
    return os.path.join(business_name, 'logo', filename)


SERVICE_TASK_MAP = {
    "labour-license": [
        "Business Identity Structure",
        "Signatory Details",
        "Business Location Proofs",
        "Business Registration Documents",
        "Review Filing Certificate"
    ],
    "msme-registration": [
        "Business Identity",
        "Business Classification Inputs",
        "Turnover And InvestmentDeclaration",
        "Registered Address",
        "Review Filing Certificate"
    ],
    "trade-license": [
        "Business Identity",
        "Applicant Details",
        "Signatory Details",
        "Business Location",
        "Trade License Details",
        "Business Document Details",
        "Review Filing Certificate"
    ]
}


due_dates = {
    "labour-license": "1 day",
    "trade-license": "1 day",
    "itr-filing": "1 day",
    "registration": "7 day",
    "msme-registration": "1 day",
    "private-limited": "15 day",
}