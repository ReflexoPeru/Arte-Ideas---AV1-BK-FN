"""
Comando de Django para configurar tenant y asignarlo a usuarios
Uso: python manage.py setup_tenant --username usuario --tenant-id 1
     python manage.py setup_tenant --username usuario --create-tenant
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.core.multitenancy.models import Tenant

User = get_user_model()


class Command(BaseCommand):
    help = 'Configurar tenant para un usuario o crear un tenant nuevo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Nombre de usuario al que asignar el tenant',
        )
        parser.add_argument(
            '--tenant-id',
            type=int,
            help='ID del tenant a asignar',
        )
        parser.add_argument(
            '--create-tenant',
            action='store_true',
            help='Crear un nuevo tenant y asignarlo al usuario',
        )
        parser.add_argument(
            '--list-tenants',
            action='store_true',
            help='Listar todos los tenants disponibles',
        )
        parser.add_argument(
            '--list-users',
            action='store_true',
            help='Listar todos los usuarios sin tenant',
        )

    def handle(self, *args, **options):
        # Listar tenants
        if options['list_tenants']:
            tenants = Tenant.objects.all()
            if tenants.exists():
                self.stdout.write(self.style.SUCCESS(f'\nTenants disponibles ({tenants.count()}):'))
                for tenant in tenants:
                    users_count = User.objects.filter(tenant=tenant).count()
                    self.stdout.write(
                        f'  ID: {tenant.id} - {tenant.name} (slug: {tenant.slug}) - '
                        f'Usuarios: {users_count} - Activo: {tenant.is_active}'
                    )
            else:
                self.stdout.write(self.style.WARNING('\nNo hay tenants en la base de datos.'))
                self.stdout.write(self.style.SUCCESS('Usa --create-tenant para crear uno nuevo.'))
            return

        # Listar usuarios sin tenant
        if options['list_users']:
            users = User.objects.filter(tenant__isnull=True)
            if users.exists():
                self.stdout.write(self.style.WARNING(f'\nUsuarios sin tenant ({users.count()}):'))
                for user in users:
                    self.stdout.write(
                        f'  ID: {user.id} - {user.username} (email: {user.email}) - '
                        f'Rol: {user.role}'
                    )
            else:
                self.stdout.write(self.style.SUCCESS('\nTodos los usuarios tienen tenant asignado.'))
            return

        # Crear tenant
        if options['create_tenant']:
            if not options['username']:
                self.stdout.write(self.style.ERROR('Error: --username es requerido cuando usas --create-tenant'))
                return

            try:
                user = User.objects.get(username=options['username'])
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Error: Usuario "{options["username"]}" no existe'))
                return

            # Verificar si el usuario ya tiene tenant
            if user.tenant:
                self.stdout.write(
                    self.style.WARNING(
                        f'\nEl usuario "{user.username}" ya tiene un tenant asignado:\n'
                        f'  Tenant ID: {user.tenant.id}\n'
                        f'  Nombre: {user.tenant.name}\n'
                        f'  Slug: {user.tenant.slug}\n'
                    )
                )
                return

            # Generar slug único
            base_slug = f'estudio-{user.username}'
            slug = base_slug
            counter = 1
            while Tenant.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1

            # Crear tenant
            tenant = Tenant.objects.create(
                name=f'Estudio {user.username}',
                slug=slug,
                business_name=f'Estudio Fotográfico {user.username}',
                business_address='Dirección por definir',
                business_phone='999999999',
                business_email=user.email or f'{user.username}@example.com',
                business_ruc='12345678901',
                is_active=True
            )

            # Asignar tenant al usuario
            user.tenant = tenant
            user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n[OK] Tenant creado y asignado exitosamente!\n'
                    f'  Tenant ID: {tenant.id}\n'
                    f'  Nombre: {tenant.name}\n'
                    f'  Slug: {tenant.slug}\n'
                    f'  Usuario: {user.username}\n'
                )
            )
            return

        # Asignar tenant existente a usuario
        if options['username'] and options['tenant_id']:
            try:
                user = User.objects.get(username=options['username'])
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Error: Usuario "{options["username"]}" no existe'))
                return

            try:
                tenant = Tenant.objects.get(id=options['tenant_id'])
            except Tenant.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Error: Tenant con ID {options["tenant_id"]} no existe'))
                self.stdout.write(self.style.WARNING('Usa --list-tenants para ver tenants disponibles'))
                return

            user.tenant = tenant
            user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n[OK] Tenant asignado exitosamente!\n'
                    f'  Usuario: {user.username}\n'
                    f'  Tenant: {tenant.name} (ID: {tenant.id})\n'
                )
            )
            return

        # Si no se proporcionaron opciones, mostrar ayuda
        self.stdout.write(self.style.WARNING('\nOpciones disponibles:'))
        self.stdout.write('  --list-tenants          Listar todos los tenants')
        self.stdout.write('  --list-users            Listar usuarios sin tenant')
        self.stdout.write('  --username USER --create-tenant    Crear tenant y asignarlo al usuario')
        self.stdout.write('  --username USER --tenant-id ID     Asignar tenant existente al usuario')
        self.stdout.write('\nEjemplos:')
        self.stdout.write('  python manage.py setup_tenant --list-tenants')
        self.stdout.write('  python manage.py setup_tenant --list-users')
        self.stdout.write('  python manage.py setup_tenant --username ruiz --create-tenant')
        self.stdout.write('  python manage.py setup_tenant --username ruiz --tenant-id 1')

