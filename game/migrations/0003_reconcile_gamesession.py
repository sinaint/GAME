"""
Fake migration to reconcile Django migration state with actual DB schema.
The DB was already migrated manually; this only updates the migration graph.
"""
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_gamesession_game_id_alter_gamesession_profile_and_more'),
        ('gamebuilder', '0001_initial'),
        ('profiles', '0004_userpersona_structured_fields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Remove old game_id IntegerField added in 0002
        migrations.RemoveField(
            model_name='gamesession',
            name='game_id',
        ),
        # Remove old profile FK (altered in 0002 to profiles.Profile, now gone)
        migrations.RemoveField(
            model_name='gamesession',
            name='profile',
        ),
        # Remove old unique constraint from 0002
        migrations.RemoveConstraint(
            model_name='gamesession',
            name='unique_profile_game',
        ),
        # Add user FK
        migrations.AddField(
            model_name='gamesession',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='game_sessions',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        # Add game FK
        migrations.AddField(
            model_name='gamesession',
            name='game',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='sessions',
                to='gamebuilder.game',
            ),
        ),
        # Add persona FK (nullable)
        migrations.AddField(
            model_name='gamesession',
            name='persona',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='game_sessions',
                to='profiles.userpersona',
            ),
        ),
        # Add new unique constraint
        migrations.AddConstraint(
            model_name='gamesession',
            constraint=models.UniqueConstraint(fields=('user', 'game'), name='unique_user_game'),
        ),
    ]
