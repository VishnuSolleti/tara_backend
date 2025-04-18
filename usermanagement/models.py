from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.conf import settings
from dateutil.relativedelta import relativedelta
from Tara.settings.default import *
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from cryptography.fernet import Fernet
from djongo.models import ArrayField, EmbeddedField, JSONField
from .helpers import *
from django.core.validators import RegexValidator



YES_NO_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
        ('na', 'NA'),
    ]

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


class CustomAccountManager(BaseUserManager):
    def create_user(self, email=None, password=None, mobile_number=None,
                    created_by=None, **extra_fields):

        # Ensure a username is provided and is unique
        if not email:
            raise ValueError("Username must be provided.")
        if self.model.objects.filter(email=email).exists():
            raise ValueError("A user with this email already exists.")

        # Normalize email if provided
        email = self.normalize_email(email) if email else None

        # Create user instance
        user = self.model(
            email=email,
            mobile_number=mobile_number,
            created_by=created_by,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, password=None, **extra_fields):
        # Ensure required fields for superuser
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self.create_user(email=email, password=password, **extra_fields)


class Context(models.Model):
    name = models.CharField(max_length=255)
    context_type = models.CharField(
        max_length=20,
        choices=[
            ('personal', 'Personal'),
            ('business', 'Business')
        ]
    )
    owner_user = models.ForeignKey(
        'Users',
        on_delete=models.CASCADE,
        related_name='owned_contexts'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('suspended', 'Suspended'),
            ('archived', 'Archived')
        ],
        default='active'
    )
    profile_status = models.CharField(
        max_length=20,
        default='incomplete'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.name} - {self.context_type}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # If this is a new context, create default roles
        if is_new:
            self.create_default_roles()

    def create_default_roles(self):
        """Create default roles for this context"""
        if self.context_type == 'personal':
            # Personal context only gets owner role
            Role.objects.get_or_create(
                name="Owner",
                context=self,
                context_type='personal',
                role_type='owner',
                defaults={
                    "description": "Personal account owner with full access",
                    "is_system_role": True,
                    "is_default_role": True
                }
            )
        else:
            # Business context gets standard roles
            business_roles = [
                {
                    "name": "Owner",
                    "role_type": "owner",
                    "description": "Business owner with full access to all features"
                },
                {
                    "name": "Administrator",
                    "role_type": "admin",
                    "description": "Business administrator with full access to all modules"
                },
                {
                    "name": "Manager",
                    "role_type": "manager",
                    "description": "Business manager with elevated permissions"
                },
                {
                    "name": "Employee",
                    "role_type": "employee",
                    "description": "Regular employee with basic access"
                }
            ]

            for role_data in business_roles:
                Role.objects.get_or_create(
                    name=role_data["name"],
                    context=self,
                    context_type='business',
                    role_type=role_data["role_type"],
                    defaults={
                        "description": role_data["description"],
                        "is_system_role": True,
                        "is_default_role": True
                    }
                )


