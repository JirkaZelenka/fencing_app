# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Název klubu')),
            ],
            options={
                'verbose_name': 'Klub',
                'verbose_name_plural': 'Kluby',
            },
        ),
        migrations.CreateModel(
            name='CircuitTraining',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Název sestavy')),
                ('description', models.TextField(blank=True, verbose_name='Popis')),
                ('exercises', models.TextField(verbose_name='Cvičení (každé na nový řádek)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='circuit_trainings', to=settings.AUTH_USER_MODEL, verbose_name='Vytvořil')),
            ],
            options={
                'verbose_name': 'Kruháč',
                'verbose_name_plural': 'Kruháče',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='EquipmentItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Název')),
                ('category', models.CharField(max_length=100, verbose_name='Kategorie')),
                ('description', models.TextField(blank=True, verbose_name='Popis')),
                ('approximate_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Orientační cena')),
                ('purchase_link', models.URLField(blank=True, verbose_name='Odkaz na nákup')),
                ('image', models.ImageField(blank=True, null=True, upload_to='equipment/', verbose_name='Obrázek')),
            ],
            options={
                'verbose_name': 'Vybavení',
                'verbose_name_plural': 'Vybavení',
                'ordering': ['category', 'name'],
            },
        ),
        migrations.CreateModel(
            name='GlossaryTerm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('term', models.CharField(max_length=200, verbose_name='Pojem')),
                ('definition', models.TextField(verbose_name='Definice')),
            ],
            options={
                'verbose_name': 'Pojem ve slovníčku',
                'verbose_name_plural': 'Slovníček pojmů',
                'ordering': ['term'],
            },
        ),
        migrations.CreateModel(
            name='GuideVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Název')),
                ('youtube_url', models.URLField(verbose_name='YouTube URL')),
                ('description', models.TextField(blank=True, verbose_name='Popis')),
                ('category', models.CharField(blank=True, max_length=100, verbose_name='Kategorie')),
            ],
            options={
                'verbose_name': 'Návodové video',
                'verbose_name_plural': 'Návodová videa',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='RulesDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Název')),
                ('content', models.TextField(verbose_name='Obsah')),
                ('file', models.FileField(blank=True, null=True, upload_to='rules/', verbose_name='Soubor')),
            ],
            options={
                'verbose_name': 'Pravidla',
                'verbose_name_plural': 'Pravidla',
            },
        ),
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Název turnaje')),
                ('date', models.DateField(verbose_name='Datum')),
                ('location', models.CharField(blank=True, max_length=200, verbose_name='Místo')),
                ('is_internal', models.BooleanField(default=False, verbose_name='Interní turnaj')),
            ],
            options={
                'verbose_name': 'Turnaj',
                'verbose_name_plural': 'Turnaje',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='CalendarEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Název')),
                ('description', models.TextField(blank=True, verbose_name='Popis')),
                ('start_date', models.DateTimeField(verbose_name='Začátek')),
                ('end_date', models.DateTimeField(blank=True, null=True, verbose_name='Konec')),
                ('location', models.CharField(blank=True, max_length=200, verbose_name='Místo')),
                ('external_link', models.URLField(blank=True, verbose_name='Externí odkaz (czechfencing)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Akce v kalendáři',
                'verbose_name_plural': 'Akce v kalendáři',
                'ordering': ['start_date'],
            },
        ),
        migrations.CreateModel(
            name='CircuitSong',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Název skladby')),
                ('audio_file', models.FileField(upload_to='circuit_songs/', verbose_name='Audio soubor')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('circuit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='songs', to='fencers.circuittraining', verbose_name='Kruháč')),
            ],
            options={
                'verbose_name': 'Skladba pro kruháč',
                'verbose_name_plural': 'Skladby pro kruháče',
            },
        ),
        migrations.CreateModel(
            name='EventPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Název')),
                ('description', models.TextField(blank=True, verbose_name='Popis')),
                ('photo', models.ImageField(upload_to='event_photos/', verbose_name='Fotka')),
                ('event_date', models.DateField(blank=True, null=True, verbose_name='Datum akce')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('is_featured', models.BooleanField(default=False, verbose_name='Doporučená')),
                ('uploaded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Nahrál')),
            ],
            options={
                'verbose_name': 'Fotka z akce',
                'verbose_name_plural': 'Fotky z akcí',
                'ordering': ['-event_date', '-uploaded_at'],
            },
        ),
        migrations.CreateModel(
            name='EventReaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('will_attend', models.BooleanField(default=False, verbose_name='Zúčastním se')),
                ('comment', models.TextField(blank=True, verbose_name='Komentář')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reactions', to='fencers.calendarevent', verbose_name='Akce')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_reactions', to=settings.AUTH_USER_MODEL, verbose_name='Uživatel')),
            ],
            options={
                'verbose_name': 'Reakce na akci',
                'verbose_name_plural': 'Reakce na akce',
                'unique_together': {('event', 'user')},
            },
        ),
        migrations.CreateModel(
            name='FencerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Telefon')),
                ('club', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='fencers.club', verbose_name='Klub')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='fencer_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Profil šermíře',
                'verbose_name_plural': 'Profily šermířů',
            },
        ),
        migrations.CreateModel(
            name='PaymentStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_paid', models.BooleanField(default=False, verbose_name='Zaplaceno')),
                ('payment_date', models.DateField(blank=True, null=True, verbose_name='Datum platby')),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Částka')),
                ('qr_code', models.ImageField(blank=True, null=True, upload_to='qr_codes/', verbose_name='QR kód')),
                ('payment_info', models.TextField(blank=True, verbose_name='Informace k platbě')),
                ('fencer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment_status', to=settings.AUTH_USER_MODEL, verbose_name='Šermíř')),
            ],
            options={
                'verbose_name': 'Stav platby',
                'verbose_name_plural': 'Stavy plateb',
            },
        ),
        migrations.CreateModel(
            name='TournamentParticipation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.IntegerField(blank=True, null=True, verbose_name='Umístění')),
                ('wins', models.IntegerField(default=0, verbose_name='Výhry')),
                ('losses', models.IntegerField(default=0, verbose_name='Prohry')),
                ('touches_scored', models.IntegerField(default=0, verbose_name='Zasazené zásahy')),
                ('touches_received', models.IntegerField(default=0, verbose_name='Obdržené zásahy')),
                ('fencer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tournament_participations', to=settings.AUTH_USER_MODEL, verbose_name='Šermíř')),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participations', to='fencers.tournament', verbose_name='Turnaj')),
            ],
            options={
                'verbose_name': 'Účast na turnaji',
                'verbose_name_plural': 'Účasti na turnajích',
                'unique_together': {('fencer', 'tournament')},
                'ordering': ['-tournament__date'],
            },
        ),
        migrations.CreateModel(
            name='TrainingNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Datum')),
                ('notes', models.TextField(verbose_name='Poznámky')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('fencer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='training_notes', to=settings.AUTH_USER_MODEL, verbose_name='Šermíř')),
            ],
            options={
                'verbose_name': 'Poznámka z tréninku',
                'verbose_name_plural': 'Poznámky z tréninků',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='UserEquipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_owned', models.BooleanField(default=False, verbose_name='Vlastním')),
                ('purchase_date', models.DateField(blank=True, null=True, verbose_name='Datum nákupu')),
                ('equipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fencers.equipmentitem', verbose_name='Vybavení')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='equipment', to=settings.AUTH_USER_MODEL, verbose_name='Uživatel')),
            ],
            options={
                'verbose_name': 'Vybavení uživatele',
                'verbose_name_plural': 'Vybavení uživatelů',
                'unique_together': {('user', 'equipment')},
            },
        ),
    ]

