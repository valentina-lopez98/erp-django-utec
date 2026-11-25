# Sprint 5 Planning — ERP Django
## Semanas W16–W18 · Espiral 6: Celery e Integraciones

**Sprint Goal:**
Al finalizar el Sprint 5, el ERP ejecutará tareas pesadas de forma
asíncrona con Celery+Redis: correos de confirmación, alertas de
stock bajo y reporte diario de ventas.

## HUs seleccionadas

| ID | Historia | Puntos | Semana |
|---|---|---|---|
| HU-E6-01 | Como dev, quiero infraestructura Celery+Redis funcional | 3 | W16 |
| HU-E6-02 | Como sistema, quiero ejecutar tareas sin bloquear HTTP | 2 | W16 |
| HU-E6-03 | Como cliente, quiero correo de confirmación post-pago | 5 | W17 |
| HU-E6-04 | Como admin, quiero correo cuando el stock es bajo | 3 | W17 |
| HU-E6-05 | Como admin, quiero reporte diario de ventas a las 8 AM | 3 | W18 |
| HU-E6-06 | Como dev, quiero monitorear tareas con Flower | 2 | W16 |

**Total Sprint 5:** 18 puntos

## DoD — Sprint 5
- Logs de Render: worker de Celery embebido "ready" y procesa tareas
- Webhook payment_intent.succeeded → tarea de correo en la cola (no espera)
- Correo de confirmación recibido en < 30 s (W17)
- Alerta de stock enviada cuando stock < umbral (W17)
- Reporte diario ejecutado a las 8:00 AM (W18)
- python manage.py test → ≥ 155 tests OK

## Sprint Backlog — actualización W16

| Tarea | Estado |
|---|---|
| pip install celery redis flower (requirements.txt en UTF-8) | ✅ W16 |
| core/celery.py + core/__init__.py | ✅ W16 |
| CELERY_* en settings.py (Redis en Render · EAGER sin REDIS_URL) | ✅ W16 |
| Key Value (Redis) Free en Render · noeviction | ✅ W16 |
| docker-entrypoint.sh: exec "$@" + worker embebido | ✅ W16 |
| render.yaml: REDIS_URL + CELERY_EMBEDDED_WORKER | ✅ W16 |
| docker-compose.yml con worker + flower (opcional, sin Docker en aula) | ✅ W16 |
| ventas/tasks.py (2 tareas placeholder) | ✅ W16 |
| webhook: .delay() con try/except (único disparo) | ✅ W16 |
| Worker embebido "ready" en logs de Render | ✅ W16 |
| SendGrid correo transaccional real | ⏳ W17 |
| Alerta de stock bajo por correo | ⏳ W17 |
| Celery Beat + tareas programadas | ⏳ W18 |

## Sprint 5 — Estado final W18

| HU | Historia | Estado | Pts |
|---|---|---|---|
| HU-E6-01 | Infraestructura Celery+Redis funcional | ✅ Completada | 3 |
| HU-E6-02 | Tareas sin bloquear HTTP | ✅ Completada | 2 |
| HU-E6-03 | Correo de confirmación post-pago | ✅ Completada | 5 |
| HU-E6-04 | Correo de alerta de stock bajo | ✅ Completada | 3 |
| HU-E6-05 | Reporte diario de ventas al cierre del día (21:00) | ✅ Completada | 3 |
| HU-E6-06 | Monitorear tareas (Logs del worker; Flower instalado, no expuesto en Render Free) | ✅ Completada | 2 |
| **Total** | | | **18/18** |

## Sprint Backlog — actualización W18

| Tarea | Estado |
|---|---|
| reporte_ventas_diario: annotate + Sum(F('cantidad') * F('precio_unitario')) | ✅ W18 |
| Top 5 incluye compras en línea (Pedido.items_snapshot) | ✅ W18 |
| Templates reporte_ventas.html + .txt (KPIs + tabla) | ✅ W18 |
| CELERY_BEAT_SCHEDULE: reporte crontab(REPORTE_DIARIO_HORA, default 21:00) + stock timedelta(hours=1) | ✅ W18 |
| Hora configurable REPORTE_DIARIO_HORA (Render: 10:00 para pruebas) | ✅ W18 |
| Beat embebido en el worker de Render (--beat, CELERY_EMBEDDED_BEAT=1) | ✅ W18 |
| Fix kombu 5.7.0 → 5.3.7 (VersionMismatch con redis 5.0.1) | ✅ W18 |
| Acción admin "Enviar correo de confirmación" (pagados sin correo) | ✅ W18 |
| Suite completa en verde | ✅ W18 |

## Hito M6 — ALCANZADO ✅
- Worker: embebido en el contenedor web de Render (`--pool=solo`)
- Beat: embebido en el worker (`--beat`), una sola instancia
- Correo: enviar_confirmacion_pedido → solo desde el webhook, idempotente
- Alerta: verificar_stock_bajo → cada hora, correo al admin
- Reporte: crontab(REPORTE_DIARIO_HORA) → 21:00 hora de México por defecto
  (configurable con REPORTE_DIARIO_HORA)
- Tests: Ran 171 tests → OK (2 skipped: PDF requiere GTK, corre en Docker/Render)
- Fecha: 20/Noviembre/2026

### Observaciones de verificación (2026-11-20)
- Laboratorio sin Docker Desktop: Redis, worker, Beat y Flower solo
  existen en Render; localmente todo corre en modo EAGER.
- En Render el correo no llegaba por `kombu==5.7.0` + `redis==5.0.1`
  (VersionMismatch). Corregido; confirmar en los Logs tras el despliegue.
- Render Free se duerme sin tráfico: Beat solo dispara si el servicio
  está despierto (ping externo cada 10 min).
- Flower (HU-E6-06) está instalado (`flower==2.0.1`), pero no se expone
  en Render Free: en producción se monitorea con los Logs del worker.