class Users(AbstractBaseUser):
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=10,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('invited', 'Invited')
        ],
        default='active'
    )
    service_request = models.CharField(max_length=40, null=True, blank=True, default=None)
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_users'
    )
    active_context = models.ForeignKey(
        Context,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='active_users'
    )
    # Add registration flow tracking
    registration_flow = models.CharField(
        max_length=20,
        choices=[
            ('module', 'Module-based'),
            ('service', 'Service-based'),
            ('standard', 'Standard')
        ],
        null=True,
        blank=True,
        help_text="Tracks which registration flow the user started from"
    )
    # Add initial module or service selection
    initial_selection = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="The initial module or service the user selected during registration"
    )
    # Add registration completion status
    registration_completed = models.CharField(
        max_length=3,
        choices=[
                ('yes', 'Yes'),
                ('no', 'No'),
            ],
        default='no',
        help_text="Indicates if the user has completed the registration process"
    )
    is_active = models.CharField(
        max_length=3,
        choices=YES_NO_CHOICES,
        default='no'
    )
    first_name = models.CharField(max_length=40, null=True, blank=True, default=None)
    last_name = models.CharField(max_length=40, null=True, blank=True, default=None)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Module(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    context_type = models.CharField(
        max_length=20,
        choices=[
            ('personal', 'Personal'),
            ('business', 'Business')
        ]
    )

    # Replace BooleanField with CharField
    is_active = models.CharField(
        max_length=3,
        choices=YES_NO_CHOICES,
        default='yes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=100)
    context = models.ForeignKey(Context, on_delete=models.CASCADE, related_name='roles')
    context_type = models.CharField(
        max_length=20,
        choices=[
            ('personal', 'Personal'),
            ('business', 'Business')
        ]
    )
    role_type = models.CharField(
        max_length=20,
        choices=[
            ('owner', 'Owner'),
            ('admin', 'Administrator'),
            ('manager', 'Manager'),
            ('employee', 'Employee'),
            ('custom', 'Custom')
        ]
    )
    description = models.TextField(blank=True, null=True)
    is_system_role = models.BooleanField(default=False)
    is_default_role = models.BooleanField(default=False)  # To identify default roles
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['name', 'context']
        ordering = ['context_type', 'role_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.context_type})"

    @classmethod
    def create_default_roles(cls):
        """Create default roles that are available for all contexts"""
        # Personal context default roles
        personal_roles = [
            {
                "name": "Owner",
                "context_type": "personal",
                "role_type": "owner",
                "description": "Personal account owner with full access",
                "is_default_role": True
            }
        ]

        # Business context default roles
        business_roles = [
            {
                "name": "Owner",
                "context_type": "business",
                "role_type": "owner",
                "description": "Business owner with full access to all features",
                "is_default_role": True
            },
            {
                "name": "Administrator",
                "context_type": "business",
                "role_type": "admin",
                "description": "Business administrator with full access to all modules",
                "is_default_role": True
            },
            {
                "name": "Manager",
                "context_type": "business",
                "role_type": "manager",
                "description": "Business manager with elevated permissions",
                "is_default_role": True
            },
            {
                "name": "Employee",
                "context_type": "business",
                "role_type": "employee",
                "description": "Regular employee with basic access",
                "is_default_role": True
            }
        ]

        # Create all default roles
        for role_data in personal_roles + business_roles:
            cls.objects.get_or_create(
                name=role_data["name"],
                context_type=role_data["context_type"],
                role_type=role_data["role_type"],
                defaults={
                    "description": role_data["description"],
                    "is_default_role": True,
                    "is_system_role": True
                }
            )

    @classmethod
    def create_context_roles(cls, context):
        """Create roles for a specific context based on default roles"""
        # Get default roles for this context type
        default_roles = cls.objects.filter(
            context_type=context.context_type,
            is_default_role=True
        )

        # Create context-specific instances of default roles
        for default_role in default_roles:
            cls.objects.get_or_create(
                name=default_role.name,
                context=context,
                context_type=default_role.context_type,
                role_type=default_role.role_type,
                defaults={
                    "description": default_role.description,
                    "is_system_role": True,
                    "is_default_role": True
                }
            )

    @classmethod
    def create_custom_role(cls, context, name, role_type='custom', description=None):
        """Create a custom role for a specific context"""
        return cls.objects.create(
            name=name,
            context=context,
            context_type=context.context_type,
            role_type=role_type,
            description=description,
            is_system_role=False,
            is_default_role=False
        )


class UserContextRole(models.Model):
    PERMISSION_CHOICES = [
        ('create', 'Create'),
        ('read', 'Read'),
        ('update', 'Update'),
        ('delete', 'Delete')
    ]

    user = models.ForeignKey('Users', on_delete=models.CASCADE, related_name='context_roles')
    context = models.ForeignKey(Context, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_contexts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    added_by = models.ForeignKey('Users', on_delete=models.CASCADE, related_name='user_context_roles_added')
    STATUS_CHOICES = [
        ("active", "Active"),
        ("invited", "Invited"),
        ("suspended", "Suspended"),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    class Meta:
        unique_together = ['user', 'context', 'role']

    def __str__(self):
        return f"{self.user.email} - {self.context.name} - {self.role.name}"


class ModuleFeature(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='features')
    service = models.CharField(max_length=100)  # Employee table
    action = models.CharField(max_length=100)  # e.g. 'create'
    label = models.CharField(max_length=255)  # 'Can Create Employee'

    class Meta:
        unique_together = ('module', 'service', 'action')

    def __str__(self):
        return f"{self.module.name} - {self.service}"


class UserFeaturePermission(models.Model):
    """
    Represents feature permissions for a user within a context and module.
    """
    user_context_role = models.ForeignKey(UserContextRole, on_delete=models.CASCADE, related_name='feature_permissions')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='user_permissions')
    actions = models.JSONField(default=list)  # List of service.action combinations
    created_by = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True,
                                   related_name='created_feature_permissions')
    is_active = models.CharField(
        max_length=3,
        choices=YES_NO_CHOICES,
        default='yes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user_context_role', 'module')

    def __str__(self):
        return f"{self.user_context_role.user.email} - {self.module.name}"


class Suite(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    included_modules = models.ManyToManyField(Module, related_name='included_in_suites')
    available_for = models.CharField(
        max_length=20,
        choices=[
            ('personal', 'Personal'),
            ('business', 'Business'),
            ('all', 'All')
        ],
        default='all'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive')
        ],
        default='active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.suite_id})"

    class Meta:
        ordering = ['name']


class SubscriptionPlan(models.Model):
    PLAN_TYPE_CHOICES = [
        ('trial', 'Trial'),
        ('monthly', 'Monthly'),
        ('annually', 'Annually')
    ]

    module = models.ForeignKey(Module, on_delete=models.CASCADE, null=True, blank=True,
                               related_name='module_subscriptions')
    suite = models.ForeignKey(Suite
                              , on_delete=models.CASCADE, null=True, blank=True,
                              related_name='suite_subscriptions')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES)

    # Base pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Base price for the plan")
    # Billing cycle
    billing_cycle_days = models.IntegerField(default=30,
                                             help_text="Number of days in billing cycle")
    features_enabled = models.JSONField(default=dict)
    is_active = models.CharField(
        max_length=3,
        choices=YES_NO_CHOICES,
        default='yes'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['module', 'name']

    def __str__(self):
        return f"{self.module.name} - {self.name} ({self.plan_type})"

    def calculate_price(self, usage_count):
        """Calculate price based on usage"""
        if self.plan_type == 'trial':
            return 0

        if usage_count <= self.free_tier_limit:
            return self.base_price

        additional_units = usage_count - self.free_tier_limit
        return self.base_price + (additional_units * self.price_per_unit)

    def get_next_renewal_date(self, start_date):
        """Calculate the next renewal date based on billing cycle"""
        return start_date + relativedelta(days=self.billing_cycle_days)


class ContextSuiteSubscription(models.Model):
    context = models.ForeignKey(Context, on_delete=models.CASCADE, related_name='context_subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE,
                                      related_name='subscription_processed_for')
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('trial', 'Trial'),
            ('expired', 'Expired'),
            ('cancelled', 'Cancelled')
        ],
        default='active'
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    auto_renew = models.CharField(
        max_length=3,
        choices=[
                ('yes', 'Yes'),
                ('no', 'No'),
            ],
        default='no'
    )
    # New fields for proration
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    applied_credit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.context.name} - {self.suite.name} ({self.plan.name})"


class ModuleSubscription(models.Model):
    context = models.ForeignKey(Context, on_delete=models.CASCADE, related_name='module_subscriptions')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='module_subscriptions')
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('trial', 'Trial'),
            ('expired', 'Expired'),
            ('cancelled', 'Cancelled')
        ],
        default='active'
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    auto_renew = models.CharField(
        max_length=3,
        choices=[
                ('yes', 'Yes'),
                ('no', 'No'),
            ],
        default='no'
    )

    # New field to track if this subscription is part of a suite
    via_suite = models.CharField(
        max_length=3,
        choices=YES_NO_CHOICES,
        default='no'
    )
    suite_subscription = models.ForeignKey(
        ContextSuiteSubscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name='module_subscriptions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.context.name} - {self.module.name} ({self.plan.name})"


class ModuleAddOn(models.Model):
    subscription = models.ForeignKey(ModuleSubscription, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)  # e.g., 'extra_user', 'extra_gstin'
    quantity = models.IntegerField(default=1)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    billing_cycle = models.CharField(max_length=10, default="monthly")  # monthly/yearly
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subscription.context.name} - {self.type} ({self.quantity})"


