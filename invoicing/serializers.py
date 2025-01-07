from rest_framework import serializers
from .models import *
from django.core.files.storage import FileSystemStorage

class CustomerProfileSerializers(serializers.Serializer):
    invoicing_profile = serializers.PrimaryKeyRelatedField(
        queryset=InvoicingProfile.objects.all()
    )
    name = serializers.CharField(max_length=100, allow_null=True, allow_blank=True)
    pan_number = serializers.CharField(max_length=10, allow_null=True, allow_blank=True)
    country = serializers.CharField(max_length=10, allow_null=True, allow_blank=True)
    address_line1 = serializers.CharField(max_length=200, allow_null=True, allow_blank=True)
    address_line2 = serializers.CharField(max_length=200, allow_null=True, allow_blank=True)
    state = serializers.CharField(max_length=30, allow_null=True, allow_blank=True)
    postal_code = serializers.CharField(max_length=10, allow_null=True, allow_blank=True)
    gst_registered = serializers.CharField(max_length=100, allow_null=True, allow_blank=True)
    gstin = serializers.CharField(max_length=100, allow_null=True, allow_blank=True)
    gst_type = serializers.CharField(max_length=60, allow_null=True, allow_blank=True)
    email = serializers.CharField(max_length=100, allow_null=True, allow_blank=True)
    mobile_number = serializers.CharField(max_length=15, allow_null=True, allow_blank=True)
    opening_balance = serializers.IntegerField(allow_null=True)

    def create(self, validated_data):
        """
        Create and return a new `InvoicingProfile` instance, given the validated data.
        """
        instance = self.Meta.model(**validated_data)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        """
        Update and return an existing `InvoicingProfile` instance, given the validated data.
        """
        [setattr(instance, k, v) for k, v in validated_data.items()]
        instance.save()
        return instance

    class Meta:
        model = CustomerProfile
        fields = '__all__'

class GoodsAndServicesSerializer(serializers.Serializer):
    invoicing_profile = serializers.PrimaryKeyRelatedField(
        queryset=InvoicingProfile.objects.all()
    )
    type = serializers.CharField(max_length=20, allow_null=True, allow_blank=True)
    name = serializers.CharField(max_length=50, allow_null=True, allow_blank=True)
    sku_value = serializers.IntegerField(allow_null=True)
    units = serializers.CharField(max_length=100, allow_null=True, allow_blank=True)
    # categoryasGST = serializers.CharField(max_length=200, allow_null=True, allow_blank=True)
    hsn_sac = serializers.CharField(max_length=200, allow_null=True, allow_blank=True)
    gst_rate = serializers.CharField(max_length=200, allow_null=True, allow_blank=True)
    tax_preference = serializers.CharField(max_length=60, allow_null=True, allow_blank=True)
    selling_price = serializers.IntegerField(allow_null=True)
    description = serializers.CharField(max_length=200, allow_null=True, allow_blank=True)

    class Meta:
        model = GoodsAndServices
        fields = [
            'id',
            'invoicing_profile',
            'type',
            'name',
            'units',
            'hsn_sac',
            'gst_rate',
            'unit_price',
            'description'
        ]

    def create(self, validated_data):
        """
        Create and return a new `InvoicingProfile` instance, given the validated data.
        """
        instance = self.Meta.model(**validated_data)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        """
        Update and return an existing `InvoicingProfile` instance, given the validated data.
        """
        [setattr(instance, k, v) for k, v in validated_data.items()]
        instance.save()
        return instance

    def validate_unit_price(self, value):
        """
        Check that the unit price is a positive number.
        """
        if value <= 0:
            raise serializers.ValidationError("Unit price must be greater than zero.")
        return value

    def validate_hsn_sac(self, value):
        """
        Ensure that HSN/SAC is exactly 4 digits.
        """
        if len(value) != 4:
            raise serializers.ValidationError("HSN/SAC must be exactly 4 digits.")
        return value

    def validate_gst_rate(self, value):
        """
        Ensure that GST rate is a valid percentage between 0 and 100.
        """
        if not (0 <= float(value) <= 100):
            raise serializers.ValidationError("GST rate must be between 0 and 100.")
        return value

class AddressSerializer(serializers.Serializer):
    address = serializers.CharField(max_length=200, allow_null=True, allow_blank=True)
    state = serializers.CharField(max_length=200, allow_null=True, allow_blank=True)
    country = serializers.CharField(max_length=200, allow_null=True, allow_blank=True)
    pincode = serializers.IntegerField()

class DetailedItemSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200, allow_null=True, allow_blank=True)
    quantity = serializers.CharField(max_length=200, allow_null=True, allow_blank=True)
    unitPrice = serializers.CharField(max_length=200, allow_null=True, allow_blank=True)
    hsn_sac = serializers.CharField(max_length=200, allow_null=True, allow_blank=True)
    discount = serializers.CharField(max_length=200, allow_null=True, allow_blank=True)
    amount = serializers.CharField(max_length=200, allow_null=True, allow_blank=True)
    cgst = serializers.CharField(max_length=200, allow_null=True, allow_blank=True)
    sgst = serializers.CharField(max_length=200, allow_null=True, allow_blank=True)
    igst = serializers.CharField(max_length=200, allow_null=True, allow_blank=True)


class PendingDataSerializer(serializers.Serializer):
    date = serializers.CharField(max_length=200, allow_null=True, allow_blank=True)
    paid_amount = serializers.FloatField(allow_null=True)


class PaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentDetail
        fields = ['date', 'paid_amount']


