from django.db import models

# class User(models.Model):
#     usernamename = models.CharField(max_length=100)
#     email = models.EmailField()
#     # roll = models.IntegerField()

    # def __str__(self):
    #     return self.name
        
class Gallery(models.Model):
    profile_image = models.ImageField(upload_to='profileimg', blank=True,
                                      help_text='Optional: Upload a profile image')
    my_file = models.FileField(upload_to = 'doc', blank=True)
    date = models.DateTimeField(auto_now_add = True)

    def delete(self, *args, **kwargs):
        if self.profile_image:
            self.profile_image.delete(save=False)

        super().delete(*args, **kwargs)