from django.db import models
from accounts.models import Profile


class CommissionType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Commission(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Full', 'Full'),
    ]

    title = models.CharField(max_length=255)
    type = models.ForeignKey(
        CommissionType,
        on_delete=models.SET_NULL,
        null=True,
        related_name='commissions'
    )
    maker = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='commissions_created', null=True)
    description = models.TextField()
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='Open')
    people_required = models.PositiveIntegerField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return self.title


class Job(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Full', 'Full'),
    ]

    commission = models.ForeignKey(
        Commission, on_delete=models.CASCADE, related_name='jobs')
    role = models.CharField(max_length=255)
    manpower_required = models.PositiveIntegerField()
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='Open')

    class Meta:
        ordering = [
            'status',
            '-manpower_required',
            'role'
        ]

    def __str__(self):
        return f"{self.role} (Commission: {self.commission.title})"


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE,
                            related_name='applications')
    applicant = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='job_applications')
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='Pending')
    applied_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = [
            'status',
            '-applied_on'
        ]

    def __str__(self):
        return f"{self.applicant.user.username} applied for {self.job.role}"
