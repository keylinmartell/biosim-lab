================================================================================
BIOSIM LAB - SIMULADOR CELULAR Y GENETICO ABSTRACTO
================================================================================

[REGLA FUNDAMENTAL DE MANTENIMIENTO DEL PROYECTO]
--------------------------------------------------------------------------------
ESTE DOCUMENTO ES LA FUENTE DE VERDAD Y DEBE ACTUALIZARSE OBLIGATORIAMENTE CON 
CADA CAMBIO O NUEVO DESARROLLO EN EL SOFTWARE.

1. Cada modificacion de arquitectura, modelo de base de datos, nuevo endpoint, 
   servicio de simulacion o modulo de interfaz DEBE quedar registrado en la 
   seccion "HISTORIAL DE CAMBIOS Y EVOLUCION" al final de este archivo.
2. Ningun componente nuevo debe considerarse terminado si no se actualiza este 
   documento con su explicacion, parametros y estado actual.
3. Se debe mantener clara la trazabilidad de los datos (observado, literatura,
   supuesto de modelo, simulado, validado).
--------------------------------------------------------------------------------

1. DESCRIPCION GENERAL
BioSIM Lab es un entorno de simulacion biologica computacional por capas.
Inicia con un modulo genetico abstracto (Fase 1) para modelar celulas virtuales,
sus secuencias de ADN (A, T, C, G), complementariedad, replicacion con tasas de error
y mutaciones controladas (sustitucion, insercion, delecion).

2. STACK TECNOLOGICO
- Backend: Python 3.11+ / FastAPI
- Base de Datos: PostgreSQL (con asyncpg y SQLAlchemy 2.0)
- Migraciones: Alembic
- Frontend: Vue 3 (Composition API, Vite, Pinia, Vanilla CSS con diseno moderno)
- Motor Bio-computacional: Algoritmos estocasticos propios + Biopython (Fase 2+)

3. ESTRUCTURA DE BASE DE DATOS (POSTGRESQL)
- data_sources: Trazabilidad y procedencia de datos (observed, literature, assumption, simulated, validated).
- virtual_cells: Entidad celula virtual (cell_id, estado, ciclo celular G1/S/G2/M, contador de divisiones).
- genomes: Secuencias de nucleotidos asociadas a la celula, representacion binaria, regiones genicas.
- mutations: Registro detallado de mutaciones ocurridas (posicion, base original, base nueva, tipo).
- experiments: Pruebas in silico con condiciones ambientales, intervenciones, controles y resultados.
- cell_events: Historial cronologico de eventos de cada celula (divisiones, exposiciones, cambios de fase).

4. MOTOR DE ADN (DNA ENGINE - FASE 1 CERRADA)
- Representacion y Validacion: Almacenamiento en alfabeto A, T, C, G; deteccion reactiva de caracteres no permitidos y manejo controlado.
- Complementariedad: Generacion de cadena complementaria bajo reglas canonicas Watson-Crick (A<->T, C<->G) antiparalela (5'->3' frente a 3'->5').
- Copia fidedigna: Generacion de copias sin cambios y verificacion automatica de identidad (100% match).
- Precision de Terminos Biologicos (Dano/Lesion vs Mutacion):
  * En Fase G1 pre-replicativa, las alteraciones son 'lesiones fisicas/quimicas' o 'aductos' reparables (ej. dimeros T-T, 8-oxo-G, uracilo).
  * La 'mutacion' permanente solo se consolida e incorpora en el genoma si la lesion escapa a la reparacion y se replica en Fase S.