class SubscriptionCycle(models.Model):
    subscription = models.ForeignKey(ModuleSubscription, on_delete=models.CASCADE, related_name="cycles")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.CharField(
        max_length=3,
        choices=[
            ('yes', 'Yes'),
            ('no', 'No'),
        ],
        default='no',
    )
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    feature_usage = models.JSONField(
        default=dict,
        help_text="Tracks feature usage quantities during this cycle"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subscription.context.name} - {self.start_date.date()}"

    def update_feature_usage(self, feature_key, quantity):
        """
        Update usage for a specific feature
        """
        current_usage = self.feature_usage.get(feature_key, 0)
        self.feature_usage[feature_key] = current_usage + quantity
        self.save()


@receiver(post_save, sender=ModuleSubscription)
def create_initial_subscription_cycle(sender, instance, created, **kwargs):
    """
    Creates initial subscription cycle only when a new ModuleSubscription is created
    """
    if not created:  # Only proceed if this is a new subscription
        return

    try:
        with transaction.atomic():
            # Initialize feature usage based on plan's features
            initial_feature_usage = {}
            if instance.plan.features_enabled:
                for feature, details in instance.plan.features_enabled.items():
                    if isinstance(details, dict) and 'limit' in details:
                        initial_feature_usage[feature] = 0

            # Create the initial subscription cycle
            SubscriptionCycle.objects.create(
                subscription=instance,
                start_date=instance.start_date,
                end_date=instance.end_date,
                amount = Decimal("0.00") if instance.status == 'trial' else Decimal(str(instance.plan.base_price)),
                is_paid='yes' if instance.status == 'trial' else 'no',
                feature_usage=initial_feature_usage
            )

    except Exception as e:
        print(f"Error creating initial subscription cycle: {str(e)}")
        raise


