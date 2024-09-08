from django.db import models

class UserDetails(models.Model):
    GENDER_CHOICES = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
    ]
    
    FAMILY_STATUS_CHOICES = [
        ('single', 'Одинокий/ая'),
        ('married', 'Женат/Замужем'),
        ('widowed', 'Вдова/Вдовец'),
    ]
    
    LIFESTYLE_CHOICES = [
        ('no_activity', 'Почти нет активности'),
        ('low_activity', 'Слабая активность'),
        ('high_activity', 'Высокая активность'),
        ('extreme_activity', 'Экстремальная активность'),
    ]

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    family_status = models.CharField(max_length=10, choices=FAMILY_STATUS_CHOICES)
    height = models.PositiveIntegerField()  # Рост
    weight = models.PositiveIntegerField()  # Вес
    lifestyle = models.CharField(max_length=20, choices=LIFESTYLE_CHOICES)
    sexual_activity = models.BooleanField()  # Наличие половой жизни
    medication_allergy = models.BooleanField()  # Аллергия на медикаменты
    medication_count = models.PositiveIntegerField()  # Количество принимаемых медикаментов
    medication_frequency = models.CharField(max_length=10)  # Как часто принимаете лекарства
    smoking_frequency = models.CharField(max_length=10)  # Как часто курите
    alcohol_frequency = models.CharField(max_length=10)  # Как часто пьёте

    def __str__(self):
        return f"{self.id}: {self.gender}, {self.family_status}"