- Checkpoint G1/S y Sensor Molecular p53 / MDM2:
  * Reposo: p53 tiene vida media corta (~20 min); la ubiquitina ligasa MDM2 lo poliubiquitina y degrada continuamente en el proteasoma 26S. p21 inactivo.
  * Dano leve/moderado: Quinasas sensoras ATM/ATR fosforilan a p53 (Ser15/Ser20), impidiendo su degradacion por MDM2; p53 induce la transcripcion de p21 (CIP1/WAF1), inhibiendo CDK4/6 y CDK2, manteniendo a Rb hipofosforilado (secuestra a E2F), congelando el ciclo en G1 y activando BER/NER.
  * Dano masivo/irreparable: Fosforilacion sostenida (Ser46/Lys120) activa promotores de baja afinidad: efectores proapoptoticos BAX, PUMA y NOXA (permeabilizacion mitocondrial MOMP, liberacion de citocromo c y caspasas).
  * Separacion Conceptual del Punto R: El Punto R solo evalua factores mitogenicos de crecimiento (Ciclina D/CDK4/6/Rb/E2F) y no detecta danos directamente. El freno por lesiones es un bypass impuesto externamente por la via ATM/ATR -> p53 -> p21.
- Induccion de Lesiones y Edicion Dirigida (Modulo 1.1):
  * Dano ambiental estocastico: Radiacion UV (dimeros T-T), Estres oxidativo ROS (8-oxo-G) y Desaminacion espontanea (C->U/T) modulados por slider de intensidad.
  * Edicion exogena (CRISPR-Cas9 in silico): Lesion puntual/aducto (sustitucion), insercion (+1 base, frameshift) y delecion (-1 base, frameshift).
- Deteccion de Desapareamientos en el Molde (Modulo 1.2):
  * Evaluacion duplex de pares de bases canonicos vs no canonicos frente a la complementaria parental intacta.
- Mecanismos de Reparacion Pre-Replicativa (Modulo 1.3 - BER / NER / Homologia):
  * Cinetica enzimatica real probabilistica con slider de eficiencia (50% a 98%): modela la probabilidad finita de escision y el escape de lesiones por saturacion.
  * Control asistido 100% fiel: restauracion determinista limpia con secuencia de referencia homologa.
- Replicacion en Fase S y Triple Filtro MMR (Fase S):
  * Replicacion con tasa de error de polimerasa y filtro de desapareamientos post-replicativo (MutS/MutL).
- Roturas Bicatenarias DSB (Fase G2/M):
  * Comparacion mecanistica entre HDR (asistida por cromatida hermana, 100% fiel) y NHEJ (union directa propensa a microdeleciones).
- Trazabilidad y Registro de Experimentos (Modulo 3 / Seccion 7):
  * Persistencia inmutable (EXP-xxxx) con secuencias inicial/final, diagnostico, parametros y notas de laboratorio.
- Marco Cientifico (Seccion 10):
  * Documentado como modelo computacional didactico basado en reglas abstractas; no reproduce la cinetica estequiometrica total in vivo.

5. FASES DE DESARROLLO
- Fase 1 [CERRADA Y VALIDADA]: Secuencias, reglas geneticas basicas, copia, mutaciones, apareamientos incorrectos, reparacion por referencia, extension DSB, registro de experimentos, tests unitarios y laboratorio reactivo.
- Fase 2 [SIGUIENTE FASE]: Genes y expresion (regiones genicas, promotores, transcripcion y traduccion abstracta a polipeptidos).
- Fase 3 [PENDIENTE]: Regulacion genica compleja y vias de señalizacion celular.
- Fase 4 [PENDIENTE]: Estado celular y transiciones continuas.
- Fase 5 [PENDIENTE]: Diferenciacion celular y perfiles funcionales.
- Fase 6 [PENDIENTE]: Intervenciones, dosis y perturbaciones ambientales.
- Fase 7 [PENDIENTE]: Modelos especializados (envejecimiento, senescencia, modelos tumorales).

