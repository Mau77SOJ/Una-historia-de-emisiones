# El Pulso del Planeta: Dashboard de Emisiones de CO₂

Un dashboard interactivo para explorar, comparar y proyectar emisiones de CO₂ a nivel global con storytelling y visualizaciones avanzadas.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)

## Descripción

Este proyecto transforma datos de emisiones de CO₂ en una narrativa visual comprensible, permitiendo a usuarios de cualquier nivel entender:

- **Quién emite** y cuánto CO₂ a nivel global
- **Cómo ha cambiado** nuestra relación con el carbono desde 1990
- **Comparaciones** entre países y regiones
- **Proyecciones** de escenarios futuros
- **Fuentes específicas** de emisiones por combustible

## Características

### Análisis Individual
- KPIs contextualizados (emisiones totales, per cápita, población, PIB)
- Evolución histórica con eventos climáticos marcados (Kyoto, París, COVID-19)
- Ranking global de emisores
- Relación entre desarrollo económico y emisiones

### Comparación de Países
- Análisis lado a lado de dos países
- Gráficos duales de evolución temporal
- Métricas comparativas detalladas
- Identificación de trayectorias divergentes

### Proyecciones Futuras
- Tres escenarios basados en tendencias históricas:
  - **Optimista**: Reducción acelerada
  - **Tendencia actual**: Business as usual
  - **Pesimista**: Aceleración de emisiones
- Proyecciones a 10 años
- Interpretación clara de cada escenario

### Fuentes de Emisión
- Desglose por combustible (carbón, petróleo, gas, cemento)
- Evolución temporal por fuente
- Análisis de transición energética
- Métrica de "Intensidad de Carbón"
- Recomendaciones de descarbonización

### Prerrequisitos
- Python 3.8 o superior
- pip

### Navegación por Tabs

#### Tab 1: Análisis Individual
1. Selecciona un país del menú desplegable
2. Explora las métricas actuales
3. Revisa la evolución histórica
4. Analiza el contexto global

#### Tab 2: Comparación de Países
1. Selecciona el "País A" y "País B"
2. Compara métricas actuales
3. Observa gráficos de evolución paralela
4. Lee el análisis comparativo

#### Tab 3: Proyecciones Futuras
1. Elige un país para proyectar
2. Visualiza los escenarios
3. Interpreta las implicaciones
4. **Nota**: Son estimaciones ilustrativas, no predicciones oficiales

#### Tab 4: Fuentes de Emisión
1. Selecciona un país
2. Examina el gráfico de torta con fuentes
3. Revisa la evolución temporal
4. Analiza la dependencia del carbón

## Fuente de Datos

Los datos provienen de **[Our World in Data - CO₂ and Greenhouse Gas Emissions](https://github.com/owid/co2-data)**, que compila información de:

- **Global Carbon Project**: Emisiones de combustibles fósiles
- **BP Statistical Review**: Datos de producción energética
- **Maddison Project Database**: Datos históricos de PIB

### Actualización de Datos
Los datos se cargan directamente desde el repositorio de GitHub de Our World in Data, garantizando información actualizada en cada ejecución.

## Características Técnicas

- **Framework**: Streamlit para interfaces web interactivas
- **Visualizaciones**: Plotly para gráficos interactivos y responsivos
- **Procesamiento**: Pandas para manipulación eficiente de datos
- **Proyecciones**: NumPy para regresión lineal simple
- **Cache**: `@st.cache_data` para optimizar carga de datos

## Notas Importantes

### Limitaciones
- **Proyecciones**: Son estimaciones simples basadas en regresión lineal de los últimos 10 años. No consideran:
  - Cambios de política climática
  - Crisis económicas
  - Innovaciones tecnológicas
  - Eventos imprevistos


- **Datos faltantes**: Algunos países tienen datos incompletos o desactualizados

