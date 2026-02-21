# 📊 Diagramas del Sistema - Arte Ideas

Este directorio contiene los diagramas UML que representan la arquitectura completa del sistema de gestión para estudios fotográficos "Arte Ideas".

## 📁 Archivos de Diagramas

### 1. 🏗️ [diagrama-clases.puml](./diagrama-clases.puml)
**Diagrama de Clases Completo**
- Muestra todos los modelos de datos de las 6 aplicaciones Django
- Incluye atributos, tipos de datos y relaciones
- Organizado por colores según la aplicación (Core, CRM, Commerce, Operations, Finance, Analytics)
- Refleja la implementación real del frontend React

**Características principales:**
- ✅ Multi-tenancy con modelo `Tenant`
- ✅ 5 roles específicos del estudio fotográfico
- ✅ Modelos con campos en español según frontend
- ✅ Relaciones correctas entre aplicaciones

### 2. 🏛️ [diagrama-arquitectura.puml](./diagrama-arquitectura.puml)
**Diagrama de Arquitectura de Aplicaciones**
- Muestra la relación entre frontend React y backend Django
- Mapeo de módulos frontend a aplicaciones backend
- Dependencias entre aplicaciones
- Servicios externos (PostgreSQL, Redis, etc.)

**Elementos clave:**
- ✅ 12 módulos frontend → 6 aplicaciones backend
- ✅ Dependencias correctas entre apps
- ✅ Servicios de infraestructura
- ✅ Flujo de datos entre capas

### 3. 🔄 [diagrama-flujo-negocio.puml](./diagrama-flujo-negocio.puml)
**Diagrama de Flujo de Negocio**
- Proceso completo del estudio fotográfico
- Desde contacto inicial hasta entrega final
- Incluye decisiones y validaciones del negocio
- Organizado por aplicaciones (swimlanes)

**Flujo típico:**
1. **CRM**: Cliente contacta → Agenda cita → Contrato (si aplica)
2. **Commerce**: Pedido → Consulta materiales → Validación stock
3. **Operations**: Desarrollo/elaboración → Asignación equipos → Entrega
4. **Finance**: Pagos → Gastos operativos
5. **Analytics**: Métricas → Dashboard

## 🛠️ Cómo Visualizar los Diagramas

### Opción 1: PlantUML Online
1. Visita [PlantUML Online Server](http://www.plantuml.com/plantuml/uml/)
2. Copia el contenido de cualquier archivo `.puml`
3. Pega en el editor y visualiza

### Opción 2: VS Code Extension
1. Instala la extensión "PlantUML" en VS Code
2. Abre cualquier archivo `.puml`
3. Usa `Ctrl+Shift+P` → "PlantUML: Preview Current Diagram"

### Opción 3: PlantUML Local
```bash
# Instalar PlantUML
npm install -g node-plantuml

# Generar imagen
puml generate diagrama-clases.puml --png
```

## 🎯 Contexto del Negocio Reflejado

### Estudio Fotográfico "Arte Ideas"
Los diagramas reflejan las características específicas del negocio:

#### 🏢 **Multi-tenancy**
- Cada estudio fotográfico es un tenant independiente
- Aislamiento completo de datos entre tenants
- Configuración personalizable por tenant

#### 👥 **Roles Específicos**
- **admin**: Administrador del sistema
- **manager**: Gerente del estudio  
- **employee**: Empleado general
- **photographer**: Fotógrafo especializado
- **assistant**: Asistente administrativo

#### 📦 **Inventario Manual**
- No hay actualización automática de stock
- Personal registra materiales manualmente
- Alertas de stock bajo configurables

#### 🔧 **Desarrollo de Pedidos**
- "Producción" = Desarrollo/elaboración de pedidos del cliente
- Proceso: Pedido → Desarrollo → Entrega
- Uso de activos (equipos) sin consumo

#### 💰 **Gestión Financiera**
- Gastos de personal (nómina)
- Gastos de servicios (alquiler, servicios públicos)
- Control de pagos y adelantos

## 📋 Validación con Frontend

Los diagramas están **100% validados** con el código frontend React existente:

- ✅ Nombres de campos exactos (`nombre`, `contacto`, `direccion`)
- ✅ Estados y opciones idénticas
- ✅ Servicios fotográficos específicos
- ✅ Categorías de inventario reales
- ✅ Flujo de negocio implementado

## 🔄 Actualización de Diagramas

Para mantener los diagramas actualizados:

1. **Cambios en modelos**: Actualizar `diagrama-clases.puml`
2. **Nuevas aplicaciones**: Actualizar `diagrama-arquitectura.puml`
3. **Cambios en flujo**: Actualizar `diagrama-flujo-negocio.puml`

## 📚 Referencias

- [Documentación de Arquitectura](./arquitectura-sistema.md)
- [Aplicaciones Backend](./aplicaciones-backend.md)
- [Compatibilidad Frontend](./compatibilidad-frontend.md)
- [Plan de Desarrollo](./plan-desarrollo-sprint.md)

---
*Diagramas generados para el sistema de gestión de estudios fotográficos "Arte Ideas"*