6. REFERENCIA DE DISENO VISUAL (REPLICA EXACTA: diseno celula visual.jpg)
- Fuente: Microfotografia real de fluorescencia confocal (Tincion DAPI).
- Paleta y Tinciones:
  * Nucleo celular: Azul DAPI brillante (#0066ff / #2563eb / #38bdf8).
  * Citoplasma y Membrana: Fluorescencia en cian tenue (#00ffff / #06b6d4 / #67e8f9) con halo difuso.
  * Focos de sintesis / Centrosomas: Verde-amarillo neón bioluminiscente (#4ade80 / #a3e635 / #facc15).
  * Fondo: Negro de camara confocal con ruido biologico tenue (#020617).
- Fases Morfologicas del Ciclo Celular:
  1. G0 (Celula en reposo): Celula compacta esferica pequena con halo cian tenue y nucleo azul DAPI central.
  2. G1 (Celula con nucleo visible): Crecimiento celular, doble anillo membranoso cian brillante y nucleo definido.
  3. S (Nucleo con ADN duplicandose brillante): Halo de nucleacion activo con cientos de particulas verdes/amarillas brillantes (focos de replicacion de ADN) dentro y alrededor del nucleo.
  4. G2 (Celula grande con centrosomas): Celula alargada/asimetrica con amplio citoplasma cian y dos centrosomas verde-amarillo fosforescentes en el polo superior.
  5. M (Mitosis / Citocinesis): Dos celulas hijas gemelas unidas por el centro con surco de escision y microtubulos de conexion, cada una con su nucleo azul DAPI.

7. GUIA DE EJECUCION LOCAL
- Requisitos: Python 3.11+, Node.js 18+, PostgreSQL (base de datos 'biosim' creada).

- Backend (FastAPI):

  Comando rápido directo (PowerShell desde la raíz del proyecto):
  ============================================================
  cd backend; python -m uvicorn app.main:app --reload --port 8000

  Comando rápido para exponer / compartir con Cloudflare:
  ============================================================
  OPCION A - Si tu terminal está en la RAÍZ del proyecto:
  .\tools\cloudflared.exe tunnel --url http://localhost:5173

  OPCION B - Si tu terminal está dentro de 'frontend\src' o 'frontend':
  cd ..\.. ; .\tools\cloudflared.exe tunnel --url http://localhost:5173
  (O directamente: ..\..\tools\cloudflared.exe tunnel --url http://localhost:5173)

  * Nota: Se recomienda el puerto 5173 porque incluye tanto la interfaz visual completa 
    como la API del backend conectada automáticamente mediante el proxy de Vite.

  
  PASO A PASO:
  1. Abrir terminal e ingresar a la carpeta del backend:
     cd backend

  2. (Recomendado) Crear y activar entorno virtual:
     # Crear entorno virtual:
     python -m venv venv

     # Activar en Windows (PowerShell):
     .\venv\Scripts\Activate.ps1
     # (Si PowerShell bloquea scripts ejecutar antes: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass)

     # Activar en Windows (CMD / Símbolo del sistema):
     venv\Scripts\activate.bat

     # Activar en Linux / macOS:
     source venv/bin/activate

  3. Instalar dependencias requeridas:
     pip install -r requirements.txt

  4. Configurar variables de entorno:
     # Copiar plantilla base si aun no existe .env:
     # En Windows:
     copy .env.example .env
     # En Linux/macOS:
     cp .env.example .env
     (Verificar en .env que los datos de POSTGRES_USER, POSTGRES_PASSWORD y POSTGRES_DB sean los correctos)

  5. Ejecutar el servidor backend:
     python -m uvicorn app.main:app --reload --port 8000

     # O alternativamente con uvicorn directo si esta en el PATH/venv:
     uvicorn app.main:app --reload --port 8000

  VERIFICACION Y RUTAS DEL BACKEND:
  * Healthcheck de conexion y BD: http://localhost:8000/api/v1/health
  * Documentacion interactiva Swagger (OpenAPI): http://localhost:8000/docs
  * Documentacion Redoc: http://localhost:8000/redoc

- Frontend (Vue 3 + Vite):
  1. cd frontend
  2. npm install
  3. npm run dev
  * Aplicacion web disponible en: http://localhost:5173

8. ESTRATEGIA DE DESPLIEGUE
- Base de Datos (Supabase):
  * Crear proyecto en Supabase (PostgreSQL gestionado).
  * Configurar DATABASE_URL con connection pooler.
- Frontend (Vercel):
  * Directorio raiz: frontend/ (npm run build -> dist, vercel.json configurado).

================================================================================
HISTORIAL DE CAMBIOS Y EVOLUCION DEL SISTEMA
================================================================================
Fecha: 2026-10-14
- Creacion del archivo base de documentacion viva (README.txt).
- Definicion de la regla de actualizacion continua obligatoria.
- Especificacion del diseno relacional PostgreSQL y servicios base de FastAPI + Vue 3.
- Implementacion del Visor 3D Procedural Organico ('diseno celula visual.jpg'):
  * Eliminacion total de primitivas geometricas duras (sin aros rigidos ni circulos planos).
  * Shaders GLSL con Ruido Simplex 3D para deformacion biologica natural y bordes difusos.
  * Nucleo DAPI con cromatina moteada y citoplasma etereo con halo de emision confocal.
  * En G1: doble gradiente de fluorescencia suave sin bordes artificiales.
  * En S: constelacion centelleante de 420 horquillas de replicacion de ADN en verde fluorescente.
  * En G2: deformacion aperada asimetrica y centrosomas duales con destello estelar bioluminiscente.
  * En M: estrangulamiento natural de citocinesis uniendo dos celulas hijas.
  * 5 Viewports 3D independientes a 60 FPS con rotacion interactiva 360 grados por raton.
- Build validado y probado en ejecucion continua en http://localhost:5173.
- Actualizacion de interfaz del Visor Celular 3D (CellViewer3D.vue):
  * Transicion de cuadricula de 5 columnas a Visor Unico Centralizado de Alta Definicion.
  * Selector superior interactivo con los nombres y codigos de cada fase (G0, G1, S, G2, M) en cabecera.
  * Visualizacion exclusiva del proceso seleccionado con cambio dinamico al hacer clic.
  * Optimizacion a un solo contexto WebGL con gestion de grupos 3D para maximo rendimiento.
  * Controles de navegacion rapida (anterior/siguiente), rotacion 360 grados y zoom con rueda del raton.
  * Overlays informativos flotantes (fase activa, morfologia, specs confocales y boton de sincronizacion).
- Rediseño Integral de la Plataforma a Material Design 3 (Estilo Laboratorio Profesional):
  * Adopcion estricta del sistema de tokens MD3 Dark Theme (--md-sys-color-*, --md-sys-typescale-*, --md-sys-shape-*).
  * Incorporacion de tipografias cientificas de Google Fonts (Roboto Flex, Roboto Mono) y Material Symbols Outlined.
  * Shell de laboratorio (App.vue): Top App Bar con telemetria en vivo (PostgreSQL, FastAPI), HUD de estacion de trabajo y breadcrumbs.
  * Microscopia 3D (CellViewer3D.vue): Estacion confocal con canales espectrales (DAPI 405nm, CFP 433nm, GFP 488nm), selector de fases segmentado y HUD microscopico de 100x inmersion.
  * Secuenciador y Mutagenesis (DNALab.vue): Track de nucleotidos estilo Benchling/NCBI con hebras codificante y antisentido, puentes de hidrogeno, medidor de GC%, controles CRISPR y diff alignment table.
  * Biobanco Celular (CellManager.vue): Catalogo de cepas virtuales con tarjetas MD3 Outlined, badges de estado fisiologico, generacion de linaje y modal dialog transaccional.
- Sustitucion de ligaduras de fuentes externas por componente vectorial nativo (Icon.vue):
  * Eliminacion total de textos en crudo en ingles provocados por la fuente Material Symbols (science, biotech, microbiology, etc.).
  * Renderizado inmediato y 100% offline mediante SVG vectoriales de alta definicion integrados en la aplicacion.
- Implementacion del Visor Molecular 3D Reactivo de Doble Helice B-DNA (DNAHelix3D.vue):
  * Representacion espacial tridimensional de nucleotidos como esferas bioluminiscentes codificadas por color (A: rojo, T: verde, C: cian, G: ambar).
  * Doble cadena helicoidal paralela con hebra codificante (5' a 3') y complementaria (3' a 5') separadas a 180 grados.
  * Puentes de hidrogeno conectores centrales y esqueletos tubulares fosfodiester continuos (CatmullRomCurve3).
  * Reactividad en tiempo real: al editar secuencias, aplicar mutaciones dirigidas CRISPR o replicacion estocastica, la helice 3D se regenera y muta al instante.
  * Interaccion bidireccional: clic sobre cualquier esfera del modelo 3D selecciona y enfoca la base en el track de mutacion.
  * Controles completos de rotacion 360 grados por raton, zoom y adaptacion dinamica segun longitud de cadena.
  * Refinamiento estricto a tokens Material Design 3: elevacion tonal (surface-container-*), MD3 Assist Chips, tarjetas HUD flotantes con blur, toolbar con MD3 Icon Buttons y anillos de seleccion halo cian (0x70d6ff).
- Configuracion de Salida a Internet y Acceso Remoto para Colaboradores:
  * Configuracion del proxy inverso en Vite (vite.config.js) para redirigir transparentemente las peticiones /api hacia FastAPI (puerto 8000).
  * Adaptacion de cliente HTTP (client.js) a rutas relativas (/api/v1) para interoperabilidad total en entornos locales y tuneles externos.
  * Habilitacion de allowedHosts en el servidor de desarrollo para aceptar dominios de tunel seguro.
  * Implementacion de tunel Cloudflare (cloudflared) proporcionando acceso HTTPS publico cifrado de alto rendimiento sin requerir contraseñas ni configuraciones en el cliente.
- Depuracion de cabecera principal (App.vue): retirada de la etiqueta 'Fase 1 · Nucleo' junto al logotipo BioSIM Lab para una estetica mas sobria y limpia.
- Actualizacion de Documentacion (README.txt): inclusion de guia completa y comandos detallados para inicializar y correr el backend en Windows (PowerShell/CMD) y Linux/macOS, incluyendo entorno virtual, variables .env y rutas de verificacion.

================================================================================
Fecha: 2026-10-15
Cierre de la Primera Fase: ADN, Copia, Mutaciones y Mecanismos de Reparacion
================================================================================
- Cumplimiento integral de la 'Guia de programacion — cierre de la primera fase' (BioSim Lab v1.1):
  * 1. Representacion y Validacion: 
       - Soporte para secuencias en alfabeto A, T, C, G.
       - Validacion estricta y rechazo controlado de simbolos no canonicos (ej. 'ATXG', espacios o numeros).
  * 2. Complementariedad y Copia Fidedigna:
       - Implementacion de complementaria canonica Watson-Crick (A<->T, C<->G).
       - Nuevo metodo y endpoint de copia ('/dna/copy') con comprobacion de identidad estricta (100% de coincidencias).
  * 3. Mutagénesis y Deteccion de Diferencias:
       - Mutaciones dirigidas (sustitucion puntual, insercion y delecion).
       - Replicacion estocastica celular con tasa de error de polimerasa.
       - Diff engine detallado informando posicion, base original, base nueva y tipo de cambio.
  * 4. Mecanismos de Reparacion Simplificados:
       - 3.1 Deteccion de apareamientos incorrectos (Mismatch Detection - '/dna/mismatches'):
         Compara dos cadenas alineadas y detecta pares canonicos vs no canonicos (ej. A-G, C-T).
         Regla fundamental del modelo: marca el error sin conjeturar la base original si no hay plantilla fiable.
       - 3.2 Reparacion guiada por referencia (Template-guided repair - '/dna/repair'):
         Compara la secuencia alterada con una referencia homologa fiable y reemplaza unicamente las
         posiciones autorizadas. Distingue entre correccion respaldada por referencia y conjetura.
       - 3.3 Roturas de ADN (DSB) como extension conceptual ('/dna/break-repair'):
         Simula corte bicatenario en posicion definida y compara dos vias abstractas:
         * HDR (Homology-Directed Repair): reconstruccion fiel asistida por secuencia homologa de referencia.
         * NHEJ (Non-Homologous End Joining): union directa de extremos sin plantilla, propensa a cicatrices/microdeleciones.
  * 5. Registro de Datos y Trazabilidad (Seccion 7 - '/dna/events'):
       - Cada operacion genera un identificador unico de experimento (EXP-xxxx-UUID).
       - Se persisten secuencias inicial y final, parametros, referencia usada, diagnostico de deteccion,
         resultado de reparacion, version de codigo (v1.1-phase1-closed) y suposiciones del modelo.
  * 6. Suite de Pruebas Automatizadas Unitarias (backend/tests/test_dna_phase1.py):
       - 10 pruebas unitarias automatizadas cubriendo los 8 escenarios minimos de la Seccion 5 de la guia:
         secuencia valida (ATCG), simbolo no valido (ATXG), complementariedad (TAGC), copia exacta (GATTACA),
         mutacion controlada, apareamiento incorrecto duplex, reparacion con referencia, comportamiento sin referencia,
         extension DSB (HDR y NHEJ) y trazabilidad de eventos.
       - Ejecucion exitosa al 100% (Ran 10 tests in 0.005s, OK).
  * 7. Interfaz de Usuario Reactiva (DNALab.vue):
       - Boton y telemetria de 'Copiar Secuencia' con banner de confirmacion de identidad.
       - Modulo interactivo de Deteccion de Desapareamientos Watson-Crick con tira visual de nucleotidos y boton 'Inducir Error'.
       - Modulo de Reparacion Asistida por Referencia Homologa con informe de estado y preview.
       - Simulador de Rotura Bicatenaria (DSB) con visualizador de corte, fragmentos escindidos y cicatriz molecular.
       - Cuaderno de Bitacora y Auditoria de Experimentos en vivo con tabla de trazabilidad completa.
       - Banner oficial de Nota Cientifica (Seccion 10) aclarando las suposiciones didacticas in silico del modelo.
  * 8. Iconos Vectoriales Nativos (Icon.vue):
       - Adicion de glifos 'content_copy', 'history' y 'build' en SVG nativo sin dependencias externas.
  * 9. Build y pruebas en navegador:
       - Compilacion de produccion con Vite exitosa en 401ms sin errores.
       - Verificacion funcional automatizada de extremo a extremo en el navegador.
  * 10. Correccion de Validacion en Tiempo Real:
       - Deteccion reactiva instantanea de simbolos no canonicos (ej. 'O', 'X', etc.) directamente sobre la cadena cruda del usuario.
       - Ingestion de 'invalid_chars' y 'error_message' en el payload de respuesta de FastAPI.
       - Desactivacion preventiva de renderizado 3D y muestra de banner de advertencia molecular cuando la cadena contiene caracteres no validos.
  * 11. Sistema de Guardado y Carga Integral de Experimentos:
       - Almacenamiento completo del ciclo de vida del experimento (molde inicial, copia, mutacion/rotura, desapareamientos, reparacion y secuencia final).
       - Endpoints dedicados: POST /dna/experiment/save, GET /dna/experiment/list y GET /dna/experiment/{id}.
       - Persistencia automatica en disco (saved_experiments.json) asegurando disponibilidad ante reinicios.
       - Dialogo modal 'Cargar Experimento Guardado' con tarjetas informativas y previsualizacion de secuencias.
       - Boton directo 'Cargar' en la tabla de bitacora para restaurar el laboratorio con un solo clic.
       - Restauracion completa del estado del laboratorio: secuencia de entrada, hélice 3D, mapa de nucleotidos, coordenadas de mutacion y reportes diff.
   * 12. Flujo Cientifico Experimental Unificado (Stepper Guiado de 5 Pasos):
        - Paso 1: Molde Inicial Validado (secuencia de entrada del usuario como referencia parental inmutable).
        - Paso 2: Copia de Trabajo Activa (duplicacion fidedigna para ensayos sin alterar el molde).
        - Paso 3: Induccion de Daño Molecular (mutacion puntual CRISPR, replicacion con error o rotura DSB).
        - Paso 4: Deteccion de Daño (MMR / Diff) automatica e instantanea comparando frente a la complementaria del molde inicial.
        - Paso 5: Reparacion Guiada por Homologia (restauracion basada en el molde inicial con verificacion de fidelidad).
        - Boton rapido 'Restaurar a Molde' para reiniciar el laboratorio directamente desde la hebra molde.

================================================================================
Fecha: 2026-10-22
Alineacion Biologica Fase G1, Eje p53/MDM2, Separacion Punto R y Actualizacion
================================================================================
- Precision de Nomenclatura Biologica (Dano/Lesion vs Mutacion):
  * Sustitucion de la palabra 'mutacion' por 'dano', 'lesion fisica/quimica' o 'aducto' en la Fase G1,
    Modulo 1.1 y selectores de evento.
  * Incorporacion de banner en la interfaz y en el manual aclarando que en Fase G1 el ADN presenta
    lesiones o aductos quimicos reparables, y que unicamente se convertiran en mutaciones irreversibles
    si escapan a la escision enzimatica (BER/NER) y se replican mas adelante en la Fase S.
- Integracion y Renderizado del Checkpoint G1/S en Vivo (DNALab.vue):
  * Implementacion de la tarjeta reactiva 'checkpoint-g1-card' vinculada a la propiedad computada 'checkpointG1Status'.
  * Semáforo molecular de tres estados en cabecera y cuerpo:
    1. Estado en reposo (Verde): Molde integro; p53 con vida media corta (~20 min) degradado de forma continua
       por la ubiquitina ligasa E3 MDM2 en el proteasoma 26S; p21 inactivo y complejos CDK activos.
    2. Dano leve/moderado (Ambar): Quinasas sensoras ATM/ATR fosforilan a p53 (Ser15/Ser20), impidiendo su degradacion
       por MDM2 y estabilizandolo; p53 transcribe p21 (CIP1/WAF1) inhibiendo CDK4/6 y CDK2, manteniendo a Rb
       hipofosforilado (secuestrando a E2F) y activando la reparacion por escision de bases y nucleotidos (BER/NER).
    3. Dano masivo/irreparable (Rojo pulsante): Fosforilacion sostenida (Ser46/Lys120) que conmuta la expresion genica
       hacia el programa proapoptotico mitocondrial transcribiendo efectores de baja afinidad: BAX, PUMA y NOXA
       (permeabilizacion mitocondrial MOMP, liberacion de citocromo c y activacion de caspasas).
- Desacoplamiento y Separacion Conceptual del Punto R:
  * El Punto de Restriccion (Punto R) evalua exclusivamente senales mitogenicas de proliferacion celular
    (Ciclina D / CDK4/6 / Rb / E2F) y no detecta danos genotoxicos de forma directa.
  * El arresto ante lesiones de ADN es un bypass impuesto externamente desde la cascada de estres ATM/ATR -> p53 -> p21,
    que neutraliza a las quinasas dependientes de ciclinas e impide superar el Punto R hacia Fase S.
- Actualizacion de Botones y Controles en la Interfaz y Manuales:
  * Modulo 1.1: 'Inducir Lesiones Ambientales en el Molde' (con selector de agente genotoxico UV, ROS, Desaminacion
    y slider de intensidad) e 'Inducir Lesión Dirigida (CRISPR-Cas9)' (con tipo de alteracion puntual, insercion o delecion).
  * Modulo 1.2: 'Escanear Apareamientos', 'Complementaria' e 'Inducir Error'.
  * Modulo 1.3: 'Usar Molde Inicial' y 'Ejecutar Ciclo de Escisión Enzimática' (con switcher de cinetica probabilistica
    vs control asistido al 100% y slider de eficiencia de escision 50%-98%).
  * Actualizacion del manual interactivo en pantalla (DNALab.vue), guia tecnica externa (MANUAL_LABORATORIO_ADN.txt)
    y bitacora del proyecto (README.txt).

