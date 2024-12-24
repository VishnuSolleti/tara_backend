from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import InvoicingProfile, CustomerProfile, GoodsAndServices, Invoice
from .serializers import (InvoicingProfileSerializer, CustomerProfileSerializers,
                          GoodsAndServicesSerializer, InvoicingProfileGoodsAndServicesSerializer, InvoiceSerializer,
                          InvoicingProfileSerializers)
from django.http import QueryDict
import logging
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.parsers import MultiPartParser, FormParser


# Create loggers for general and error logs
logger = logging.getLogger(__name__)

@swagger_auto_schema(
    method='get',
    operation_description="Retrieve the invoicing profile for the logged-in user.",
    tags=["Invoicing Profiles"],
    responses={
        200: openapi.Response(
            description="Invoicing profile details.",
            examples={
                "application/json": {
                    "id": 1,
                    "business": 1,
                    "pan_number": "ABCDE1234F",
                    "bank_name": "XYZ Bank",
                    "account_number": 1234567890123456,
                    "ifsc_code": "XYZ0001234",
                    "swift_code": "XYZ1234XX",
                    "invoice_format": {},
                    "signature": "signatures/abc.png"
                }
            }
        ),
        403: openapi.Response("Unauthorized access."),
        404: openapi.Response("Invoicing profile not found."),
        500: openapi.Response("An unexpected error occurred.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_invoicing_profile(request):
    """
    Retrieve the invoicing profile for the logged-in user.
    """
    try:
        user = request.user
        invoicing_profile = InvoicingProfile.objects.get(business=user)

        serializer = InvoicingProfileSerializers(invoicing_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except InvoicingProfile.DoesNotExist:
        return Response({"message": "Invoicing profile not found."}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Unexpected error in get_invoicing_profile: {e}")
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@swagger_auto_schema(
    method='post',
    operation_description="Create a new invoicing profile for the logged-in user.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "pan_number": openapi.Schema(type=openapi.TYPE_STRING, example="ABCDE1234F"),
            "bank_name": openapi.Schema(type=openapi.TYPE_STRING, example="XYZ Bank"),
            "account_number": openapi.Schema(type=openapi.TYPE_INTEGER, example=1234567890123456),
            "ifsc_code": openapi.Schema(type=openapi.TYPE_STRING, example="XYZ0001234"),
            "swift_code": openapi.Schema(type=openapi.TYPE_STRING, example="XYZ1234XX"),
            "invoice_format": openapi.Schema(type=openapi.TYPE_OBJECT, example={}),
            "signature": openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_BINARY,
                description="Upload your signature here as an image file."
            )
        }
    ),
    tags=["Invoicing Profiles"],
    responses={
        201: openapi.Response(
            description="Invoicing profile created successfully.",
            examples={
                "application/json": {
                    "id": 1,
                    "business": 1,
                    "pan_number": "ABCDE1234F",
                    "bank_name": "XYZ Bank",
                    "account_number": 1234567890123456,
                    "ifsc_code": "XYZ0001234",
                    "swift_code": "XYZ1234XX",
                    "invoice_format": {},
                    "signature": "signatures/abc.png"
                }
            }
        ),
        400: openapi.Response("Bad request."),
        403: openapi.Response("Unauthorized access."),
        500: openapi.Response("An unexpected error occurred.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        ),
    ]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_invoicing_profile(request):
    """
    Create a new invoicing profile for the logged-in user.
    """
    user = request.user
    data = request.data.copy()
    data['business'] = user.id  # Assign the current user as the business owner

    serializer = InvoicingProfileSerializer(data=data)

    if serializer.is_valid():
        try:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Unexpected error in create_invoicing_profile: {e}")
            return Response(
                {"error": f"An unexpected error occurred: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='put',
    operation_description="Update the existing invoicing profile for the logged-in user.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "pan_number": openapi.Schema(type=openapi.TYPE_STRING, example="ABCDE1234F"),
            "bank_name": openapi.Schema(type=openapi.TYPE_STRING, example="XYZ Bank"),
            "account_number": openapi.Schema(type=openapi.TYPE_INTEGER, example=1234567890123456),
            "ifsc_code": openapi.Schema(type=openapi.TYPE_STRING, example="XYZ0001234"),
            "swift_code": openapi.Schema(type=openapi.TYPE_STRING, example="XYZ1234XX"),
            "invoice_format": openapi.Schema(type=openapi.TYPE_OBJECT, example={}),
            "signature": openapi.Schema(type=openapi.TYPE_FILE, format=openapi.FORMAT_BINARY)  # Added file upload field
        },
        required=[]  # Change this to an empty list since all fields are optional
    ),
    tags=["Invoicing Profiles"],
    responses={
        200: openapi.Response(
            description="Invoicing profile updated successfully.",
            examples={
                "application/json": {
                    "id": 1,
                    "business": 1,
                    "pan_number": "ABCDE1234F",
                    "bank_name": "XYZ Bank",
                    "account_number": 1234567890123456,
                    "ifsc_code": "XYZ0001234",
                    "swift_code": "XYZ1234XX",
                    "invoice_format": {},
                    "signature": "signatures/abc.png"
                }
            }
        ),
        400: openapi.Response("Bad request."),
        403: openapi.Response("Unauthorized access."),
        404: openapi.Response("Invoicing profile not found."),
        500: openapi.Response("An unexpected error occurred.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        ),
    ]
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_invoicing_profile(request, pk):
    """
    Update the existing invoicing profile for the logged-in user.
    """
    try:
        invoicing_profile = InvoicingProfile.objects.get(business=request.user)
    except InvoicingProfile.DoesNotExist:
        return Response({"message": "Invoicing profile not found."}, status=status.HTTP_404_NOT_FOUND)

    # Parse file uploads
    parser_classes = (MultiPartParser, FormParser)

    # Convert request.data to a mutable dictionary
    data = request.data.dict() if isinstance(request.data, QueryDict) else request.data

    if 'signature' in request.FILES:
        data['signature'] = request.FILES['signature']

    serializer = InvoicingProfileSerializer(invoicing_profile, data=data, partial=True)

    if serializer.is_valid():
        try:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Unexpected error in update_invoicing_profile: {e}")
            return Response(
                {"error": f"An unexpected error occurred: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='delete',
    operation_description="Delete the invoicing profile for the logged-in user.",
    tags=["Invoicing Profiles"],
    responses={
        204: openapi.Response("Invoicing profile deleted successfully."),
        403: openapi.Response("Unauthorized access."),
        404: openapi.Response("Invoicing profile not found."),
        500: openapi.Response("An unexpected error occurred.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        ),
    ]
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_invoicing_profile(request):
    """
    Delete the invoicing profile for the logged-in user.
    """
    try:
        invoicing_profile = InvoicingProfile.objects.get(business=request.user)
        invoicing_profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    except InvoicingProfile.DoesNotExist:
        return Response({"message": "Invoicing profile not found."}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Unexpected error in delete_invoicing_profile: {e}")
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method='post',
    operation_description="Create a new customer profile for the logged-in user.",
    tags=["Customer Profiles"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'invoicing_profile': openapi.Schema(type=openapi.TYPE_INTEGER, description="Invoicing profile ID"),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description="Customer name"),
            'pan_number': openapi.Schema(type=openapi.TYPE_STRING, description="PAN number"),
            'country': openapi.Schema(type=openapi.TYPE_STRING, description="Country"),
            'address_line1': openapi.Schema(type=openapi.TYPE_STRING, description="Address line 1"),
            'address_line2': openapi.Schema(type=openapi.TYPE_STRING, description="Address line 2"),
            'state': openapi.Schema(type=openapi.TYPE_STRING, description="State"),
            'postal_code': openapi.Schema(type=openapi.TYPE_STRING, description="Postal code"),
            'gst_registered': openapi.Schema(type=openapi.TYPE_STRING, description="GST registered status"),
            'gstin': openapi.Schema(type=openapi.TYPE_STRING, description="GSTIN"),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description="Email address"),
            'mobile_number': openapi.Schema(type=openapi.TYPE_STRING, description="Mobile number"),
            "opening_balance": openapi.Schema(type=openapi.TYPE_STRING, description="Opening Balance"),
            "gst_type": openapi.Schema(type=openapi.TYPE_STRING, description="Gst Type")
        }
    ),
    responses={
        201: openapi.Response(
            description="Customer profile created successfully.",
            examples={
                "application/json": {
                    "id": 1,
                    "invoicing_profile": 1,
                    "name": "John Doe",
                    "pan_number": "ABCDE1234F",
                    "country": "USA",
                    "address_line1": "123 Main St",
                    "address_line2": "XYZ Buddy",
                    "state": "California",
                    "postal_code": "12345",
                    "gst_registered": "Yes",
                    "gstin": "GSTIN12345",
                    "email": "johndoe@example.com",
                    "mobile_number": "1234567890",
                    "opening_balance": 97000,
                    "gst_type": "Anything"
                }
            }
        ),
        403: openapi.Response("Unauthorized access."),
        500: openapi.Response("An unexpected error occurred.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_customer_profile(request):
    """
    Create a new customer profile for the logged-in user.
    """
    serializer = CustomerProfileSerializers(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@swagger_auto_schema(
    method='get',
    operation_description="Retrieve the customer profile of the logged-in user.",
    tags=["Customer Profiles"],
    responses={
        200: openapi.Response(
            description="Customer profile details.",
            examples={
                "application/json": {
                    "id": 1,
                    "invoicing_profile": 1,
                    "name": "John Doe",
                    "pan_number": "ABCDE1234F",
                    "country": "USA",
                    "address_line1": "123 Main St",
                    "state": "California",
                    "postal_code": "12345",
                    "gst_registered": "Yes",
                    "gstin": "GSTIN12345",
                    "email": "johndoe@example.com",
                    "mobile_number": "1234567890"
                }
            }
        ),
        403: openapi.Response("Unauthorized access."),
        404: openapi.Response("Customer profile not found."),
        500: openapi.Response("An unexpected error occurred.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_customer_profile(request):
    """
    Retrieve all invoicing profiles along with their associated customer profiles for the logged-in user.
    """
    try:
        # Get all invoicing profiles associated with the user's business
        invoicing_profiles = InvoicingProfile.objects.filter(business=request.user)

        if not invoicing_profiles.exists():
            logger.warning(f"User {request.user.id} tried to access invoicing profiles, but none exist.")
            return Response({"message": "No invoicing profiles found."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the data
        serializer = InvoicingProfileSerializers(invoicing_profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Unexpected error in get_customer_profiles: {e}")
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method='put',
    operation_description="Update the customer profile for the logged-in user.",
    tags=["Customer Profiles"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'invoicing_profile': openapi.Schema(type=openapi.TYPE_INTEGER, description="Invoicing profile ID"),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description="Customer name"),
            'pan_number': openapi.Schema(type=openapi.TYPE_STRING, description="PAN number"),
            'country': openapi.Schema(type=openapi.TYPE_STRING, description="Country"),
            'address_line1': openapi.Schema(type=openapi.TYPE_STRING, description="Address line 1"),
            'state': openapi.Schema(type=openapi.TYPE_STRING, description="State"),
            'postal_code': openapi.Schema(type=openapi.TYPE_STRING, description="Postal code"),
            'gst_registered': openapi.Schema(type=openapi.TYPE_STRING, description="GST registered status"),
            'gstin': openapi.Schema(type=openapi.TYPE_STRING, description="GSTIN"),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description="Email address"),
            'mobile_number': openapi.Schema(type=openapi.TYPE_STRING, description="Mobile number"),
        }
    ),
    responses={
        200: openapi.Response(
            description="Customer profile updated successfully.",
            examples={
                "application/json": {
                    "id": 1,
                    "invoicing_profile": 1,
                    "name": "John Doe Updated",
                    "pan_number": "ABCDE1234F",
                    "country": "USA",
                    "address_line1": "123 Main St",
                    "state": "California",
                    "postal_code": "12345",
                    "gst_registered": "Yes",
                    "gstin": "GSTIN12345",
                    "email": "johndoe@example.com",
                    "mobile_number": "1234567890"
                }
            }
        ),
        403: openapi.Response("Unauthorized access."),
        404: openapi.Response("Customer profile not found."),
        500: openapi.Response("An unexpected error occurred.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_customer_profile(request, id):
    """
    Update the customer profile for the given ID.
    """
    try:
        # Retrieve the customer profile by ID
        customer_profile = CustomerProfile.objects.get(id=id)
        serializer = CustomerProfileSerializers(customer_profile, data=request.data, partial=True)

        # Validate and save the updated data
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except CustomerProfile.DoesNotExist:
        logger.warning(f"Customer profile with ID {id} does not exist.")
        return Response({"message": "Customer profile not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Unexpected error in update_customer_profile: {e}")
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )



@swagger_auto_schema(
    method='delete',
    operation_description="Delete the customer profile of the logged-in user.",
    tags=["Customer Profiles"],
    responses={
        204: openapi.Response(
            description="Customer profile deleted successfully."
        ),
        403: openapi.Response("Unauthorized access."),
        404: openapi.Response("Customer profile not found."),
        500: openapi.Response("An unexpected error occurred.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_customer_profile(request):
    """
    Delete the customer profile of the logged-in user.
    """
    try:
        customer_profile = CustomerProfile.objects.get(invoicing_profile__business=request.user)
        customer_profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except ObjectDoesNotExist:
        logger.warning(f"User {request.user.id} tried to delete a non-existent customer profile.")
        return Response({"message": "Customer profile not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Unexpected error in delete_customer_profile: {e}")
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method='post',
    operation_description="Create a new goods and services entry for the logged-in user.",
    tags=["Goods and Services"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'invoicing_profile': openapi.Schema(type=openapi.TYPE_INTEGER, description="Invoicing profile ID"),
            'type': openapi.Schema(type=openapi.TYPE_STRING, description="Type of goods or services"),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the goods or services"),
            'units': openapi.Schema(type=openapi.TYPE_STRING, description="Units of the goods or services"),
            'hsn_sac': openapi.Schema(type=openapi.TYPE_STRING, description="HSN/SAC code"),
            'gst_rate': openapi.Schema(type=openapi.TYPE_STRING, description="GST rate"),
            'unit_price': openapi.Schema(type=openapi.TYPE_NUMBER, description="Price per unit"),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description="Description of the goods or services"),
        }
    ),
    responses={
        201: openapi.Response(
            description="Goods and services entry created successfully.",
            examples={
                "application/json": {
                    "id": 1,
                    "invoicing_profile": 1,
                    "type": "Service",
                    "name": "Consulting",
                    "units": "Hours",
                    "hsn_sac": "1234",
                    "gst_rate": "18",
                    "unit_price": 100.0,
                    "description": "Consulting services for software development"
                }
            }
        ),
        403: openapi.Response("Unauthorized access."),
        500: openapi.Response("An unexpected error occurred.")
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_goods_and_services(request):
    """
    Create a new goods and services entry for the logged-in user.
    """
    serializer = GoodsAndServicesSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    operation_description="Retrieve goods and services entries for the logged-in user.",
    tags=["Goods and Services"],
    responses={
        200: openapi.Response(
            description="Goods and services entry details.",
            examples={
                "application/json": [
                    {
                        "id": 1,
                        "invoicing_profile": 1,
                        "type": "Service",
                        "name": "Consulting",
                        "units": "Hours",
                        "hsn_sac": "1234",
                        "gst_rate": "18",
                        "unit_price": 100.0,
                        "description": "Consulting services for software development"
                    },
                    {
                        "id": 2,
                        "invoicing_profile": 1,
                        "type": "Product",
                        "name": "Laptop",
                        "units": "Piece",
                        "hsn_sac": "5678",
                        "gst_rate": "28",
                        "unit_price": 1000.0,
                        "description": "High-performance laptop"
                    }
                ]
            }
        ),
        403: openapi.Response("Unauthorized access."),
        500: openapi.Response("An unexpected error occurred.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_goods_and_services(request):
    """
    Retrieve goods and services entries for the logged-in user.
    """
    try:
        goods_and_services_entries = GoodsAndServices.objects.filter(invoicing_profile__business=request.user)
        serializer = GoodsAndServicesSerializer(goods_and_services_entries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Unexpected error in get_goods_and_services: {e}")
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method='put',
    operation_description="Update a goods and services entry for the logged-in user.",
    tags=["Goods and Services"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'invoicing_profile': openapi.Schema(type=openapi.TYPE_INTEGER, description="Invoicing profile ID"),
            'type': openapi.Schema(type=openapi.TYPE_STRING, description="Type of goods or services"),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the goods or services"),
            'units': openapi.Schema(type=openapi.TYPE_STRING, description="Units of the goods or services"),
            'hsn_sac': openapi.Schema(type=openapi.TYPE_STRING, description="HSN/SAC code"),
            'gst_rate': openapi.Schema(type=openapi.TYPE_STRING, description="GST rate"),
            'unit_price': openapi.Schema(type=openapi.TYPE_NUMBER, description="Price per unit"),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description="Description of the goods or services"),
        }
    ),
    responses={
        200: openapi.Response(
            description="Goods and services entry updated successfully.",
            examples={
                "application/json": {
                    "id": 1,
                    "invoicing_profile": 1,
                    "type": "Service",
                    "name": "Consulting Updated",
                    "units": "Hours",
                    "hsn_sac": "1234",
                    "gst_rate": "18",
                    "unit_price": 110.0,
                    "description": "Updated consulting services for software development"
                }
            }
        ),
        403: openapi.Response("Unauthorized access."),
        404: openapi.Response("Goods and services entry not found."),
        500: openapi.Response("An unexpected error occurred.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_goods_and_services(request, pk):
    """
    Update a goods and services entry for the logged-in user.
    """
    try:
        goods_and_services_entry = GoodsAndServices.objects.get(pk=pk, invoicing_profile__business=request.user)
        serializer = GoodsAndServicesSerializer(goods_and_services_entry, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except GoodsAndServices.DoesNotExist:
        logger.warning(f"User {request.user.id} tried to update a non-existent goods and services entry.")
        return Response({"message": "Goods and services entry not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Unexpected error in update_goods_and_services: {e}")
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method='delete',
    operation_description="Delete a goods and services entry for the logged-in user.",
    tags=["Goods and Services"],
    responses={
        204: openapi.Response(
            description="Goods and services entry deleted successfully."
        ),
        403: openapi.Response("Unauthorized access."),
        404: openapi.Response("Goods and services entry not found."),
        500: openapi.Response("An unexpected error occurred.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_goods_and_services(request, pk):
    """
    Delete a goods and services entry for the logged-in user.
    """
    try:
        goods_and_services_entry = GoodsAndServices.objects.get(pk=pk, invoicing_profile__business=request.user)
        goods_and_services_entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except GoodsAndServices.DoesNotExist:
        logger.warning(f"User {request.user.id} tried to delete a non-existent goods and services entry.")
        return Response({"message": "Goods and services entry not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Unexpected error in delete_goods_and_services: {e}")
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method='post',
    operation_description="Create a new goods or service entry.",
    tags=["Goods and Services"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'invoicing_profile': openapi.Schema(type=openapi.TYPE_INTEGER, description="Invoicing profile ID"),
            'type': openapi.Schema(type=openapi.TYPE_STRING, description="Type of goods or service"),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the goods or service"),
            'sku_value': openapi.Schema(type=openapi.TYPE_NUMBER, description="SKU value"),
            'units': openapi.Schema(type=openapi.TYPE_STRING, description="Units of measurement"),
            'hsn_sac': openapi.Schema(type=openapi.TYPE_STRING, description="HSN/SAC code"),
            'gst_rate': openapi.Schema(type=openapi.TYPE_STRING, description="GST rate"),
            'tax_preference': openapi.Schema(type=openapi.TYPE_INTEGER, description="Tax preference"),
            'selling_price': openapi.Schema(type=openapi.TYPE_INTEGER, description="Selling price"),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description="Description"),
        }
    ),
    responses={
        201: openapi.Response(
            description="Goods or service created successfully.",
            examples={
                "application/json": {
                    "id": 1,
                    "invoicing_profile": 1,
                    "type": "Product",
                    "name": "Laptop",
                    "sku_value": 12345.67,
                    "units": "piece",
                    "hsn_sac": "8471",
                    "gst_rate": "18",
                    "tax_preference": 1,
                    "selling_price": 50000,
                    "description": "High-end gaming laptop"
                }
            }
        ),
        400: openapi.Response("Bad Request."),
        500: openapi.Response("An unexpected error occurred.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_goods_service(request):
    """
    Create a new goods or service entry.
    """
    serializer = GoodsAndServicesSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    operation_description="Retrieve a goods or service entry by ID.",
    tags=["Goods and Services"],
    responses={
        200: openapi.Response(
            description="Successfully retrieved goods or service.",
            examples={
                "application/json": {
                    "id": 1,
                    "invoicing_profile": 1,
                    "type": "Product",
                    "name": "Laptop",
                    "sku_value": 12345.67,
                    "units": "piece",
                    "hsn_sac": "8471",
                    "gst_rate": "18",
                    "tax_preference": 1,
                    "selling_price": 50000,
                    "description": "High-end gaming laptop"
                }
            }
        ),
        404: openapi.Response("Goods or service not found."),
        500: openapi.Response("An unexpected error occurred.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def retrieve_goods_service(request):
    """
    Retrieve a goods or service entry by ID.
    """
    try:
        # Get all invoicing profiles associated with the user's business
        invoicing_profiles = InvoicingProfile.objects.filter(business=request.user)

        if not invoicing_profiles.exists():
            logger.warning(f"User {request.user.id} tried to access invoicing profiles, but none exist.")
            return Response({"message": "No invoicing profiles found."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the data
        serializer = InvoicingProfileGoodsAndServicesSerializer(invoicing_profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Unexpected error in get_customer_profiles: {e}")
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method='put',
    operation_description="Update an existing goods or service entry by ID.",
    tags=["Goods and Services"],
    request_body=GoodsAndServicesSerializer,
    responses={
        200: openapi.Response("Successfully updated the goods or service."),
        400: openapi.Response("Bad Request."),
        404: openapi.Response("Goods or service not found."),
        500: openapi.Response("An unexpected error occurred.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_goods_service(request, id):
    """
    Update an existing goods or service entry by ID.
    """
    try:
        goods_service = GoodsAndServices.objects.get(id=id)
        serializer = GoodsAndServicesSerializer(goods_service, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except GoodsAndServices.DoesNotExist:
        return Response({"message": "Goods or service not found."}, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(
    method='delete',
    operation_description="Delete a goods or service entry by ID.",
    tags=["Goods and Services"],
    responses={
        204: openapi.Response("Successfully deleted the goods or service."),
        404: openapi.Response("Goods or service not found."),
        500: openapi.Response("An unexpected error occurred.")
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_goods_service(request, id):
    """
    Delete a goods or service entry by ID.
    """
    try:
        goods_service = GoodsAndServices.objects.get(id=id)
        goods_service.delete()
        return Response({"message": "Goods or service deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except GoodsAndServices.DoesNotExist:
        return Response({"message": "Goods or service not found."}, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(
    method='post',
    operation_description="Create a new invoice.",
    tags=["Invoices"],
    request_body=InvoiceSerializer,
    responses={
        201: openapi.Response("Invoice created successfully."),
        400: openapi.Response("Bad request."),
        500: openapi.Response("An unexpected error occurred."),
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_invoice(request):
    """
    Create a new invoice.
    """
    try:
        serializer = InvoiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.warning(f"Validation error: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Unexpected error in create_invoice: {e}")
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method='get',
    operation_description="Retrieve all invoices.",
    tags=["Invoices"],
    responses={
        200: openapi.Response(
            description="List of invoices.",
            examples={
                "application/json": [
                    {
                        "id": 1,
                        "invoicing_profile": 1,
                        "customer": "John Doe",
                        "terms": "Net 30",
                        "financial_year": "2023-24",
                        "invoice_number": "INV-0001",
                        "invoice_date": "2024-12-18T00:00:00Z",
                        "place_of_supply": "California",
                        "billing_address": {"line1": "123 Main St", "city": "Los Angeles"},
                        "shipping_address": {"line1": "456 Oak Ave", "city": "San Francisco"},
                        "item_details": [
                            {"name": "Product A", "price": 100, "quantity": 2},
                            {"name": "Service B", "price": 200, "quantity": 1}
                        ],
                        "total_amount": 400,
                        "subtotal_amount": 350,
                        "shipping_amount": 50,
                        "cgst_amount": 18,
                        "sgst_amount": 18,
                        "igst_amount": 0,
                        "pending_amount": 200,
                        "amount_invoiced": 400,
                        "payment_status": "Partial",
                        "is_same_as_billing": True,
                        "notes": "Thank you for your business.",
                        "terms_and_conditions": "No returns after 30 days."
                    }
                ]
            }
        ),
        404: openapi.Response("No invoices found."),
        500: openapi.Response("An unexpected error occurred."),
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def retrieve_invoices(request):
    """
    Retrieve all invoices.
    """
    try:
        invoices = Invoice.objects.all()
        if not invoices.exists():
            logger.warning("No invoices found.")
            return Response({"message": "No invoices found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Unexpected error in retrieve_invoices: {e}")
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method='put',
    operation_description="Update an existing invoice by ID.",
    tags=["Invoices"],
    request_body=InvoiceSerializer,
    responses={
        200: openapi.Response("Invoice updated successfully."),
        404: openapi.Response("Invoice not found."),
        400: openapi.Response("Validation error."),
        500: openapi.Response("An unexpected error occurred."),
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_invoice(request, invoice_id):
    """
    Update an existing invoice by ID.
    """
    try:
        invoice = Invoice.objects.filter(id=invoice_id).first()

        if not invoice:
            logger.warning(f"Invoice with ID {invoice_id} not found.")
            return Response({"message": "Invoice not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = InvoiceSerializer(invoice, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        logger.warning(f"Validation error while updating invoice: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Unexpected error in update_invoice: {e}")
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@swagger_auto_schema(
    method='delete',
    operation_description="Delete an existing invoice by ID.",
    tags=["Invoices"],
    responses={
        204: openapi.Response("Invoice deleted successfully."),
        404: openapi.Response("Invoice not found."),
        500: openapi.Response("An unexpected error occurred."),
    },
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <JWT Token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ]
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_invoice(request, invoice_id):
    """
    Delete an existing invoice by ID. To be tested
    """
    try:
        invoice = Invoice.objects.filter(id=invoice_id).first()

        if not invoice:
            logger.warning(f"Invoice with ID {invoice_id} not found.")
            return Response({"message": "Invoice not found."}, status=status.HTTP_404_NOT_FOUND)

        invoice.delete()
        return Response({"message": "Invoice deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        logger.error(f"Unexpected error in delete_invoice: {e}")
        return Response(
            {"error": f"An unexpected error occurred: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
