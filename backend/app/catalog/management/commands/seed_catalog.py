from pathlib import Path

from django.core.files import File
from django.core.management import call_command
from django.core.management.base import BaseCommand

from catalog.models import CatalogItem

SEED_DIR = Path(__file__).resolve().parent.parent.parent / "seed_images"


class Command(BaseCommand):
    help = "Загружает fixture каталога и прикрепляет placeholder-картинки в MEDIA_ROOT."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush", action="store_true",
            help="Удалить существующий каталог перед загрузкой.",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            CatalogItem.objects.all().delete()
        elif CatalogItem.objects.exists():
            self.stdout.write("Каталог не пуст, пропускаю. Используй --flush для перезаписи.")
            return

        call_command("loaddata", "catalog", verbosity=0)

        # даты уже заданы в fixture, здесь только прикрепляем картинки по порядку pk
        items = list(CatalogItem.objects.order_by("pk"))
        images = sorted(SEED_DIR.glob("*.png"))
        for item, img_path in zip(items, images):
            with img_path.open("rb") as f:
                item.image.save(img_path.name, File(f), save=True)

        self.stdout.write(self.style.SUCCESS(f"Загружено записей: {len(items)}"))
