from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from cryptography.fernet import Fernet
from django.db import models
from djongo.models import ArrayField, EmbeddedField
from Tara.settings.default import *
import json
from djongo.models import ArrayField, EmbeddedField, JSONField


KEY = b'zSwtDDLJp6Qkb9CMCJnVeOzAeSJv-bA3VYNCy5zM-b4='  # Fernet key

class EncryptedField(models.Field):
    def __init__(self, *args, **kwargs):
        self.cipher = Fernet(KEY)
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        """Override to encrypt data before saving to the database"""
        if value is None:
            return None
        try:
            # Encrypt and decode to ensure it's a string
            encrypted_value = self.cipher.encrypt(value.encode()).decode()
            return encrypted_value
        except Exception as e:
            print(f"Encryption failed with error: {str(e)}")
            return None

    def from_db_value(self, value, expression, connection):
        """Override to decrypt data when retrieving from the database"""
        if value is None:
            return None
        try:
            # Decrypt the value before returning it
            decrypted_value = self.cipher.decrypt(value.encode()).decode()
            return decrypted_value
        except Exception as e:
            print(f"Decryption failed with error: {str(e)}")
            return None


class CustomPermission(models.Model):
    codename = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class CustomGroup(models.Model):
    name = models.CharField(max_length=255, unique=True)
    permissions = models.ManyToManyField(CustomPermission, related_name='groups')

    def __str__(self):
        return self.name

class CustomAccountManager(BaseUserManager):
    def create_user(self, email=None, password=None, mobile_number=None, created_by=None, **extra_fields):
        # Normalize email if provided
        email = self.normalize_email(email) if email else None

        # Ensure at least one identifier is provided
        if not email and not mobile_number:
            raise ValueError("At least one of email or mobile number must be provided.")

        # Check for existing users
        if email and self.model.objects.filter(email=email).exists():
            raise ValueError("A user with this email already exists.")
        if mobile_number and self.model.objects.filter(mobile_number=mobile_number).exists():
            raise ValueError("A user with this mobile number already exists.")

        # Dynamically set email_or_mobile
        email_or_mobile = email or mobile_number

        # Create user instance
        user = self.model(
            email=email,
            mobile_number=mobile_number,
            email_or_mobile=email_or_mobile,
            created_by=created_by,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, password=None, **extra_fields):
        # Set fields for superuser creation
        extra_fields.setdefault('user_type', 'superuser')
        return self.create_user(email=email, password=password, **extra_fields)


class AddressModel(models.Model):
    address_line1 = models.TextField(null=True, blank=False)
    address_line2 = models.TextField(null=True, blank=False)
    address_line3 = models.CharField(max_length=255, blank=True, null=True)
    pinCode = models.IntegerField(max_length=6, blank=True, null=True)
    state = models.CharField(max_length=20, null=True, blank=False)
    city = models.CharField(max_length=20, null=True, blank=False)
    country = models.CharField(max_length=20, null=True, blank=False)

    class Meta:
        abstract = True


USER_ROLE_CHOICES = [
    ('CA_Admin', 'CA Admin'),
    ('CA_Partner', 'CA Partner'),
    ('CA_Manager', 'CA Manager'),
    ('CA_Employee', 'CA Employee'),
    ('Individual_User', 'Individual User'),
    ('Business_Owner', 'Business Owner'),
    ('Business_Admin', 'Business Admin'),
    ('Business_Team Owner', 'Business Team Owner'),
    ('Business_Employee', 'Business Employee'),
    ('Business_TeamAssociate', 'Business Team Associate'),
    ('ServiceProvider_Owner', 'Service Provider Owner'),
    ('ServiceProvider_Admin', 'Service Provider Admin'),
    ('ServiceProvider_Employee', 'Service Provider Employee'),
    ('Tara_SuperAdmin', 'Tara Super Admin'),
    ('Tara_Admin', 'Tara Admin'),
    ('Tara_Editor', 'Tara Editor'),
    ('Tara_Developer', 'Tara Developer'),
    ('Tara_Tester', 'Tara Tester'),
]


