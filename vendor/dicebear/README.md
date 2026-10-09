# DiceBear, dentro de Lumea

Lumea dibuja a la persona (estilo **voxel-art**) y a los compañeros (estilo **gaze**) en el navegador, con estos archivos. No le pide nada a `api.dicebear.com`. Así:
- DiceBear no se entera de cómo se ve ni de cómo se siente cada persona, ni de su IP;
- las figuras se dibujan aunque no haya internet.

| Carpeta | Paquete | Versión | Licencia |
|---|---|---|---|
| `core/` | `@dicebear/core` (solo los `.js` de `lib/`) | 10.7.0 | MIT (`core/LICENSE`) |
| `estilos/voxel-art.json` | `@dicebear/styles` | 10.6.0 | CC0 1.0 («Voxel Art» de DiceBear) |
| `estilos/gaze.json` | `@dicebear/styles` | 10.6.0 | CC0 1.0 («Gaze» de DiceBear) |

**Uso** (módulo ES; desde la raíz del sitio):

```js
import { Style, Avatar } from './vendor/dicebear/core/index.js';
const def = await (await fetch('vendor/dicebear/estilos/voxel-art.json')).json();
const svg = new Avatar(new Style(def), { seed: 'lumea', topVariant: ['braids'], outfitVariant: ['overalls'] }).toString();
```

Las opciones son las mismas de la URL de DiceBear 10.x (`topVariant`, `skinColor`…). Van en listas, y los colores, en hexadecimal sin `#`.
