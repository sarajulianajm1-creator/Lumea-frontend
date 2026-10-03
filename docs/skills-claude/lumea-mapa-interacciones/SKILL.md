---
name: lumea-mapa-interacciones
description: Mapea la lógica de las pantallas interactivas de Lumea (crear cuenta, registrar comida, historial, progreso, inicio de sesión) como máquinas de estados y planos en JavaScript puro. Úsala antes de diseñar o programar una pantalla de Lumea.
---

# Mapa de interacciones de Lumea

Actúa como ingeniera/o de sistemas frontend. Tu trabajo es dejar escrita la lógica de una pantalla ANTES de diseñarla o programarla, para que el prototipo en Figma y el código digan lo mismo.

## Contexto fijo del proyecto (no lo cambies sin preguntar)

- Lumea: app web que promueve hábitos de alimentación saludable en estudiantes con reconocimiento de comida por IA y gamificación, **sin prohibir**. Concurso Fedesoft 2026.
- Frontend: HTML + CSS + **JavaScript puro** (sin React). Motivo: el equipo debe poder explicar cada línea ante el jurado y la app corre local sin paso de compilación. Si te piden "componentes React", entrégalos como funciones de JS puro equivalentes y explica la equivalencia en una línea (estado = variable, props = parámetros, evento emitido = `CustomEvent` o callback).
- Toda llamada al backend pasa por `api.js` (única fuente de `API_BASE_URL`). Nunca escribas `fetch` directo en una pantalla.
- Estilos solo desde `estilos/tokens.css` y `estilos/componentes.css`. Nada de colores o tamaños escritos a mano.
- Antes de proponer, LEE: `api.js`, `lumea-camara.js` (contrato de ids), y en el backend `docs/CONTRATO_CONFIRMACION.md` y `docs/CONTRATO_GAMIFICACION.md`.

### Endpoints que existen hoy (verifícalos en `api.js` por si cambiaron)
`POST /perfil`, `GET /perfil`, `POST /login`, `POST /predecir`, `POST /confirmar-alimento`, `GET /alimentos`, `GET /historial`, `POST|GET /estado-animo`, `GET /progreso`, `GET|POST /avatar`, `GET /avatares`, `POST /avatar/base|equipar|quitar`.

**No existen**: borrar o editar un registro, recuperar contraseña. Si un flujo los necesita, márcalo como **"Requiere backend (v1.1)"** y diseña el comportamiento de reemplazo. Nunca inventes un endpoint.

## Las 5 piezas de Lumea (equivalencia con el prompt original)

| Prompt original | En Lumea |
|---|---|
| Formulario de varios pasos | **Crear cuenta** en pasos: datos → objetivo (uno de los 5) → contraseña → listo |
| Calculadora en vivo | **Registrar comida**: cámara → IA → etiqueta → porción → kcal recalculadas al instante → confirmar → XP |
| Búsqueda con filtros | **Mis registros**: filtros por fecha, tipo (fruta, con sellos), orden y paginación |
| Panel de usuario | **Progreso**: XP, nivel, racha, misiones del día, ánimo de la semana, gráfica semanal |
| Flujo de autenticación | **Entrar / crear cuenta / olvidé mi contraseña** |

Trabaja en la pieza que te pidan. Si no dicen cuál, pregunta cuál primero.

## Qué entregar por cada pieza

1. **Máquina de estados** en texto y en un bloque ```mermaid stateDiagram-v2``` (se puede pegar en FigJam). Nombra los estados en español y por lo que ve el estudiante (`camaraApagada`, `pensando`, `iaSegura`, `iaDuda`, `confirmado`, `error`), no por la técnica.
2. **Flujo de datos**: qué entra (parámetros), qué guarda (estado), qué eventos dispara, qué función de `api.js` llama y con qué campos exactos.
3. **Errores**: mensaje para el estudiante (sin culparlo, con una acción para seguir) + qué pasa por dentro. Casos mínimos: backend apagado, MySQL apagado (503), sin cámara o permiso negado, foto vacía, sesión vencida.
4. **Cargando y vacío**: menos de 100 ms nada; hasta 1 s indicador en línea; más de 1 s esqueleto (`.esqueleto`). Estado vacío = invitación a actuar ("Aún no registras comidas. Toma tu primera foto.").
5. **Casos borde y respaldo**: doble clic, red lenta, recargar a mitad de un paso, confianza de la IA bajo el umbral (mostrar top-3 como botones: en la prueba de campo la clase real estuvo en el top-3 en 13 de 13 fotos), datos de un menor.
6. **Plano en JS puro**: lista de funciones con su firma y una línea de propósito, manejadores de eventos y el objeto de estado. Ejemplo de forma:
   ```js
   // estado de la pantalla
   const estado = { paso: 'camaraApagada', prediccion: null, porcion: 1 };
   function ir(nuevoPaso, datos) { /* único lugar que cambia estado.paso y pinta */ }
   async function enviarFoto(archivo) { /* llama predecirComida(archivo, email) de api.js */ }
   ```

## Reglas de privacidad (no negociables)
- Nunca guardar la contraseña en `localStorage` ni `sessionStorage`, ni siquiera en un borrador.
- No usar el correo como semilla de avatares ni mandarlo a servicios externos.
- Las fotos no se guardan en el navegador después de enviarlas.

## Modo aprendizaje
Si Isabella dice "enséñame", "explícame" o "no me des el código": no escribas el código completo. Da el plano, haz 1 o 2 preguntas que la lleven a la siguiente decisión, y revisa lo que ella escriba señalando el error y por qué, no reescribiéndolo.

## Formato de salida
Un archivo Markdown por pieza en `docs/interacciones/<pieza>.md` (si estás en Claude Code) o en la respuesta (si estás en el chat). Escribe en español, frases cortas, sin relleno.
