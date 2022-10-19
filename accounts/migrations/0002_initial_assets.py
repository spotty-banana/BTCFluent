from django.db import migrations

def add_assets(apps, schema_editor):
    Asset = apps.get_model('accounts', 'Asset')
    from accounts.models import DEFAULT_ASSETS
    for d in DEFAULT_ASSETS:
        Asset.objects.create(id=d[0], ticker=d[1], base_unit=d[1], atomic_unit=d[2], description=d[3])

class Migration(migrations.Migration):
    dependencies = [('accounts', '0001_initial')]
    atomic = False

    operations = [
        migrations.RunPython(add_assets),
    ]