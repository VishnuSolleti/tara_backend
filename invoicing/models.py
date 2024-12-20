from django.core.validators import RegexValidator
from django.db import models
from djongo.models import ArrayField, EmbeddedField, JSONField
from user_management.models import User
from django.core.exceptions import ValidationError


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def validate_account_number(value):
    if value < 0 or value > 9999999999999999:
        raise ValidationError("Account number must be a positive integer with up to 16 digits")


class Address(models.Model):
    address_line1 = models.CharField(max_length=200, null=True, blank=True)
    state = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True)
    postal_code = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True


class DetailedItem(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    quantity = models.CharField(max_length=200, null=True, blank=True)
    unit_price = models.CharField(max_length=200, null=True, blank=True)
    hsn_sac = models.CharField(max_length=200, null=True, blank=True)
    discount = models.CharField(max_length=200, null=True, blank=True)
    amount = models.CharField(max_length=200, null=True, blank=True)
    cgst = models.CharField(max_length=200, null=True, blank=True)
    sgst = models.CharField(max_length=200, null=True, blank=True)
    igst = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        abstract = True


class PaymentDetail(models.Model):
    date = models.CharField(max_length=50, null=True, blank=True)
    paid_amount = models.FloatField(null=True, blank=True)

    class Meta:
        abstract = True


class InvoicingProfile(BaseModel):
    business = models.OneToOneField(User, on_delete=models.CASCADE)
    pan_number = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=50)
    account_number = models.BigIntegerField(validators=[validate_account_number])
    ifsc_code = models.CharField(max_length=50)
    swift_code = models.CharField(max_length=50)
    invoice_format = JSONField(default=dict())
    signature = models.ImageField(upload_to="signatures/", null=True, blank=True)

    def __str__(self):
        return f"Invoicing Profile: {self.business}"


class CustomerProfile(models.Model):
    invoicing_profile = models.ForeignKey(InvoicingProfile, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    pan_number = models.CharField(max_length=10, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    address_line1 = models.CharField(max_length=200, null=True, blank=True)
    address_line2 = models.CharField(max_length=200, null=True, blank=True)
    state = models.CharField(max_length=30, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    city = models.CharField(max_length=30, null=True, blank=True)
    gst_registered = models.CharField(max_length=100, null=True, blank=True)
    gstin = models.CharField(max_length=100, null=True, blank=True)
    gst_type = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    mobile_number = models.CharField(max_length=15, null=True, blank=True)
    opening_balance = models.IntegerField(null=True)

    def __str__(self):
        return f"Customer: {self.name}"


class GoodsAndServices(models.Model):
    invoicing_profile = models.ForeignKey(InvoicingProfile, on_delete=models.CASCADE, null=True, related_name='goods_and_services')
    type = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    sku_value = models.FloatField(null=True)
    units = models.CharField(max_length=100, null=True, blank=True)
    hsn_sac = models.CharField(max_length=500, null=True, blank=True)
    gst_rate = models.CharField(max_length=10, null=True, blank=True)
    tax_preference = models.IntegerField(null=True)
    selling_price = models.IntegerField(null=True)
    description = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - GST Rate: {self.gst_rate}%"


class Invoice(models.Model):
    invoicing_profile = models.ForeignKey(InvoicingProfile, on_delete=models.CASCADE, null=True)
    customer = models.CharField(max_length=200, null=False, blank=False)
    terms = models.CharField(max_length=500, null=False, blank=False)
    financial_year = models.CharField(max_length=50, null=False, blank=False)
    invoice_number = models.CharField(max_length=50, null=False, blank=False)
    invoice_date = models.DateField(null=False, blank=False)
    place_of_supply = models.CharField(max_length=500, null=False, blank=False)
    billing_address = EmbeddedField(model_container=Address, default=dict)
    shipping_address = EmbeddedField(model_container=Address, default=dict)
    item_details = JSONField(
        default=list,
        blank=True
    )
    total_amount = models.FloatField(null=True, blank=False)
    subtotal_amount = models.FloatField(null=True, blank=False)
    shipping_amount = models.FloatField(null=True, blank=False)
    cgst_amount = models.FloatField(null=True, blank=False)
    sgst_amount = models.FloatField(null=True, blank=False)
    igst_amount = models.FloatField(null=True, blank=False)
    pending_amount = models.FloatField(null=True, blank=False)
    amount_invoiced = models.FloatField(null=True, blank=False)
    payment_status = models.CharField(max_length=50, default="Unpaid", null=True, blank=True)
    notes = models.CharField(max_length=500, null=True, blank=True)
    terms_and_conditions = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"Invoice: {self.invoice_number}"

#
# class PaymentDetail(models.Model):
#     invoice = models.ForeignKey(Invoice, related_name='payments', on_delete=models.CASCADE)
#     date = models.DateTimeField(auto_now_add=True)
#     amount = models.FloatField()
#     method = models.CharField(max_length=50)
#     reference_number = models.CharField(max_length=50, null=True, blank=True)
#
#     def __str__(self):
#         return f"Payment for Invoice #{self.invoice.invoice_number} - {self.method}"