class ModuleUsageCycle(models.Model):
    cycle = models.ForeignKey(SubscriptionCycle, on_delete=models.CASCADE, related_name="usages")
    feature_key = models.CharField(max_length=100)  # e.g., 'invoices', 'payrolls'
    usage_count = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['cycle', 'feature_key']


@receiver(post_save, sender=SubscriptionCycle)
def create_usage_cycles(sender, instance, created, **kwargs):
    if not created:
        return

    plan = instance.subscription.plan
    features = plan.features_enabled or {}

    for feature_key, config in features.items():
        # Only track features with "limit" or explicitly "track": true
        if isinstance(config, dict):
            if config.get("limit") is not None or config.get("track") is True:
                ModuleUsageCycle.objects.create(
                    cycle=instance,
                    feature_key=feature_key,
                    usage_count=0
                )
        elif isinstance(config, int):  # basic numeric limit
            ModuleUsageCycle.objects.create(
                cycle=instance,
                feature_key=feature_key,
                usage_count=0
            )


class UserKYC(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE, related_name='userkyc')  # `related_name='userkyc'`
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
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
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


class BaseModel(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Business(BaseModel):
    entity_choices = [
        ('soleProprietor', 'Sole Proprietor'),
        ('partnershipUnregistered', 'Partnership Unregistered'),
        ('partnershipRegistered', 'Partnership Registered'),
        ('llp', 'LLP'),
        ('huf', 'HUF'),
        ('privateLimitedCompany', 'Private Limited Company'),
        ('publicCompanyListed', 'Public Company Listed'),
        ('publicCompanyUnlisted', 'Public Company Unlisted'),
        ('trust', 'Trust'),
        ('society', 'Society'),
        ('opc', 'OPC'),
        ('others', 'Others (Specify)'),
    ]

    business_nature_choices = [
        ('Agency or Sales House', 'Agency or Sales House'),
        ('Agriculture', 'Agriculture'),
        ('Art and Design', 'Art and Design'),
        ('Automotive', 'Automotive'),
        ('Construction', 'Construction'),
        ('Consulting', 'Consulting'),
        ('Consumer Packaged Goods', 'Consumer Packaged Goods'),
        ('Education', 'Education'),
        ('Engineering', 'Engineering'),
        ('Entertainment', 'Entertainment'),
        ('Financial Services', 'Financial Services'),
        ('Food Services (Restaurants/Fast Food)', 'Food Services (Restaurants/Fast Food)'),
        ('Gaming', 'Gaming'),
        ('Government', 'Government'),
        ('Health Care', 'Health Care'),
        ('Interior Design', 'Interior Design'),
        ('Internal', 'Internal'),
        ('Legal', 'Legal'),
        ('Manufacturing', 'Manufacturing'),
        ('Marketing', 'Marketing'),
        ('Mining and Logistics', 'Mining and Logistics'),
        ('Non-Profit', 'Non-Profit'),
        ('Publishing and Web Media', 'Publishing and Web Media'),
        ('Real Estate', 'Real Estate'),
        ('Retail (E-Commerce and Offline)', 'Retail (E-Commerce and Offline)'),
        ('Services', 'Services'),
        ('Technology', 'Technology'),
        ('Telecommunications', 'Telecommunications'),
        ('Travel/Hospitality', 'Travel/Hospitality'),
        ('Web Designing', 'Web Designing'),
        ('Web Development', 'Web Development'),
        ('Writers', 'Writers'),
    ]

    client = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='business_clients_id')
    nameOfBusiness = models.CharField(max_length=200, unique=True, db_index=True)
    registrationNumber = models.CharField(max_length=120, null=True, blank=True, default=None)
    entityType = models.CharField(max_length=50, null=True, blank=True, default=None)
    headOffice = JSONField(default=dict, null=True, blank=True)
    pan = models.CharField(max_length=15, null=True, blank=True, default=None)
    business_nature = models.CharField(
        max_length=50, choices=business_nature_choices, null=True, blank=True, default=None
    )  # Default as None
    trade_name = models.CharField(max_length=100, null=True, blank=True, default=None)
    mobile_number = models.CharField(max_length=15, null=True, blank=True, default=None)
    email = models.EmailField(null=True, blank=True, default=None)
    dob_or_incorp_date = models.DateField(null=True, blank=True, default=None)

    class Meta:
        unique_together = [('nameOfBusiness', 'pan')]

    def __str__(self):
        return str(self.nameOfBusiness)


