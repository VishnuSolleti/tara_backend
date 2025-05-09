from django.db import models
from usermanagement.models import Context
import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from storages.backends.s3boto3 import S3Boto3Storage
from Tara.settings.default import AWS_PRIVATE_BUCKET_NAME
# Create your models here.


class PrivateS3Storage(S3Boto3Storage):
    bucket_name = AWS_PRIVATE_BUCKET_NAME
    custom_domain = f"{AWS_PRIVATE_BUCKET_NAME}.s3.amazonaws.com"  # Default S3 domain or your custom domain
    file_overwrite = True  # Allow file overwrite (optional)


class DocWallet(models.Model):
    context = models.OneToOneField(Context, on_delete=models.CASCADE, related_name='wallet')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wallet for {self.context}"


class Folder(models.Model):
    name = models.CharField(max_length=255)
    wallet = models.ForeignKey(DocWallet, on_delete=models.CASCADE, related_name='folders')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subfolders')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


def folder_path(instance, filename):
    # Get context id and context name (personal/business)
    context_id = instance.folder.wallet.context.id
    context_name = instance.folder.wallet.context.name
    context_name = context_name.replace(' ', '_')

    # Build folder hierarchy (e.g., PermanentWorkingPapers/subfolder1/subfolder2)
    folder_hierarchy = []
    folder = instance.folder
    while folder:
        folder_hierarchy.insert(0, folder.name.replace(' ', '_'))
        folder = folder.parent

    # Join all parts to form the path: context_id/context_name/folder1/folder2/filename
    path = os.path.join(str(context_id), context_name, *folder_hierarchy, filename)
    return path


class Document(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=folder_path, null=True, blank=True, storage=PrivateS3Storage())
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='documents')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Automatically assign the filename from the uploaded file if 'name' is not provided
        if not self.name:
            self.name = os.path.basename(self.file.name)  # Take the filename from the file path
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


@receiver(post_save, sender=DocWallet)
def create_root_folders(sender, instance, created, **kwargs):
    if created:
        root_folder_names = [
            'PermanentWorkingPapers',
            'CurrentWorkPapers',
            'OtherDocuments'
        ]
        for folder_name in root_folder_names:
            Folder.objects.create(
                name=folder_name,
                wallet=instance,
                parent=None  # Root folders have no parent
            )



