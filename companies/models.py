from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone 


class Company(models.Model):
    owner = models.OneToOneField(User , on_delete=models.CASCADE ,related_name='company_profile')
    name = models.CharField(max_length = 255 ,verbose_name = "company name" , null = False ,unique = True)
    image = models.ImageField(upload_to = 'companies_images/' ,null = True)
    location = models.CharField(max_length = 255 , null = True)
    phone_number = PhoneNumberField(null = False , blank = True ,unique = True)
    description = models.TextField(null = True)
    email = models.EmailField(null = False , blank = True ,unique = True)
    website = models.URLField(null = True , blank = True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    is_active = models.BooleanField(default = True)
    deleted_at = models.DateTimeField(null = True , blank = True)
    def save(self, *args, **kwargs):
        try:
            old_instance = Company.objects.get(pk=self.pk)
            if old_instance.image and old_instance.image != self.image:
                old_instance.image.delete(save=False)
        except Company.DoesNotExist:
            pass
        
        super().save(*args, **kwargs)


    def __str__(self):
        return self.name


    def soft_delete(self):
        self.is_active = False
        self.deleted_at = timezone.now() 
        self.save()


    def restore(self):
        self.is_active = True
        self.deleted_at = None
        self.save()
    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ['-created_at']
    