class InvoiceSerializer(serializers.Serializer):
    invoicing_profile = serializers.PrimaryKeyRelatedField(
        queryset=InvoicingProfile.objects.all()
    )
    customer = serializers.CharField(max_length=500, allow_null=True, allow_blank=True)
    terms = serializers.CharField(max_length=500, allow_null=True, allow_blank=True)
    financial_year = serializers.CharField(max_length=50, allow_null=True, allow_blank=True)
    invoice_number = serializers.CharField(max_length=50, allow_null=True, allow_blank=True)
    format_version = serializers.IntegerField(allow_null=False)
    invoice_date = serializers.DateField(allow_null=True)
    due_date = serializers.DateField(allow_null=False)
    month = serializers.IntegerField(allow_null=False)
    sales_person = serializers.CharField(max_length=60, allow_null=True, allow_blank=True)
    order_number = serializers.CharField(max_length=60, allow_null=True, allow_blank=True)
    place_of_supply = serializers.CharField(max_length=500, allow_null=True, allow_blank=True)
    billing_address = serializers.JSONField(required=False, default={})
    shipping_address = serializers.JSONField(required=False, default={})
    item_details = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=[],
    )
    total_amount = serializers.FloatField(allow_null=True)
    subtotal_amount = serializers.FloatField(allow_null=True)
    shipping_amount = serializers.FloatField(allow_null=True)
    total_cgst_amount = serializers.FloatField(allow_null=True)
    total_sgst_amount = serializers.FloatField(allow_null=True)
    total_igst_amount = serializers.FloatField(allow_null=True)
    pending_amount = serializers.FloatField(allow_null=True)
    amount_invoiced = serializers.FloatField(allow_null=True)
    payment_status = serializers.CharField(max_length=50, allow_null=True, allow_blank=True, default='Pending')
    notes = serializers.CharField(max_length=500, allow_null=True, allow_blank=True)
    terms_and_conditions = serializers.CharField(max_length=500, allow_null=True, allow_blank=True)
    applied_tax = serializers.BooleanField(default=False)
    shipping_tax = serializers.FloatField(allow_null=True)
    shipping_amount_with_tax = serializers.FloatField(allow_null=True)
    selected_gst_rate = serializers.FloatField(allow_null=True)

    def create(self, validated_data):
        """
        Create and return a new `InvoicingProfile` instance, given the validated data.
        """
        instance = self.Meta.model(**validated_data)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        """
        Update and return an existing `InvoicingProfile` instance, given the validated data.
        """
        [setattr(instance, k, v) for k, v in validated_data.items()]
        instance.save()
        return instance

    class Meta:
        model = Invoice
        fields = '__all__'


class SignatureStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(location='/home/signature', base_url='/media/signature/', *args, **kwargs)

class InvoicingProfileSerializer(serializers.ModelSerializer):
    invoice_format = serializers.JSONField(required=False)
    signature = models.ImageField(storage=SignatureStorage(), upload_to='signature/', blank=True, null=True)

    def create(self, validated_data):
        """
        Create and return a new `InvoicingProfile` instance, given the validated data.
        """
        instance = self.Meta.model(**validated_data)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        """
        Update and return an existing `InvoicingProfile` instance, given the validated data.
        """
        [setattr(instance, k, v) for k, v in validated_data.items()]
        instance.save()
        return instance

    class Meta:
        model = InvoicingProfile
        fields = '__all__'

class CustomerProfileGetSerializers(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        exclude = ['invoicing_profile']

class InvoicingProfileSerializers(serializers.ModelSerializer):
    customer_profiles = CustomerProfileGetSerializers(many=True, source='customerprofile_set')
    invoice_format = serializers.JSONField()
    class Meta:
        model = InvoicingProfile
        fields = [
            'id',
            'business',
            'pan_number',
            'bank_name',
            'account_number',
            'ifsc_code',
            'swift_code',
            'customer_profiles',  # Nested customer profiles included
            'invoice_format'
        ]
class InvoicingProfileCustomersSerializer(serializers.ModelSerializer):
    customer_profiles = CustomerProfileGetSerializers(many=True, source='customerprofile_set')

    class Meta:
        model = InvoicingProfile
        fields = [
            'id',
            'business',
            'customer_profiles',  # Nested customer profiles included
        ]


class GoodsAndServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsAndServices
        exclude = ['invoicing_profile']  # Exclude the 'invoicing_profile' field


class InvoicingProfileGoodsAndServicesSerializer(serializers.ModelSerializer):
    goods_and_services = GoodsAndServiceSerializer(many=True)

    class Meta:
        model = InvoicingProfile
        fields = [
            'id',
            'business',
            'goods_and_services',  # Nested goods and services
        ]


class InvoicesSerializer(serializers.ModelSerializer):
    billing_address = serializers.JSONField()  # Properly serialize as JSON
    shipping_address = serializers.JSONField()
    item_details = serializers.ListField()

    class Meta:
        model = Invoice
        exclude = ['invoicing_profile']  # Ensuring all fields from the Invoice model are serialized

# InvoicingProfile Serializer
class InvoicingProfileInvoices(serializers.ModelSerializer):
    invoices = serializers.SerializerMethodField()  # Nested serializer for invoices

    class Meta:
        model = InvoicingProfile
        fields = ['id', 'business', 'invoices']

    def get_invoices(self, obj):
        """
        Dynamically filters invoices based on the financial_year query parameter.
        """
        request = self.context.get('request')
        financial_year = request.query_params.get('financial_year') if request else None

        # Get all invoices related to the InvoicingProfile instance (obj)
        invoices = obj.invoices.all()

        # Apply the financial_year filter if provided
        if financial_year:
            invoices = invoices.filter(financial_year=financial_year)

        # Serialize the filtered invoices using the InvoicesSerializer
        return InvoicesSerializer(invoices, many=True).data


class InvoiceSerializerData(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'


class InvoiceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'

