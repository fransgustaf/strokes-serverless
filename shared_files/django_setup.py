if True: # Don't do this if not necessary, but how do we know?	
	print("I am here")
	from django.conf import settings
	settings.configure(
		DATABASES = {
		'default': {
		'ENGINE': 'django.db.backends.mysql',
		'NAME': 'strokes',
		'USER': 'root',
		'PASSWORD': 'heyheyhey',
		'HOST': 'strokes.cgf0r7uvrbjf.ap-southeast-1.rds.amazonaws.com',
		'PORT': '3306',
		}
		},
		INSTALLED_APPS = ("strokes",)
		)

	import django
	django.setup()
