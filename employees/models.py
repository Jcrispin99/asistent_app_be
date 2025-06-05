from django.db import models
from django.core.validators import RegexValidator
from companies.models import Company
from departments.models import Department
from positions.models import Position
from datetime import date

# Opciones para turnos y días de descanso
SHIFT_TYPES = [
    ('turno_1', 'Turno 1'),
    ('turno_2', 'Turno 2'),
    ('turno_3', 'Turno 3'),
    ('turno_4', 'Turno 4'),
]

REST_DAYS = [
    ('lunes', 'Lunes'),
    ('martes', 'Martes'),
    ('miercoles', 'Miércoles'),
    ('jueves', 'Jueves'),
    ('viernes', 'Viernes'),
    ('sabado', 'Sábado'),
    ('domingo', 'Domingo'),
]

class Employee(models.Model):
    nombres = models.CharField(max_length=70, verbose_name='Nombres')
    apellidos = models.CharField(max_length=70, verbose_name='Apellidos')
    dni_validator = RegexValidator(
        regex=r'^\d{8}$',
        message='El DNI debe tener 8 dígitos numéricos.'
    )
    dni = models.CharField(max_length=8, validators=[dni_validator], unique=True, verbose_name='DNI')
    fecha_nacimiento = models.DateField(verbose_name='Fecha de Nacimiento')
    telefono = models.CharField(max_length=15, verbose_name='Teléfono', blank=True, null=True)
    email_personal = models.EmailField(blank=True, null=True, verbose_name='Correo Personal')
    #email_empresa = models.EmailField(blank=True, null=True, verbose_name='Correo Empresa')
    direccion = models.CharField(max_length=255, blank=True, null=True, verbose_name='Dirección')
    codigo_empleado = models.CharField(max_length=20, unique=True, verbose_name='Código de Empleado')
    fecha_ingreso = models.DateField(verbose_name='Fecha de Ingreso')
    salario_actual = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Salario Actual')
    empresa = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Empresa')
    departamento = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='Departamento')
    cargo = models.ForeignKey(Position, on_delete=models.CASCADE, verbose_name='Cargo')
    
    # Nuevos campos para horarios y asistencia
    shift_type = models.CharField(
        max_length=20, 
        choices=SHIFT_TYPES, 
        verbose_name="Tipo de Turno",
        default='turno_1'
    )
    rest_day = models.CharField(
        max_length=20, 
        choices=REST_DAYS, 
        verbose_name="Día de Descanso",
        default='domingo'
    )
    
    foto = models.ImageField(upload_to='employee/fotos/', blank=True, null=True, verbose_name='Foto')
    firma = models.ImageField(upload_to='employee/firmas/', blank=True, null=True, verbose_name='Firma')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_cese = models.DateField(blank=True, null=True, verbose_name='Fecha de Cese')
    motivo_cese = models.TextField(blank=True, null=True, verbose_name='Motivo de Cese')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering = ['nombres', 'apellidos']
        unique_together = ['empresa', 'codigo_empleado']
        
    def __str__(self):
        return f"{self.apellidos}, {self.nombres} ({self.codigo_empleado})"

    @property
    def nombre_completo(self):
        """Retorna el nombre completo del empleado"""
        return f"{self.nombres} {self.apellidos}"
    
    def get_edad(self):
        """Calcula la edad del empleado"""
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )
    
    get_edad.short_description = "Edad"
    
    def get_antiguedad(self):
        """Calcula los años de antigüedad en la empresa"""
        if self.fecha_cese:
            fecha_fin = self.fecha_cese
        else:
            fecha_fin = date.today()
        
        years = fecha_fin.year - self.fecha_ingreso.year
        if (fecha_fin.month, fecha_fin.day) < (self.fecha_ingreso.month, self.fecha_ingreso.day):
            years -= 1
        return years
    
    get_antiguedad.short_description = "Antigüedad (años)"
    
    def get_email_corporativo(self):
        """Genera el email corporativo basado en el nombre"""
        if self.empresa.email:
            domain = self.empresa.email.split('@')[1]
            nombre_usuario = f"{self.nombres.split()[0].lower()}.{self.apellidos.split()[0].lower()}"
            return f"{nombre_usuario}@{domain}"
        return None
    
    get_email_corporativo.short_description = "Email Corporativo"
    
    # Nuevos métodos para horarios
    def get_shift_display_extended(self):
        """Retorna información extendida del turno"""
        return f"{self.get_shift_type_display()} - Descanso: {self.get_rest_day_display()}"
    
    get_shift_display_extended.short_description = "Horario Completo"
    
    def trabaja_hoy(self, fecha=None):
        """Verifica si el empleado trabaja en una fecha específica"""
        if fecha is None:
            fecha = date.today()
        
        # Obtener el día de la semana (0=lunes, 6=domingo)
        dia_semana = fecha.weekday()
        dias_semana = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        dia_nombre = dias_semana[dia_semana]
        
        # Verificar si es su día de descanso
        return dia_nombre != self.rest_day
    
    def clean(self):
        """Validaciones personalizadas"""
        from django.core.exceptions import ValidationError
        
        # Validar que la fecha de nacimiento sea coherente
        if self.fecha_nacimiento:
            edad = self.get_edad()
            if edad < 18:
                raise ValidationError('El empleado debe ser mayor de edad (18 años)')
            if edad > 70:
                raise ValidationError('La edad del empleado parece incorrecta')
        
        # Validar que la fecha de ingreso no sea futura
        if self.fecha_ingreso and self.fecha_ingreso > date.today():
            raise ValidationError('La fecha de ingreso no puede ser futura')
        
        # Validar que la fecha de salida sea posterior al ingreso
        if self.fecha_cese and self.fecha_ingreso:
            if self.fecha_cese <= self.fecha_ingreso:
                raise ValidationError('La fecha de salida debe ser posterior a la fecha de ingreso')
        
        # Validar que el departamento pertenezca a la empresa
        if self.departamento and self.empresa:
            if self.departamento.empresa != self.empresa:
                raise ValidationError('El departamento debe pertenecer a la empresa seleccionada')
        
        # Validar que el cargo pertenezca al departamento
        if self.cargo and self.departamento:
            if self.cargo.departamento != self.departamento:
                raise ValidationError('El cargo debe pertenecer al departamento seleccionado')