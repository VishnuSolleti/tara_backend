import os

# --- File Upload Paths ---

def upload_address_proof_file(instance, filename):
    return os.path.join('company_incorporation', 'address_proof', str(instance.service_request.id), filename)

def upload_utility_bill_file(instance, filename):
    return os.path.join('company_incorporation', 'utility_bill', str(instance.service_request.id), filename)

def upload_noc_file(instance, filename):
    return os.path.join('company_incorporation', 'noc', str(instance.service_request.id), filename)

def upload_rent_agreement_file(instance, filename):
    return os.path.join('company_incorporation', 'rent_agreement', str(instance.service_request.id), filename)

def upload_property_tax_receipt_file(instance, filename):
    return os.path.join('company_incorporation', 'property_tax_receipt', str(instance.service_request.id), filename)

def upload_pan_card_file(instance, filename):
    return os.path.join('company_incorporation', 'pan_card', str(instance.directors_ref.service_request.id), filename)

def upload_aadhaar_card_file(instance, filename):
    return os.path.join('company_incorporation', 'aadhaar_card',
                        str(instance.directors_ref.service_request.id), filename)

def upload_passport_photo_file(instance, filename):
    return os.path.join('company_incorporation', 'passport_photo',
                        str(instance.directors_ref.service_request.id), filename)

def upload_residential_address_proof_file(instance, filename):
    return os.path.join('company_incorporation', 'residential_address_proof',
                        str(instance.directors_ref.service_request.id), filename)

def upload_form_dir2(instance, filename):
    return os.path.join('company_incorporation', 'form_dir2', str(instance.directors_ref.service_request.id), filename)

def upload_specimen_signature_of_director(instance, filename):
    return os.path.join('company_incorporation', 'specimen_signature',
                        str(instance.directors_ref.service_request.id), filename)

def upload_bank_statement_file(instance, filename):
    return os.path.join('company_incorporation', 'bank_statement',
                        str(instance.shareholders_ref.service_request.id), filename)

# --- Final Review Document Path ---

def review_filing_certificate(instance, filename):
    service_request_id = str(instance.service_request.id)
    return os.path.join('service_requests', 'company_incorporation', service_request_id,
                        'review_filing_certificate', filename)
