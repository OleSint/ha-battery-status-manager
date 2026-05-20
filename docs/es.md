# Battery Status Manager — Documentación (Español)

> **Volver a:** [README](../README.md) | [EN](en.md) | [DE](de.md) | [FR](fr.md) | [NL](nl.md)

---

## Tabla de contenidos

1. [¿Qué hace esta integración?](#1-qué-hace-esta-integración)
2. [Requisitos](#2-requisitos)
3. [Instalación](#3-instalación)
4. [Configuración inicial](#4-configuración-inicial)
5. [Ámbito de supervisión](#5-ámbito-de-supervisión)
6. [Umbrales](#6-umbrales)
7. [Notificaciones](#7-notificaciones)
8. [Informe semanal](#8-informe-semanal)
9. [Cambiar la configuración más adelante](#9-cambiar-la-configuración-más-adelante)
10. [Cómo funcionan las notificaciones (detalles técnicos)](#10-cómo-funcionan-las-notificaciones-detalles-técnicos)
11. [Solución de problemas](#11-solución-de-problemas)

---

## 1. ¿Qué hace esta integración?

Battery Status Manager supervisa todos los dispositivos alimentados por batería en su Home Assistant y le notifica cuando es necesaria alguna acción. Está diseñada para configurarse una sola vez y luego funcionar silenciosamente en segundo plano.

Funciones principales:

- Envía una **advertencia** cuando una batería baja de un nivel configurable (ej. 20 %).
- Envía una **alerta crítica** cuando una batería alcanza un nivel peligrosamente bajo (ej. 10 %).
- Detecta un **drenaje rápido** (ej. pérdida de 20 % en 24 horas) y le avisa de inmediato.
- Incluye una **previsión de agotamiento** en cada notificación — la integración estima cuántos días quedan hasta que la batería se agote, basándose en la tasa de drenaje medida.
- Envía **recordatorios** a intervalos configurables si una batería sigue baja.
- Genera opcionalmente un **informe de resumen semanal** el día y a la hora que usted elija.
- Respeta una **ventana de tiempo** y **días activos**, para no ser molestado a las 3 de la madrugada.

---

## 2. Requisitos

- Home Assistant **2023.6** o posterior.
- Al menos un **servicio de notificación** configurado en Home Assistant (ej. la aplicación móvil oficial, un bot de Telegram o un notificador de correo electrónico). Estos aparecen como `notify.su_servicio` en Home Assistant.

---

## 3. Instalación

### A través de HACS (recomendado)

HACS es el Home Assistant Community Store. Si aún no lo tiene, siga la [guía de instalación de HACS](https://hacs.xyz/docs/use/download/download/).

1. Abra HACS en la barra lateral de Home Assistant.
2. Vaya a **Integraciones**.
3. Haga clic en el menú de tres puntos (⋮) en la esquina superior derecha y elija **Repositorios personalizados**.
4. Pegue `https://github.com/OleSint/ha-battery-status-manager` y seleccione **Integración** como categoría. Haga clic en **Añadir**.
5. Cierre el diálogo. Busque **Battery Status Manager** en la lista de integraciones de HACS.
6. Haga clic en él y luego en **Descargar** (inferior derecho).
7. **Reinicie Home Assistant** (Configuración → Sistema → Reiniciar).

### Instalación manual

1. Descargue el ZIP de la última versión desde [GitHub Releases](https://github.com/OleSint/ha-battery-status-manager/releases).
2. Descomprímalo y copie la carpeta `custom_components/battery_status_manager` en el directorio `config/custom_components/` de su instalación de Home Assistant.
3. Reinicie Home Assistant.

---

## 4. Configuración inicial

Tras reiniciar:

1. Vaya a **Configuración → Dispositivos y servicios**.
2. Haga clic en **+ Añadir integración** (inferior derecho).
3. Busque **Battery Status Manager** y haga clic en él.
4. Siga el asistente de configuración (4 pasos, descritos a continuación).

---

## 5. Ámbito de supervisión

El primer paso del asistente le permite elegir qué baterías supervisar.

### Opción A — Todas las baterías

Supervisa todas las entidades de Home Assistant con la clase de dispositivo `battery`. Es la opción más sencilla e incluye automáticamente los nuevos dispositivos que añada posteriormente.

Tras elegir "Todas", puede opcionalmente **excluir** entidades específicas (por ejemplo, un sensor de batería defectuoso que siempre muestra 0 %).

### Opción B — Por dispositivo

Verá una lista de todos los dispositivos que tienen al menos una entidad de batería. Seleccione uno o varios dispositivos. Solo se supervisan las entidades de batería de los dispositivos seleccionados.

### Opción C — Por entidad

Verá una lista de todas las entidades de batería en Home Assistant. Seleccione exactamente cuáles supervisar.

---

## 6. Umbrales

### Umbral de advertencia (⚠️)

- **Activar advertencia de batería baja** — Active esto para recibir una notificación cuando una batería baje del nivel de advertencia.
- **Umbral de advertencia (%)** — El porcentaje por debajo del cual se envía una advertencia. Valor predeterminado: 20 %.

### Umbral crítico (🚨)

- **Activar alerta crítica de batería** — Active esto para recibir una segunda notificación más urgente a un nivel muy bajo.
- **Umbral crítico (%)** — Debe ser menor que el umbral de advertencia. Valor predeterminado: 10 %.

### Detección de drenaje rápido

- **Activar notificación de drenaje rápido** — Active esto para ser alertado ante un drenaje inusualmente rápido.
- **Umbral de drenaje (%)** — Cuántos puntos porcentuales de pérdida disparan una alerta. Ejemplo: 20 %.
- **Ventana de observación (horas)** — A lo largo de cuántas horas se mide la pérdida. Ejemplo: 24 horas.

---

## 7. Notificaciones

### Servicios de notificación

Seleccione qué servicios `notify.*` deben recibir las notificaciones. Puede seleccionar varios. Se requiere al menos uno.

### Título de la notificación

El título que aparece en las notificaciones push o correos electrónicos. Predeterminado: `Battery Status Manager`.

### Ventana de tiempo (opcional)

Active esto para restringir las notificaciones a un rango horario específico.

- **Inicio de la ventana de tiempo** — Hora más temprana en que puede enviarse una notificación. Ejemplo: `08:00`.
- **Fin de la ventana de tiempo** — Hora más tardía. Ejemplo: `20:00`.

Las ventanas nocturnas funcionan correctamente: inicio `22:00` y fin `07:00` permite notificaciones entre las 22:00 y las 7:00 horas.

> Las notificaciones suprimidas por estar fuera de la ventana de tiempo **no se ponen en cola** — simplemente se omiten.

### Días activos (opcional)

Elija los días de la semana en los que se pueden enviar notificaciones. Por defecto, los siete días están activos.

### Recordatorio (opcional)

- **Activar recordatorio** — Si una batería sigue bajo el umbral tras la primera notificación, se envía un recordatorio después del intervalo configurado.
- **Intervalo de recordatorio (horas)** — Con qué frecuencia se repite el recordatorio. Ejemplo: 24 horas.

---

## 8. Informe semanal

El informe semanal es completamente opcional. Cuando está activado, la integración envía un resumen una vez por semana.

- **Activar informe semanal** — Activa el informe.
- **Día de la semana para el informe** — Qué día se envía el informe (ej. lunes).
- **Hora para el informe** — A qué hora (ej. 09:00).

### Contenido del informe

- Número total de baterías supervisadas.
- Número de baterías actualmente por debajo del umbral de advertencia.
- Número de baterías actualmente por debajo del umbral crítico.
- Número de baterías que se han recuperado o reemplazado en los últimos 7 días.
- Previsión de 7 días: baterías actualmente por encima del umbral pero que se espera que bajen en los próximos 7 días.

El informe se envía como máximo una vez por período de 7 días.

---

## 9. Cambiar la configuración más adelante

Todas las configuraciones se pueden cambiar en cualquier momento:

1. Vaya a **Configuración → Dispositivos y servicios**.
2. Encuentre la tarjeta **Battery Status Manager**.
3. Haga clic en **Configurar**.
4. Recorra el asistente de nuevo — sus valores anteriores están pre-rellenados.

---

## 10. Cómo funcionan las notificaciones (detalles técnicos)

### Intervalo de comprobación

La integración comprueba todos los niveles de batería cada **60 minutos**.

### Una notificación por nivel

Cuando tanto la advertencia como la alerta crítica están activadas, la integración envía únicamente **una** notificación por ciclo de comprobación — nunca ambas al mismo tiempo:

- Batería por debajo del **umbral crítico** → solo se envía la alerta 🚨 crítica. La advertencia se suprime, porque la alerta crítica ya transmite la información más urgente.
- Batería por debajo del **umbral de advertencia** pero por encima del crítico → solo se envía la ⚠️ advertencia.

### Histéresis

Para evitar notificaciones repetidas por el mismo evento:

- Una batería por debajo del **umbral de advertencia** dispara una advertencia. No disparará otra hasta que primero se recupere por encima de `umbral de advertencia + 5 %`.
- Una batería por debajo del **umbral crítico** dispara una alerta crítica. No disparará otra hasta que primero se recupere por encima de `umbral crítico + 3 %`.

Ejemplo: umbral de advertencia = 20 %, umbral crítico = 10 %. Una batería al 8 % solo dispara una alerta crítica. No disparará otra alerta crítica hasta que suba por encima del 13 % y luego vuelva a bajar del 10 %. Si se recupera al 12 % (por encima del crítico pero aún por debajo de la advertencia), en ese momento se envía una advertencia.

### Previsión de agotamiento

La integración almacena un historial de lecturas de batería. Con al menos 3 puntos de datos durante al menos 2 horas, calcula una tasa de drenaje lineal y extrapola cuántos días quedan hasta el agotamiento.

### Almacenamiento de datos

Todos los datos de estado se almacenan en el archivo `.storage/battery_status_manager` de Home Assistant y persisten tras los reinicios.

---

## 11. Solución de problemas

**No se reciben notificaciones**
- Verifique que un servicio `notify.*` esté correctamente configurado y seleccionado.
- Verifique la ventana de tiempo y los días activos.
- El nivel de batería debe estar por debajo del umbral en el momento de la comprobación horaria.

**Demasiadas notificaciones**
- La histéresis está activa por defecto. Verifique si el nivel de batería fluctúa alrededor del umbral.

**Una entidad no aparece en la lista de selección**
- Solo se incluyen las entidades con clase de dispositivo `battery` y un valor numérico (0–100).

**El informe semanal no llega**
- El informe se envía como máximo una vez cada 7 días. Verifique el día y la hora configurados.

**Otro problema**
- Revise los registros de Home Assistant (Configuración → Sistema → Registros) y busque `battery_status_manager`.
- Abra un issue en [GitHub](https://github.com/OleSint/ha-battery-status-manager/issues).
