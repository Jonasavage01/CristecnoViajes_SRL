# Sistema de Permisos

## Roles Disponibles
- **Administrador**: Acceso completo al sistema
- **Gestor de Clientes**: 
  - Crear/Editar clientes
  - Gestionar documentos
- **Gestor de Reservas**:
  - Crear/Modificar reservas
  - Generar reportes

## Implementación Técnica

### Mixins de Acceso
```python
from core.mixins import RoleAccessMixin

class MiVista(RoleAccessMixin, View):
    allowed_roles = ['admin', 'gestor']