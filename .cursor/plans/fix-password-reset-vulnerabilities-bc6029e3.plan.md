<!-- bc6029e3-2893-4a9f-90f6-69e4932c1310 adffc905-1766-4ccc-a1cf-80d3cec7d925 -->
# Solución Vulnerabilidades Password Reset

## Contexto

La plataforma usa autenticación SSO (CAS), por lo que el endpoint `mail_password` no se utiliza. El pentest ha identificado vulnerabilidades de enumeración de usuarios y anti-automatización insuficiente.

## Dos Propuestas

### Propuesta 1: Ocultar/Deshabilitar endpoint (RECOMENDADA para SSO)

Como la plataforma usa SSO y no se utiliza `mail_password`, la solución más simple es ocultarlo completamente devolviendo un error 404 o mensaje de no disponible.

**Archivos a crear/modificar**:

- `src/genweb6.core/src/genweb6/core/browser/password_reset.py`: Vista que sobrescribe `mail_password` y devuelve 404 o mensaje genérico
- `src/genweb6.core/src/genweb6/core/browser/configure.zcml`: Registrar vista con nombre `mail_password` para sobrescribir la de Plone
- Traducciones en `locales/*/LC_MESSAGES/genweb.po` para mensajes

**Implementación**:

- Vista que siempre devuelve HTTP 404 o mensaje genérico sin procesar nada
- No expone información sobre usuarios
- Elimina completamente el vector de ataque

**Ventajas**: Simple, elimina completamente el riesgo, adecuada para SSO

### Propuesta 2: Implementar seguridad completa

Si se necesita mantener la funcionalidad, implementar rate-limiting, CAPTCHA y mensajes unificados.

**Archivos a crear/modificar**:

- `src/genweb6.core/src/genweb6/core/browser/password_reset.py`: Vista con rate-limiting y CAPTCHA
- `src/genweb6.core/src/genweb6/core/utils.py`: Utilidades de rate-limiting por IP
- `src/genweb6.core/src/genweb6/core/browser/views_templates/password_reset.pt`: Template con CAPTCHA integrado
- `src/genweb6.core/src/genweb6/core/profiles/default/registry.xml`: Configuración de límites de rate-limiting

**Implementación**:

- Rate-limiting: 5 intentos cada 10 minutos por IP
- CAPTCHA usando `plone.formwidget.recaptcha` (ya instalado)
- Mensajes unificados: siempre HTTP 200 con mensaje genérico
- Manejo de excepciones sin exponer información

**Ventajas**: Mantiene funcionalidad pero segura, adecuada si se necesita el reset de contraseña

## Decisión

Implementar **Propuesta 2 (seguridad completa)** para que sea reutilizable en otros proyectos Plone 6.

### To-dos

- [ ] Crear utilidad de rate-limiting en utils.py o nuevo archivo rate_limit.py con funciones para gestionar intentos por IP
- [ ] Crear vista SecurePasswordResetView en password_reset.py que implemente rate-limiting, CAPTCHA y respuestas unificadas
- [ ] Registrar la vista personalizada en configure.zcml con nombre mail_password y permisos adecuados
- [ ] Crear template password_reset.pt con formulario y CAPTCHA integrado
- [ ] Añadir configuración de rate-limiting en registry.xml con valores configurables
- [ ] Añadir traducciones para mensajes genéricos en locales (ca, es, en)