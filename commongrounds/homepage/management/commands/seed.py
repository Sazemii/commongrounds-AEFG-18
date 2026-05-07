"""
Idempotent demo seed.

Run:
    python manage.py seed

Creates a fixed set of demo users (one per Profile role) and ~5 records
for every app's main models. Re-running is safe: it uses get_or_create.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import Profile
from bookclub.models import Book, BookReview, Bookmark, Borrow, Genre
from commissions.models import Commission, CommissionType, Job, JobApplication
from diyprojects.models import (
    Favorite,
    Project,
    ProjectCategory,
    ProjectRating,
    ProjectReview,
)
from localevents.models import Event, EventSignup, EventType
from merchstore.models import Product, ProductType, Transaction


User = get_user_model()


DEMO_PASSWORD = "demopass123"

DEMO_USERS = [
    ("alice",  "Alice Reader",     "alice@example.com",  Profile.ROLE_MEMBER),
    ("bob",    "Bob Seller",       "bob@example.com",    Profile.ROLE_MARKET_SELLER),
    ("carol",  "Carol Organizer",  "carol@example.com",  Profile.ROLE_EVENT_ORGANIZER),
    ("dave",   "Dave Contributor", "dave@example.com",   Profile.ROLE_BOOK_CONTRIBUTOR),
    ("eve",    "Eve Maker",        "eve@example.com",    Profile.ROLE_PROJECT_CREATOR),
    ("frank",  "Frank Commissioner","frank@example.com", Profile.ROLE_COMMISSION_MAKER),
]


class Command(BaseCommand):
    help = "Populate the database with demo data for every app."

    @transaction.atomic
    def handle(self, *args, **options):
        profiles = self._seed_users()
        self._seed_bookclub(profiles)
        self._seed_commissions(profiles)
        self._seed_diyprojects(profiles)
        self._seed_localevents(profiles)
        self._seed_merchstore(profiles)

        self.stdout.write(self.style.SUCCESS("\nSeed complete."))
        self.stdout.write("Demo accounts (password for all: '{}'):".format(DEMO_PASSWORD))
        for username, display, email, role in DEMO_USERS:
            self.stdout.write("  {:8s}  {:20s}  {}".format(username, role, email))

    # ---- users / profiles ----------------------------------------------------

    def _seed_users(self):
        profiles = {}
        for username, display, email, role in DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": email},
            )
            if created:
                user.set_password(DEMO_PASSWORD)
                user.email = email
                user.save()
            profile, _ = Profile.objects.get_or_create(
                user=user,
                defaults={
                    "display_name": display,
                    "email_address": email,
                    "role": role,
                },
            )
            # keep role/display in sync if profile already existed
            updated = False
            if profile.display_name != display:
                profile.display_name = display
                updated = True
            if profile.role != role:
                profile.role = role
                updated = True
            if updated:
                profile.save()
            profiles[username] = profile
        self.stdout.write("Users:        {}".format(len(profiles)))
        return profiles

    # ---- bookclub ------------------------------------------------------------

    def _seed_bookclub(self, profiles):
        genres = {}
        for name, desc in [
            ("Fiction",     "Imaginative narrative works."),
            ("Non-Fiction", "Factual and informational writing."),
            ("Sci-Fi",      "Speculative futures and technology."),
            ("Fantasy",     "Magic, myth, and other worlds."),
            ("Mystery",     "Puzzles, crimes, and clues."),
        ]:
            g, _ = Genre.objects.get_or_create(name=name, defaults={"description": desc})
            genres[name] = g

        contributor = profiles["dave"]
        books_data = [
            ("The Quiet Library",     "Mira Owens",   2018, "Fiction",
             "A librarian uncovers a town's hidden history."),
            ("Iron Sky Protocol",     "Dax Reed",     2022, "Sci-Fi",
             "An orbital station faces a quiet rebellion."),
            ("Roots and Recipes",     "Elena Cruz",   2020, "Non-Fiction",
             "A cook's journey through heirloom ingredients."),
            ("Crown of Cinders",      "Hale Voss",    2019, "Fantasy",
             "A reluctant heir confronts a burning kingdom."),
            ("The Vanishing Tenant",  "Priya Anand",  2021, "Mystery",
             "A flat goes empty overnight and clues vanish too."),
        ]
        books = []
        for title, author, year, genre_name, synopsis in books_data:
            b, _ = Book.objects.get_or_create(
                title=title,
                defaults={
                    "author": author,
                    "publication_year": year,
                    "genre": genres[genre_name],
                    "contributor": contributor,
                    "synopsis": synopsis,
                    "available_to_borrow": True,
                },
            )
            books.append(b)
        self.stdout.write("Books:        {}".format(len(books)))

        # Reviews + bookmarks (a few each)
        reviewers = [profiles["alice"], profiles["eve"], profiles["bob"]]
        for i, book in enumerate(books):
            BookReview.objects.get_or_create(
                book=book,
                user_reviewer=reviewers[i % len(reviewers)],
                title="A solid read",
                defaults={"comment": "Engaging from the first page. Recommended."},
            )
            Bookmark.objects.get_or_create(profile=profiles["alice"], book=book)

        # One borrow record
        Borrow.objects.get_or_create(
            book=books[0],
            borrower=profiles["alice"],
            defaults={
                "name": profiles["alice"].display_name,
                "date_borrowed": date.today(),
                "date_to_return": date.today() + timedelta(weeks=2),
            },
        )

    # ---- commissions ---------------------------------------------------------

    def _seed_commissions(self, profiles):
        types = {}
        for name, desc in [
            ("Art",          "Illustration and visual art commissions."),
            ("Writing",      "Copy, fiction, and editing."),
            ("Music",        "Composition, mixing, and performance."),
            ("Video",        "Editing, motion, and short films."),
            ("Development",  "Software and small tooling."),
        ]:
            t, _ = CommissionType.objects.get_or_create(name=name, defaults={"description": desc})
            types[name] = t

        maker = profiles["frank"]
        commissions_data = [
            ("Album Cover Illustration",  "Art",
             "Hand-drawn cover art for an indie band's debut album.", 2),
            ("Short Story Anthology Edit", "Writing",
             "Line edits for five short stories under 8k words.", 1),
            ("Lo-fi Background Track",    "Music",
             "A 2-minute lo-fi loop for a vlog intro.", 1),
            ("Promo Video Cut",           "Video",
             "30-second promo edit from supplied footage.", 2),
            ("Discord Bot Helper",        "Development",
             "Small Discord bot with role-management commands.", 3),
        ]
        commissions = []
        for title, type_name, desc, people in commissions_data:
            c, _ = Commission.objects.get_or_create(
                title=title,
                defaults={
                    "type": types[type_name],
                    "maker": maker,
                    "description": desc,
                    "people_required": people,
                },
            )
            commissions.append(c)
        self.stdout.write("Commissions:  {}".format(len(commissions)))

        # One job per commission, plus one application
        for c in commissions:
            job, _ = Job.objects.get_or_create(
                commission=c,
                role="Lead {}".format(c.type.name if c.type else "Contributor"),
                defaults={"manpower_required": 1},
            )
            JobApplication.objects.get_or_create(
                job=job,
                applicant=profiles["alice"],
            )

    # ---- diyprojects ---------------------------------------------------------

    def _seed_diyprojects(self, profiles):
        cats = {}
        for name, desc in [
            ("Woodworking",  "Building with wood and joinery."),
            ("Electronics",  "Soldering, microcontrollers, circuits."),
            ("Crafts",       "Paper, fabric, and small handmade items."),
            ("Garden",       "Outdoor and plant-related builds."),
            ("Upcycle",      "Repurposing existing objects."),
        ]:
            c, _ = ProjectCategory.objects.get_or_create(name=name, defaults={"description": desc})
            cats[name] = c

        creator = profiles["eve"]
        projects_data = [
            ("Floating Bookshelf",     "Woodworking",
             "A wall-mounted shelf that hides its brackets.",
             "1x6 board, L-brackets, screws, stain.",
             "Cut, sand, mount brackets, attach board, finish."),
            ("Desk Ambient Light",     "Electronics",
             "USB-powered LED strip controller.",
             "ESP32, WS2812B strip, USB cable, enclosure.",
             "Wire strip, flash firmware, enclose, test."),
            ("Notebook Rebinding",     "Crafts",
             "Convert a worn notebook to a hardcover.",
             "Bookboard, fabric, glue, thread.",
             "Disassemble, prep cover, sew, glue, press."),
            ("Self-Watering Planter",  "Garden",
             "Two-bottle wicking planter for herbs.",
             "2 PET bottles, cotton wick, soil, seedling.",
             "Cut bottles, thread wick, fill, plant."),
            ("Pallet Coffee Table",    "Upcycle",
             "Reclaimed pallet to small coffee table.",
             "Pallet, wheels, screws, finish.",
             "Clean, sand, attach wheels, finish surface."),
        ]
        projects = []
        for title, cat_name, desc, mats, steps in projects_data:
            p, _ = Project.objects.get_or_create(
                title=title,
                defaults={
                    "category": cats[cat_name],
                    "creator": creator,
                    "description": desc,
                    "materials": mats,
                    "steps": steps,
                },
            )
            projects.append(p)
        self.stdout.write("DIY Projects: {}".format(len(projects)))

        # Favorites, reviews, ratings
        for p in projects:
            Favorite.objects.get_or_create(profile=profiles["alice"], project=p)
            ProjectReview.objects.get_or_create(
                project=p,
                reviewer=profiles["bob"],
                defaults={"comment": "Followed the steps — turned out great!"},
            )
            ProjectRating.objects.get_or_create(
                project=p,
                profile=profiles["alice"],
                defaults={"score": 9},
            )

    # ---- localevents ---------------------------------------------------------

    def _seed_localevents(self, profiles):
        types = {}
        for name, desc in [
            ("Workshop",     "Hands-on small-group learning."),
            ("Meetup",       "Casual community gathering."),
            ("Market",       "Pop-up sellers and crafts."),
            ("Performance",  "Music, theatre, or spoken word."),
            ("Talk",         "Lectures and panels."),
        ]:
            t, _ = EventType.objects.get_or_create(name=name, defaults={"description": desc})
            types[name] = t

        organizer = profiles["carol"]
        now = timezone.now()
        events_data = [
            ("Intro to Bookbinding",     "Workshop",   "Community Hall, Room 2",   2,  20),
            ("Coffee + Code Meetup",     "Meetup",     "Brewline Cafe",            5,  40),
            ("Saturday Makers Market",   "Market",     "Riverside Park",           7,  150),
            ("Acoustic Night",           "Performance","Loft 19",                  10, 80),
            ("Talk: Sustainable Design", "Talk",       "Library Auditorium",       14, 60),
        ]
        events = []
        for title, type_name, location, days_ahead, capacity in events_data:
            start = now + timedelta(days=days_ahead, hours=18)
            end = start + timedelta(hours=2)
            ev, created = Event.objects.get_or_create(
                title=title,
                defaults={
                    "category": types[type_name],
                    "description": "Demo seeded event: {}.".format(title),
                    "location": location,
                    "start_time": start,
                    "end_time": end,
                    "event_capacity": capacity,
                    "event_image": "images/placeholder.png",
                },
            )
            if created:
                ev.organizer.add(organizer)
            events.append(ev)
        self.stdout.write("Events:       {}".format(len(events)))

        # A couple of signups
        for ev in events[:3]:
            EventSignup.objects.get_or_create(
                event=ev, user_registrant=profiles["alice"]
            )

    # ---- merchstore ----------------------------------------------------------

    def _seed_merchstore(self, profiles):
        types = {}
        for name, desc in [
            ("Apparel",     "Wearable items."),
            ("Accessories", "Small everyday items."),
            ("Print",       "Posters, prints, zines."),
            ("Sticker",     "Vinyl and paper stickers."),
            ("Home",        "Items for the home."),
        ]:
            t, _ = ProductType.objects.get_or_create(name=name, defaults={"description": desc})
            types[name] = t

        owner = profiles["bob"]
        products_data = [
            ("Common Grounds Tee",   "Apparel",     "Soft cotton tee with logo.",        Decimal("499.00"), 25),
            ("Enamel Pin Set",       "Accessories", "Three-pin set in a kraft sleeve.",  Decimal("249.00"), 50),
            ("Risograph Print A3",   "Print",       "Two-color risograph print.",        Decimal("350.00"), 15),
            ("Sticker Pack (5)",     "Sticker",     "Five vinyl stickers.",              Decimal("120.00"), 100),
            ("Ceramic Mug",          "Home",        "12oz hand-glazed mug.",             Decimal("420.00"), 12),
        ]
        products = []
        for name, type_name, desc, price, stock in products_data:
            p, _ = Product.objects.get_or_create(
                name=name,
                defaults={
                    "product_type": types[type_name],
                    "owner": owner,
                    "description": desc,
                    "price": price,
                    "stock": stock,
                },
            )
            products.append(p)
        self.stdout.write("Products:     {}".format(len(products)))

        # A demo transaction per product
        for p in products:
            Transaction.objects.get_or_create(
                buyer=profiles["alice"],
                product=p,
                defaults={"amount": 1, "status": Transaction.STATUS_DELIVERED},
            )
