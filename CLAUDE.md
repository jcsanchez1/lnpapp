# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django 5.1.4 application for the **Laboratorio Nacional de Parasitología (LNP)** in Honduras. It manages parasitological sample analysis with a three-tier role-based access system (National, Regional, Center) covering 20 health regions across 18 departments.

**Core Domain**: Laboratory information management system tracking patient records (expedientes), parasitological samples (muestras), and epidemiological data across Honduras' health network.

## Development Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Running the Application
```bash
# Start development server
python manage.py runserver

# Access admin interface
# http://localhost:8000/admin/
```

### Data Initialization
```bash
# Initialize base data (roles, regions, centers)
python manage.py inicializar_datos

# Load Honduras departments and municipalities (298 municipalities, 18 departments)
python manage.py cargar_departamentos_municipios

# Create 20 health regions (18 departmental + 2 metropolitan)
python manage.py crear_20_regiones

# Generate epidemiological weeks
python manage.py generar_semanas

# Create test data
python manage.py crear_datos_prueba
python manage.py crear_muestras
```

### Migrations
```bash
# After model changes, create and apply migrations
python manage.py makemigrations
python manage.py migrate
```

## Architecture Overview

### Three-Tier Role System
The system implements strict geographic access control:

1. **LNP (National)** - Full access to all regions and data, can generate national reports
2. **REG (Regional)** - Access limited to assigned region's centers and data
3. **CAT (Center)** - Access limited to assigned health center only

**Critical**: The `Profile` model enforces geographic assignment via `clean()` validation:
- LNP users must NOT have region or center assigned
- REG users must have region only (no center)
- CAT users must have center (region auto-assigned from center)

### Geographic Hierarchy
```
Departamento (18 total)
  └─ Municipio (298 total, using ChainedForeignKey)
       └─ Region (20: 18 departmental + 2 metropolitan)
            └─ CentroAtencion (health centers)
                 └─ Expediente (patient records with DNI)
                      └─ Muestra (samples with 21 parasite fields)
```

### Data Model Relationships

**Core Models** (in `examen/models.py`):
- `Expediente`: Patient records with mandatory DNI (format: 0801-1990-12345). One expediente per patient, tracks demographics and location
- `Muestra`: Parasitological samples. Automatically calculates `resultado` (POS/NEG) based on 21 parasite fields
- `SemanaEpidemiologica`: Epidemiological weeks (ISO 8601) with cached statistics updated via signals
- `Profile`: User profile with role and geographic assignment. Uses `django-smart-selects` for cascading dropdowns

**Important**: `Muestra.save()` automatically:
1. Calculates `resultado` from parasite fields
2. Assigns `semana_epidemiologica` from `fecha_examen`
3. Populates denormalized fields (`semana_numero`, `año_epidemiologico`) for query performance

### Signal Behavior

`examen/signals.py` handles:
- Auto-creation of `Profile` when `User` is created (defaults to CAT role)
- Real-time updates of `SemanaEpidemiologica` cached statistics when `Muestra` is saved/deleted

### URL Structure

Main URL configuration in `lnpapp/urls.py` includes:
- `/admin/` - Django admin
- `/chaining/` - django-smart-selects AJAX endpoints (required for cascading dropdowns)
- `/` - Main app URLs from `examen.urls`

Dashboard views in `examen/views/dashboard_views.py`:
- `dashboard_nacional()` - National dashboard for LNP users
- `dashboard_regional()` - Regional dashboard for REG users
- `dashboard_centro()` - Center dashboard for CAT users

Each dashboard filters data based on user's role and geographic assignment.

## Key Implementation Details

### Parasite Fields
`Muestra` model tracks 21 parasites across 4 categories:
- **Protozoos**: Amebas (5), Flagelados (3), Ciliados (1)
- **Coccidios**: 3 species + Blastocystis
- **Helmintos - Nematodos**: 6 species (including Ascaris with intensity field)
- **Helmintos - Cestodos**: 3 species

Each has stage choices (Trofozoíto, Quiste, Huevos, Larva, etc.). Result is automatically calculated as POS if ANY parasite field has a value.

### ChainedForeignKey Usage
Uses `django-smart-selects` for cascading dropdowns:
- `Profile.centro_atencion` chains to `Profile.region`
- `Expediente.municipio` chains to `Expediente.departamento`

**Important**: In admin, users must select parent field (region/department) BEFORE child field (center/municipality) appears.

### Data Migration Pattern
The codebase includes a migration from text-based to FK-based location fields:
- Old fields: `departamento_old`, `municipio_old` (CharField, read-only)
- New fields: `departamento`, `municipio` (ForeignKey, ChainedForeignKey)
- Migration commands: `preparar_migracion_expedientes.py`, `migrar_expedientes.py`

### Performance Optimizations
- Denormalized week/year fields on `Muestra` for query performance (avoids JOINs)
- Cached statistics on `SemanaEpidemiologica` updated via signals
- Database indexes on frequently queried fields (DNI, dates, results)

## Database Notes

Currently using SQLite (`db.sqlite3`) for development. Settings include PostgreSQL support (`psycopg2-binary`) for production deployment.

## Frontend & Templates

Templates in `examen/templates/`:
- Uses Bootstrap 5 (`crispy-bootstrap5` for forms)
- Dashboard templates for each role level
- Template tags in `examen/templatetags/dashboard_extras.py`

Static files in `examen/static/` include GeoJSON for Honduras map visualization.

## Testing & Data Generation

Management commands for generating test data:
- `crear_datos_prueba` - Creates sample expedientes
- `crear_muestras` - Generates sample parasitological results
- Use these to populate development database with realistic data

## Dependencies

Key third-party packages:
- `django-smart-selects==1.6.0` - Cascading dropdowns (CRITICAL for UX)
- `djangorestframework==3.14.0` - API framework (may be for future API)
- `django-crispy-forms` + `crispy-bootstrap5` - Form rendering
- `openpyxl`, `pandas`, `reportlab`, `pillow` - Export/reporting functionality

## Common Gotchas

1. **Profile Assignment**: Always validate geographic assignment matches role level. Use `Profile.clean()` validation.

2. **ChainedForeignKey**: Parent field must be saved before child field appears. In forms, use AJAX endpoint at `/chaining/`.

3. **Automatic Calculation**: `Muestra.resultado` is calculated automatically - never set manually. It's marked `editable=False`.

4. **Epidemiological Weeks**: Use `SemanaEpidemiologica.obtener_o_crear_desde_fecha()` to ensure weeks exist before assigning to samples.

5. **Signal Recursion**: Be careful when modifying `Muestra` or `SemanaEpidemiologica` in signals to avoid infinite loops.

6. **DNI Format**: Expediente DNI must match regex `^\d{4}-\d{4}-\d{5}$` (e.g., 0801-1990-12345).

7. **20 vs 21 Parasites**: The system tracks 21 total parasite fields but "20 parásitos" appears in comments/variable names because one field tracks infection intensity, not a separate organism.
