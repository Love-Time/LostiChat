from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

User = get_user_model()


# Create your models here.

class Friends(models.Model):
    first_user = models.ForeignKey(User, related_name='user1', on_delete=models.CASCADE)
    second_user = models.ForeignKey(User, related_name='user2', on_delete=models.CASCADE)

    ACCEPT = (
        (0, "waiting"),
        (-1, "not accepted"),
        (1, "accepted"))

    accepted = models.IntegerField(choices=ACCEPT, max_length=1, default=0)
    class Meta:
        constraints = [
        models.UniqueConstraint(
            fields=['first_user', 'second_user'], name='unique_friends_first_user_second_user'
        ),
        ]

    def clean(self):
        if self.first_user == self.second_user:
            raise ValidationError("You can't add yourself as a friend")

    def save(self, *args, **kwargs):
        data = Friends.objects.filter(Q(first_user=self.second_user) & Q(second_user=self.first_user))
        if data:
            self.accepted = 1
            super(Friends, self).save(*args, **kwargs)
            if data[0].accepted != 1:
                data[0].accepted = 1
                data[0].save()
        else:
            if self.accepted != -1:
                self.accepted = 0
            super(Friends, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        data = Friends.objects.filter(Q(first_user=self.second_user) & Q(second_user=self.first_user))
        print(data)
        if data:
            super(Friends, self).delete(*args, **kwargs)
            data[0].accepted = -1
            data[0].save()
        else:
            super(Friends, self).delete(*args, **kwargs)




