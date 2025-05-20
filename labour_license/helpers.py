import os


def business_identity_structure_pan(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = instance.service_request.id
    # Construct the upload path
    return os.path.join('service_requests', 'Labour License', service_request_id, 'business_identity_pan', filename)


def signatory_details_aadhar_image(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = instance.service_request.id
    # Construct the upload path
    return os.path.join('service_requests', 'Labour License', service_request_id, 'signatory_details_aadhar_image',
                        filename)


def signatory_details_pan_image(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = instance.service_request.id
    # Construct the upload path
    return os.path.join('service_requests', 'Labour License', service_request_id, 'signatory_details_pan_image',
                        filename)


def business_location_address_proof(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = instance.service_request.id
    # Construct the upload path
    return os.path.join('service_requests', 'Labour License', service_request_id, 'business_location_address_proof',
                        filename)


def business_location_rental_agreement(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = instance.service_request.id
    # Construct the upload path
    return os.path.join('service_requests',  'Labour License', service_request_id,
                        'business_location_rental_agreement', filename)


def business_location_bank_statement(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = instance.service_request.id
    # Construct the upload path
    return os.path.join('service_requests', 'Labour License', service_request_id, 'business_location_bank_statement',
                        filename)


def additional_business_space_address_proof(instance, filename):
    # Get the name of the business, replace spaces with underscores
    business_location_proof_id = instance.business_location_proofs.id
    service_request_id = instance.business_location_proofs.service_requestid
    # Construct the upload path
    return os.path.join('service_requests',  'Labour License', service_request_id, business_location_proof_id,
                        'additional_business_space_address_proof', filename)


def additional_business_space_rental_agreement(instance, filename):
    # Get the name of the business, replace spaces with underscores
    business_location_proof_id = instance.business_location_proofs.id
    service_request_id = instance.business_location_proofs.service_requestid
    # Construct the upload path
    return os.path.join('service_requests',  'Labour License', service_request_id, business_location_proof_id,
                        'additional_business_space_rental_agreement', filename)


def business_registration_documents_certificate_of_incorporation(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = instance.service_request.id
    # Construct the upload path
    return os.path.join('service_requests',  'Labour License', service_request_id,
                        'business_registration_documents_certificate_of_incorporation', filename)


def business_registration_documents_memorandum_of_articles(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = instance.service_request.id
    # Construct the upload path
    return os.path.join('service_requests',  'Labour License', service_request_id,
                        'business_registration_documents_memorandum_of_articles', filename)


def business_registration_documents_local_language_name_board_photo_business(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = instance.service_request.id
    # Construct the upload path
    return os.path.join('service_requests',  'Labour License', service_request_id,
                        'business_registration_documents_local_language_name_board_photo_business', filename)


def business_registration_documents_authorization_letter(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = instance.service_request.id
    # Construct the upload path
    return os.path.join('service_requests',  'Labour License', service_request_id,
                        'business_registration_documents_authorization_letter', filename)


def review_filing_certificate(instance, filename):
    # Get the name of the business, replace spaces with underscores
    service_request_id = instance.service_request.id
    # Construct the upload path
    return os.path.join('service_requests',  'Labour License', service_request_id,
                        'review_filing_certificate', filename)