class GSTDetails(BaseModel):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='gst_details')
    gstin = models.CharField(max_length=120, unique=True, null=True, blank=True)
    gst_username = models.CharField(max_length=60, null=True, blank=True)
    gst_password = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=120, null=True, blank=True)
    pinCode = models.IntegerField(null=True)
    branch_name = models.CharField(max_length=60, null=True, blank=True, default=None)
    state = models.CharField(max_length=60, null=True, blank=True, default=None)
    authorized_signatory_pan = models.CharField(max_length=60, null=True, blank=True, default=None)
    gst_document = models.FileField(upload_to=gst_document_upload_path, null=True, blank=True)

    def __str__(self):
        return f"GST Details for {self.business.nameOfBusiness}"


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
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="visa_applications")
    passport_number = models.CharField(max_length=20, blank=True, null=True)
    purpose = models.CharField(max_length=20, blank=True, null=True)
    visa_type = models.CharField(max_length=15, blank=True, null=True)
    destination_country = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        unique_together = ("user", "purpose", "visa_type", "destination_country")

    def __str__(self):
        return f"{self.user.email} - {self.visa_type}"


class Contact(models.Model):
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    email = models.EmailField()  # No unique constraint
    mobile_number = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?\d{10,15}$',
                message="Enter a valid mobile number with 10-15 digits, optionally starting with +"
            )
        ]
    )
    message = models.TextField()
    created_date = models.DateField(auto_now_add=True)  # Stores only Date (YYYY-MM-DD)
    created_time = models.TimeField(auto_now_add=True)  # Stores only Time (HH:MM:SS)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"


class Consultation(models.Model):
    name = models.CharField(max_length=40)
    email = models.EmailField()  # No unique constraint
    mobile_number = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?\d{10,15}$',
                message="Enter a valid mobile number with 10-15 digits, optionally starting with +"
            )
        ]
    )
    message = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    created_date = models.DateField(auto_now_add=True)  # Stores only Date (YYYY-MM-DD)
    created_time = models.TimeField(auto_now_add=True)  # Stores only Time (HH:MM:SS)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"