class User(AbstractBaseUser):
    USER_TYPE_CHOICES = [
        ('Individual', 'Individual'),
        ('CA', 'Chartered Accountant Firm'),
        ('Business', 'Business/Corporate'),
        ('ServiceProvider', 'ServiceProvider')
    ]
    email_or_mobile = models.CharField(max_length=120, unique=True, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    mobile_number = models.CharField(max_length=15, null=True, blank=True)
    first_name = models.CharField(max_length=40, null=True, blank=True)
    last_name = models.CharField(max_length=40, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    user_kyc = models.BooleanField(default=False)
    otp = models.IntegerField(null=True)
    user_type = models.CharField(
        max_length=40,
        choices=USER_TYPE_CHOICES,
        default=None,  # Default value set to None
        null=True,  # Allows storing NULL in the database
        blank=True  # Allows leaving the field blank in forms
    )
    user_role = models.CharField(
        max_length=40,
        choices=USER_ROLE_CHOICES,
        default=None,  # Default value set to None
        null=True,  # Allows storing NULL in the database
        blank=True  # Allows leaving the field blank in forms
    )
    created_by = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_users'
    )

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email_or_mobile'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email_or_mobile or "User"


class UserGroup(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    group = JSONField(default=list, blank=True)  # List of custom group ids (from CustomGroup)
    custom_permissions = models.ManyToManyField(
        CustomPermission,
        related_name="user_groups",
        blank=True,
        help_text="User-specific custom permissions."
    )

    # Optional: Track the date when the user was added to the group
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email}"


class UserKYC(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userkyc')  # Added `related_name='userkyc'`
    name = models.CharField(max_length=40, blank=False, null=False)
    pan_number = EncryptedField(max_length=20, blank=True, null=True)
    aadhaar_number = EncryptedField(max_length=20, blank=True, null=True)
    date = models.DateField(null=True, blank=True)
    icai_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.JSONField(default=dict, null=True, blank=True)
    have_firm = models.BooleanField(default=False)

    @property
    def is_completed(self):
        required_fields = [self.name, self.pan_number, self.aadhaar_number, self.date]

        if self.have_firm:
            required_fields.append(self.icai_number)

        if self.address:
            required_address_fields = ['address_line1', 'address_line2', 'state', 'city', 'country']
            for field in required_address_fields:
                if not self.address.get(field):
                    return False  # If any required address field is missing or empty, return False

        return all(field is not None and field != "" for field in required_fields)

    def __str__(self):
        return f"{self.user.email} - {self.user.user_type}"


class FirmKYC(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    firm_name = models.CharField(max_length=255, blank=True, null=True)
    firm_registration_number = models.CharField(max_length=40, blank=True, null=True)
    firm_email = models.EmailField(unique=True, null=True, blank=True)
    firm_mobile_number = models.CharField(max_length=40, blank=True, null=True)
    number_of_firm_partners = models.IntegerField()
    address = models.JSONField(default=dict, null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.firm_registration_number}"


class ServicesMasterData(models.Model):
    service_name = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return f"{self.service_name}"


class ServiceDetails(models.Model):
    STATUS_CHOICES = [
        ('in progress', 'In Progress'),
        ('created', 'Created'),
        ('completed', 'Completed'),
        ('pending', 'Pending'),
    ]

    service_type = models.ForeignKey(ServicesMasterData, on_delete=models.CASCADE, related_name="service_details")
    date = models.DateField(default=timezone.now)
    status = models.CharField(
        max_length=40,
        choices=STATUS_CHOICES,
        default='pending'
    )
    comments = models.CharField(max_length=256, blank=True, null=True)
    quantity = models.IntegerField(null=False)
    visa_application = models.ForeignKey('VisaApplications', related_name='services', on_delete=models.CASCADE)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Service for {self.visa_application.first_name} {self.visa_application.last_name}"


class VisaApplications(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="visa_applications")
    passport_number = models.CharField(max_length=20, blank=True, null=True)
    purpose = models.CharField(max_length=20, blank=True, null=True)
    visa_type = models.CharField(max_length=15, blank=True, null=True)
    destination_country = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        unique_together = ("user", "purpose", "visa_type", "destination_country")

    def __str__(self):
        return f"{self.user.email} - {self.visa_type}"




