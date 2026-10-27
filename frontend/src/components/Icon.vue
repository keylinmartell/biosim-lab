<template>
  <svg 
    :width="size" 
    :height="size" 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    :stroke-width="strokeWidth" 
    stroke-linecap="round" 
    stroke-linejoin="round"
    class="lab-icon"
  >
    <!-- Matraz / Ciencia -->
    <g v-if="name === 'science' || name === 'flask'">
      <path d="M10 2v7.31L4.2 18.06A2 2 0 0 0 5.86 21h12.28a2 2 0 0 0 1.66-2.94L14 9.31V2" />
      <line x1="8.5" y1="2" x2="15.5" y2="2" />
      <path d="M14 9.3a6.5 6.5 0 0 0-4 0" />
      <circle cx="10" cy="15" r="1" fill="currentColor" />
      <circle cx="13" cy="17" r="1" fill="currentColor" />
    </g>

    <!-- Microscopio / Biotech -->
    <g v-else-if="name === 'biotech' || name === 'microscope'">
      <path d="M6 18h8" />
      <path d="M3 22h18" />
      <path d="M14 22a7 7 0 1 0 0-14h-1" />
      <path d="M9 14h2" />
      <path d="M9 12a2 2 0 0 1-2-2V6h6v4a2 2 0 0 1-2 2Z" />
      <line x1="12" y1="6" x2="12" y2="2" />
    </g>

    <!-- ADN / Genética -->
    <g v-else-if="name === 'dna' || name === 'cyclone' || name === 'genetics'">
      <path d="M2 15c6.667-6 13.333 0 20-6" />
      <path d="M9 22c1.798-1.998 2.518-3.995 2.807-5.993" />
      <path d="M15 2c-1.798 1.998-2.518 3.995-2.807 5.993" />
      <path d="M17 6l-2.5-2.5" />
      <path d="M14 8l-1-1" />
      <path d="M7 18l2.5 2.5" />
      <path d="M3.5 14.5l.5.5" />
      <path d="M20 9.5l.5.5" />
      <path d="M6.5 12.5l11-1" />
      <path d="M10 10l4 4" />
    </g>

    <!-- Base de Datos / Dataset -->
    <g v-else-if="name === 'dataset' || name === 'database' || name === 'storage'">
      <ellipse cx="12" cy="5" rx="9" ry="3" />
      <path d="M3 5V19A9 3 0 0 0 21 19V5" />
      <path d="M3 12A9 3 0 0 0 21 12" />
    </g>

    <!-- Servidor / DNS -->
    <g v-else-if="name === 'dns' || name === 'server'">
      <rect x="2" y="2" width="20" height="8" rx="2" ry="2" />
      <rect x="2" y="14" width="20" height="8" rx="2" ry="2" />
      <line x1="6" y1="6" x2="6.01" y2="6" stroke-width="3" />
      <line x1="6" y1="18" x2="6.01" y2="18" stroke-width="3" />
    </g>

    <!-- Terminal -->
    <g v-else-if="name === 'terminal'">
      <polyline points="4 17 10 11 4 5" />
      <line x1="12" y1="19" x2="20" y2="19" />
    </g>

    <!-- Escudo / Protección -->
    <g v-else-if="name === 'shield'">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </g>

    <!-- Rotación 3D -->
    <g v-else-if="name === '3d_rotation' || name === 'rotate'">
      <path d="M21.5 2v6h-6" />
      <path d="M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67" />
    </g>

    <!-- Zoom In -->
    <g v-else-if="name === 'zoom_in' || name === 'zoom'">
      <circle cx="11" cy="11" r="8" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
      <line x1="11" y1="8" x2="11" y2="14" />
      <line x1="8" y1="11" x2="14" y2="11" />
    </g>

    <!-- Zoom Out -->
    <g v-else-if="name === 'zoom_out'">
      <circle cx="11" cy="11" r="8" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
      <line x1="8" y1="11" x2="14" y2="11" />
    </g>

    <!-- Desplazar / Pan / Mano -->
    <g v-else-if="name === 'pan_tool' || name === 'drag' || name === 'pan'">
      <polyline points="5 9 2 12 5 15" />
      <polyline points="9 5 12 2 15 5" />
      <polyline points="15 19 12 22 9 19" />
      <polyline points="19 9 22 12 19 15" />
      <line x1="2" y1="12" x2="22" y2="12" />
      <line x1="12" y1="2" x2="12" y2="22" />
    </g>

    <!-- Flechas Arriba y Abajo -->
    <g v-else-if="name === 'arrow_upward' || name === 'arrow_up'">
      <line x1="12" y1="19" x2="12" y2="5" />
      <polyline points="5 12 12 5 19 12" />
    </g>
    <g v-else-if="name === 'arrow_downward' || name === 'arrow_down'">
      <line x1="12" y1="5" x2="12" y2="19" />
      <polyline points="19 12 12 19 5 12" />
    </g>

    <!-- Flechas Navegación -->
    <g v-else-if="name === 'chevron_left'">
      <polyline points="15 18 9 12 15 6" />
    </g>
    <g v-else-if="name === 'chevron_right'">
      <polyline points="9 18 15 12 9 6" />
    </g>
    <g v-else-if="name === 'arrow_forward'">
      <line x1="5" y1="12" x2="19" y2="12" />
      <polyline points="12 5 19 12 12 19" />
    </g>
    <g v-else-if="name === 'arrow_back'">
      <line x1="19" y1="12" x2="5" y2="12" />
      <polyline points="12 19 5 12 12 5" />
    </g>
    <g v-else-if="name === 'my_location'">
      <circle cx="12" cy="12" r="8" />
      <line x1="12" y1="2" x2="12" y2="6" />
      <line x1="12" y1="18" x2="12" y2="22" />
      <line x1="2" y1="12" x2="6" y2="12" />
      <line x1="18" y1="12" x2="22" y2="12" />
      <circle cx="12" cy="12" r="2" fill="currentColor" />
    </g>

    <!-- Info -->
    <g v-else-if="name === 'info'">
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="16" x2="12" y2="12" />
      <line x1="12" y1="8" x2="12.01" y2="8" stroke-width="3" />
    </g>

    <!-- Guardar -->
    <g v-else-if="name === 'save'">
      <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
      <polyline points="17 21 17 13 7 13 7 21" />
      <polyline points="7 3 7 8 15 8" />
    </g>

    <!-- Etiqueta / Muestra -->
    <g v-else-if="name === 'tag'">
      <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" />
      <line x1="7" y1="7" x2="7.01" y2="7" stroke-width="3" />
    </g>

    <!-- Gota de Agua -->
    <g v-else-if="name === 'water_drop'">
      <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z" />
    </g>

    <!-- Analítica -->
    <g v-else-if="name === 'analytics'">
      <line x1="18" y1="20" x2="18" y2="10" />
      <line x1="12" y1="20" x2="12" y2="4" />
      <line x1="6" y1="20" x2="6" y2="14" />
    </g>

    <!-- Check Circle -->
    <g v-else-if="name === 'check_circle' || name === 'check'">
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
      <polyline points="22 4 12 14.01 9 11.01" />
    </g>

    <!-- Advertencia -->
    <g v-else-if="name === 'warning' || name === 'priority_high'">
      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
      <line x1="12" y1="9" x2="12" y2="13" />
      <line x1="12" y1="17" x2="12.01" y2="17" stroke-width="3" />
    </g>

    <!-- Edición / Corte CRISPR -->
    <g v-else-if="name === 'edit_note' || name === 'content_cut'">
      <circle cx="6" cy="6" r="3" />
      <circle cx="6" cy="18" r="3" />
      <line x1="20" y1="4" x2="8.12" y2="15.88" />
      <line x1="14.47" y1="14.48" x2="20" y2="20" />
      <line x1="8.12" y1="8.12" x2="12" y2="12" />
    </g>

    <!-- Duplicación Aleatoria / Barajar -->
    <g v-else-if="name === 'shuffle'">
      <polyline points="16 3 21 3 21 8" />
      <line x1="4" y1="20" x2="21" y2="3" />
      <polyline points="21 16 21 21 16 21" />
      <line x1="15" y1="15" x2="21" y2="21" />
      <line x1="4" y1="4" x2="9" y2="9" />
    </g>

    <!-- Reinicio / Replicar -->
    <g v-else-if="name === 'restart_alt'">
      <path d="M3 12a9 9 0 0 1 15.55-6.36L21 8" />
      <polyline points="21 3 21 8 16 8" />
      <path d="M21 12a9 9 0 0 1-15.55 6.36L3 16" />
      <polyline points="3 21 3 16 8 16" />
    </g>

    <!-- Comparar -->
    <g v-else-if="name === 'compare_arrows'">
      <polyline points="7 10 12 15 17 10" />
      <line x1="12" y1="15" x2="12" y2="3" />
      <polyline points="17 14 12 9 7 14" />
      <line x1="12" y1="9" x2="12" y2="21" />
    </g>

    <!-- Huella Dactilar / Identificador -->
    <g v-else-if="name === 'fingerprint'">
      <path d="M12 10a2 2 0 0 0-2 2c0 1.02-.1 2.51-.26 4" />
      <path d="M14 13.12c0 2.38 0 6.38-1 8.88" />
      <path d="M2 16h.01" />
      <path d="M21.8 16c.2-2 .131-5.354 0-6" />
      <path d="M5 19.5C5.5 18 6 15 6 12a6 6 0 0 1 .34-2" />
      <path d="M8.65 22c.21-.66.45-1.32.57-2" />
      <path d="M9 6.8a6 6 0 0 1 9 5.2v2" />
    </g>

    <!-- División Celular -->
    <g v-else-if="name === 'cell_merge'">
      <circle cx="7" cy="12" r="5" />
      <circle cx="17" cy="12" r="5" />
      <line x1="12" y1="7" x2="12" y2="17" stroke-dasharray="2 2" />
    </g>

    <!-- Ojo / Inspeccionar -->
    <g v-else-if="name === 'visibility'">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
      <circle cx="12" cy="12" r="3" />
    </g>

    <!-- Más / Agregar -->
    <g v-else-if="name === 'add'">
      <line x1="12" y1="5" x2="12" y2="19" />
      <line x1="5" y1="12" x2="19" y2="12" />
    </g>

    <!-- Reproducir / Play -->
    <g v-else-if="name === 'play_arrow' || name === 'play'">
      <polygon points="5 3 19 12 5 21 5 3" fill="currentColor" />
    </g>

    <!-- Pausa -->
    <g v-else-if="name === 'pause'">
      <rect x="6" y="4" width="4" height="16" fill="currentColor" />
      <rect x="14" y="4" width="4" height="16" fill="currentColor" />
    </g>

    <!-- Capas / Layers -->
    <g v-else-if="name === 'layers'">
      <polygon points="12 2 2 7 12 12 22 7 12 2" />
      <polyline points="2 17 12 22 22 17" />
      <polyline points="2 12 12 17 22 12" />
    </g>

    <!-- Ajustes / Tune -->
    <g v-else-if="name === 'tune' || name === 'sliders'">
      <line x1="4" y1="21" x2="4" y2="14" />
      <line x1="4" y1="10" x2="4" y2="3" />
      <line x1="12" y1="21" x2="12" y2="12" />
      <line x1="12" y1="8" x2="12" y2="3" />
      <line x1="20" y1="21" x2="20" y2="16" />
      <line x1="20" y1="12" x2="20" y2="3" />
      <line x1="1" y1="14" x2="7" y2="14" />
      <line x1="9" y1="8" x2="15" y2="8" />
      <line x1="17" y1="16" x2="23" y2="16" />
    </g>

    <!-- Copiar / Portapapeles -->
    <g v-else-if="name === 'content_copy' || name === 'copy'">
      <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
    </g>

    <!-- Historial / Bitácora -->
    <g v-else-if="name === 'history' || name === 'log'">
      <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
      <path d="M3 3v5h5" />
      <path d="M12 7v5l4 2" />
    </g>

    <!-- Reparación / Herramienta -->
    <g v-else-if="name === 'build' || name === 'repair'">
      <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" />
    </g>

    <!-- Manual / Libro / Ayuda -->
    <g v-else-if="name === 'menu_book' || name === 'book' || name === 'manual'">
      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
      <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
      <line x1="12" y1="6" x2="16" y2="6" />
      <line x1="12" y1="10" x2="16" y2="10" />
    </g>

    <!-- Verificado / Certificado -->
    <g v-else-if="name === 'verified'">
      <path d="M9 12l2 2 4-4" />
      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87L18.18 21 12 17.27 5.82 21 7 14.14l-5-4.87 6.91-1.01L12 2z" />
    </g>

    <!-- Escuela / Didáctico -->
    <g v-else-if="name === 'school'">
      <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
      <path d="M6 12v5c3 3 9 3 12 0v-5" />
    </g>

    <!-- Dashboard / Tablero -->
    <g v-else-if="name === 'dashboard'">
      <rect x="3" y="3" width="7" height="7" rx="1" />
      <rect x="14" y="3" width="7" height="4" rx="1" />
      <rect x="14" y="10" width="7" height="11" rx="1" />
      <rect x="3" y="13" width="7" height="8" rx="1" />
    </g>

    <!-- Sincronizar -->
    <g v-else-if="name === 'sync'">
      <path d="M21.5 2v6h-6" />
      <path d="M2.5 22v-6h6" />
      <path d="M21.34 8A10 10 0 0 0 4.26 5.68L2.5 8" />
      <path d="M2.66 16A10 10 0 0 0 19.74 18.32L21.5 16" />
    </g>

    <!-- Entrada / Input -->
    <g v-else-if="name === 'input'">
      <path d="M21 3H3v18h18" />
      <polyline points="9 12 13 12" />
      <polyline points="11 9 14 12 11 15" />
    </g>

    <!-- Línea de Tiempo / Timeline -->
    <g v-else-if="name === 'view_timeline'">
      <rect x="2" y="3" width="20" height="4" rx="1" />
      <rect x="4" y="10" width="16" height="4" rx="1" />
      <rect x="6" y="17" width="12" height="4" rx="1" />
    </g>

    <!-- Caja / Vacío -->
    <g v-else>
      <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
      <line x1="9" y1="9" x2="15" y2="15" />
      <line x1="15" y1="9" x2="9" y2="15" />
    </g>
  </svg>
</template>

<script setup>
defineProps({
  name: {
    type: String,
    required: true
  },
  size: {
    type: [Number, String],
    default: 18
  },
  strokeWidth: {
    type: [Number, String],
    default: 2
  }
});
</script>

<style scoped>
.lab-icon {
  display: inline-block;
  vertical-align: middle;
  flex-shrink: 0;
}
</style>
