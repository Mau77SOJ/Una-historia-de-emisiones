import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Configuración de página
st.set_page_config(page_title="Emisiones CO₂ Global", page_icon="🌍", layout="wide")

# Cargar dataset
@st.cache_data(show_spinner=False)
def load_data():
    url = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
    df = pd.read_csv(url)
    df = df[df["year"] >= 1950]
    return df

df = load_data()

# Header con contexto
st.title("El Pulso del Planeta: Una Historia de Emisiones")
st.markdown("""
<div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 30px;'>
<h3 style='color: #1f77b4; margin-top: 0;'>¿Por qué importa el CO₂?</h3>
<p style='font-size: 16px; line-height: 1.6;'>
Cada tonelada de CO₂ emitida permanece en la atmósfera por <b>siglos</b>, atrapando calor 
y alterando el clima global. Desde la Revolución Industrial, hemos emitido más de 
<b>1.5 billones de toneladas</b>, elevando la temperatura global 1.1°C. 
<br><br>
Este dashboard te permite explorar <b>quién emite</b>, <b>cuánto</b> y <b>cómo ha cambiado</b> 
nuestra relación con el carbono.
</p>
</div>
""", unsafe_allow_html=True)

# Tabs para diferentes análisis
tab1, tab2, tab3, tab4 = st.tabs([
    "Análisis Individual", 
    "Comparación de Países", 
    "Proyecciones Futuras",
    "Fuentes de Emisión"
])

# ========== TAB 1: ANÁLISIS INDIVIDUAL ==========
with tab1:
    st.subheader("Explora un país")
    col_select, col_info = st.columns([2, 3])

    with col_select:
        paises = df["country"].unique().tolist()
        pais = st.selectbox(
            "Selecciona un territorio", 
            ["World"] + sorted(paises),
            help="Puedes explorar países individuales o el total mundial",
            key="pais1"
        )

    with col_info:
        if pais == "World":
            st.info("**Vista Global**: Observa el panorama completo de emisiones mundiales desde 1990.")
        else:
            st.success(f"**{pais}**: Descubre el perfil de emisiones y su evolución en las últimas décadas.")

    data_pais = df[df["country"] == pais].sort_values("year")

    # Validar datos
    if data_pais.empty or data_pais["co2"].isna().all():
        st.warning(f"No hay datos suficientes de CO₂ para {pais}")
        st.stop()

    # === El Contexto Actual ===
    st.markdown("---")
    st.header("La Situación Actual")

    ultimo_año = int(data_pais["year"].max())
    data_reciente = data_pais[data_pais["year"] == ultimo_año].iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        emisiones_actuales = data_reciente["co2"] if pd.notna(data_reciente["co2"]) else 0
        st.metric("Emisiones Anuales", f"{emisiones_actuales:,.0f} Mt", help=f"Millones de toneladas en {ultimo_año}")
        st.caption(f"Año {ultimo_año}")

    with col2:
        per_capita = data_reciente["co2_per_capita"] if pd.notna(data_reciente["co2_per_capita"]) else 0
        st.metric("Por Persona", f"{per_capita:.1f} t", help="Toneladas de CO₂ por habitante al año")
        if per_capita > 10:
            st.caption("🔴 Alto impacto")
        elif per_capita > 5:
            st.caption("🟡 Impacto medio")
        else:
            st.caption("🟢 Bajo impacto")

    with col3:
        poblacion = data_reciente["population"] if pd.notna(data_reciente["population"]) else 0
        st.metric("Población", f"{poblacion/1e6:.0f}M", help="Millones de habitantes")


    # === La Historia ===
    st.markdown("---")
    st.header("La Historia en Números")

    primer_año = int(data_pais["year"].min())
    data_primera = data_pais[data_pais["year"] == primer_año].iloc[0]
    cambio_porcentual = ((emisiones_actuales - data_primera["co2"]) / data_primera["co2"] * 100) if pd.notna(data_primera["co2"]) and data_primera["co2"] > 0 else 0

    col_story1, col_story2 = st.columns([2, 1])

    with col_story1:
        st.markdown(f"""
        **Desde {primer_año}**, las emisiones de **{pais}** han cambiado un 
        **{cambio_porcentual:+.1f}%**. 
        {'Crecimiento asociado al desarrollo económico.' if cambio_porcentual > 0 else 'Reducción asociada a transición energética.'}
        """)

    with col_story2:
        st.metric("Cambio Total", f"{cambio_porcentual:+.1f}%", delta=f"vs {primer_año}")

    fig_time = go.Figure()
    fig_time.add_trace(go.Scatter(
        x=data_pais["year"], y=data_pais["co2"],
        mode='lines+markers', name='Emisiones Totales',
        line=dict(color='#ff6b6b', width=3),
        hovertemplate='<b>%{x}</b><br>Emisiones: %{y:.1f} Mt<extra></extra>'
    ))

    if pais == "World":
        eventos = [(1997, "Protocolo de Kyoto", "green"), (2015, "Acuerdo de París", "blue"), (2020, "COVID-19", "purple")]
        for año, texto, color in eventos:
            fig_time.add_vline(x=año, line_dash="dash", line_color=color, annotation_text=texto)

    fig_time.update_layout(title=f"Evolución de Emisiones: {pais}", xaxis_title="Año", yaxis_title="Emisiones CO₂ (Mt)", hovermode='x unified', height=400)
    st.plotly_chart(fig_time, use_container_width=True)

    # === Emisiones per cápita ===
    st.markdown("---")
    st.header("La Huella Personal")

    st.write("Las emisiones per cápita reflejan el estilo de vida promedio. Un estadounidense emite ~15 t/año, mientras un habitante de India ~2 t.")

    fig_capita = px.area(
        data_pais, x="year", y="co2_per_capita",
        title=f"Emisiones por Persona en {pais}",
        labels={"co2_per_capita": "Toneladas CO₂/persona", "year": "Año"},
        color_discrete_sequence=["#4ecdc4"]
    )
    fig_capita.update_layout(height=350)
    st.plotly_chart(fig_capita, use_container_width=True)

    # === Contexto Global ===
    st.markdown("---")
    st.header("¿Dónde Está Parado Este País en el Mundo?")

    data_ultimo_año = df[df["year"] == ultimo_año].dropna(subset=["co2"])
    top_10 = data_ultimo_año.nlargest(10, "co2")

    col_rank1, col_rank2 = st.columns([1, 2])

    with col_rank1:
        if pais != "World":
            ranking = data_ultimo_año[data_ultimo_año["co2"] > 0].sort_values("co2", ascending=False).reset_index(drop=True)
            if pais in ranking["country"].values:
                posicion = ranking[ranking["country"] == pais].index[0] + 1
            else:
                posicion = "N/A"
            st.markdown(f"### Ranking Global\n**{pais}** ocupa la posición **#{posicion}** de {len(ranking)} países con datos.")

    with col_rank2:
        fig_top = px.bar(
            top_10, x="co2", y="country", orientation='h',
            title=f"Top 10 Emisores en {ultimo_año}",
            labels={"co2": "Emisiones (Mt)", "country": "País"},
            color="co2", color_continuous_scale="Reds"
        )
        if pais in top_10["country"].values:
            fig_top.update_traces(marker=dict(line=dict(width=2, color='DarkSlateGrey')))
        fig_top.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_top, use_container_width=True)

    # === CO₂ vs Desarrollo ===
    st.markdown("---")
    st.header("¿Más Riqueza = Más Emisiones?")

    try:
        year_disponible = int(df["year"].max())
        data_scatter = df[df["year"] == year_disponible].copy()

        cols_requeridas = {"co2", "gdp", "population", "co2_per_capita", "country"}
        if not cols_requeridas.issubset(data_scatter.columns):
            st.warning("Faltan columnas necesarias en el dataset.")
        else:
            data_scatter = data_scatter.dropna(subset=["co2", "gdp", "population"])
            data_scatter = data_scatter[(data_scatter["co2"] > 0) &
                                        (data_scatter["gdp"] > 0) &
                                        (data_scatter["population"] > 0)]

            exclude_regions = [
                "World", "Europe", "Asia", "Africa", "North America", "South America",
                "European Union", "High-income countries", "Low-income countries",
                "Upper-middle-income countries", "Lower-middle-income countries",
                "Oceania", "Antarctica", "International transport"
            ]
            data_scatter = data_scatter[~data_scatter["country"].isin(exclude_regions)]

            if len(data_scatter) < 10:
                year_alt = sorted(df["year"].unique())[-2]
                data_scatter = df[df["year"] == year_alt].copy()
                data_scatter = data_scatter.dropna(subset=["co2", "gdp", "population"])
                data_scatter = data_scatter[(data_scatter["co2"] > 0) &
                                            (data_scatter["gdp"] > 0) &
                                            (data_scatter["population"] > 0)]
                data_scatter = data_scatter[~data_scatter["country"].isin(exclude_regions)]
                year_disponible = int(year_alt)

            if len(data_scatter) >= 10:
                fig_scatter = px.scatter(
                    data_scatter,
                    x="gdp",
                    y="co2",
                    size="population",
                    color="co2_per_capita",
                    hover_name="country",
                    title=f"Emisiones vs PIB (PPA) (año {year_disponible})",
                    labels={
                        "gdp": "PIB (PPA) Total (USD)",
                        "co2": "Emisiones CO₂ (Mt)",
                        "population": "Población",
                        "co2_per_capita": "CO₂ per cápita (t)"
                    },
                    color_continuous_scale="RdYlGn_r"
                )

                fig_scatter.update_xaxes(type="log")
                fig_scatter.update_yaxes(type="log")

                if pais != "World" and pais in data_scatter["country"].values:
                    pais_data = data_scatter[data_scatter["country"] == pais].iloc[0]
                    fig_scatter.add_trace(go.Scatter(
                        x=[pais_data["gdp"]],
                        y=[pais_data["co2"]],
                        mode='markers+text',
                        marker=dict(size=25, color='yellow', line=dict(width=3, color='black')),
                        text=[pais],
                        textposition="top center",
                        name=f"{pais} (seleccionado)",
                        showlegend=True
                    ))

                fig_scatter.update_layout(height=500, hovermode='closest')
                st.plotly_chart(fig_scatter, use_container_width=True)
                st.caption("Cada burbuja representa un país. El tamaño indica población y el color las emisiones per cápita.")
            else:
                st.info(f"No hay suficientes países con datos completos en {year_disponible}.")

    except Exception as e:
        st.error(f"Error al generar el gráfico: {e}")

# ========== TAB 2: COMPARACIÓN DE PAÍSES ==========
with tab2:
    st.header("Comparación Lado a Lado")
    st.write("Compara dos países para entender sus diferentes trayectorias de emisiones.")
    
    col_comp1, col_comp2 = st.columns(2)
    
    with col_comp1:
        pais_a = st.selectbox("País A", sorted(df["country"].unique()), index=sorted(df["country"].unique()).index("United States") if "United States" in df["country"].unique() else 0, key="pais_a")
    
    with col_comp2:
        pais_b = st.selectbox("País B", sorted(df["country"].unique()), index=sorted(df["country"].unique()).index("China") if "China" in df["country"].unique() else 1, key="pais_b")
    
    data_a = df[df["country"] == pais_a].sort_values("year")
    data_b = df[df["country"] == pais_b].sort_values("year")
    
    if data_a.empty or data_b.empty:
        st.warning("Uno o ambos países no tienen datos suficientes.")
    else:
        # Métricas comparativas
        st.subheader("Comparación Actual")
        
        ultimo_año_comp = min(int(data_a["year"].max()), int(data_b["year"].max()))
        
        data_a_rec = data_a[data_a["year"] == ultimo_año_comp].iloc[0] if not data_a[data_a["year"] == ultimo_año_comp].empty else None
        data_b_rec = data_b[data_b["year"] == ultimo_año_comp].iloc[0] if not data_b[data_b["year"] == ultimo_año_comp].empty else None
        
        if data_a_rec is not None and data_b_rec is not None:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(f"{pais_a}", f"{data_a_rec['co2']:,.0f} Mt", help="Emisiones totales")
                st.metric(f"{pais_b}", f"{data_b_rec['co2']:,.0f} Mt")
            
            with col2:
                st.metric(f"{pais_a}", f"{data_a_rec['co2_per_capita']:.1f} t/persona", help="Emisiones per cápita")
                st.metric(f"{pais_b}", f"{data_b_rec['co2_per_capita']:.1f} t/persona")
            
            with col3:
                st.metric(f"{pais_a}", f"{data_a_rec['population']/1e6:.0f}M", help="Población")
                st.metric(f"{pais_b}", f"{data_b_rec['population']/1e6:.0f}M")
        
        # Gráficos comparativos
        st.subheader("Evolución Temporal")
        
        fig_comp = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Emisiones Totales", "Emisiones per Cápita")
        )
        
        # Emisiones totales
        fig_comp.add_trace(
            go.Scatter(x=data_a["year"], y=data_a["co2"], name=pais_a, line=dict(color='#ff6b6b', width=3)),
            row=1, col=1
        )
        fig_comp.add_trace(
            go.Scatter(x=data_b["year"], y=data_b["co2"], name=pais_b, line=dict(color='#4ecdc4', width=3)),
            row=1, col=1
        )
        
        # Emisiones per cápita
        fig_comp.add_trace(
            go.Scatter(x=data_a["year"], y=data_a["co2_per_capita"], name=pais_a, line=dict(color='#ff6b6b', width=3), showlegend=False),
            row=1, col=2
        )
        fig_comp.add_trace(
            go.Scatter(x=data_b["year"], y=data_b["co2_per_capita"], name=pais_b, line=dict(color='#4ecdc4', width=3), showlegend=False),
            row=1, col=2
        )
        
        fig_comp.update_xaxes(title_text="Año", row=1, col=1)
        fig_comp.update_xaxes(title_text="Año", row=1, col=2)
        fig_comp.update_yaxes(title_text="CO₂ (Mt)", row=1, col=1)
        fig_comp.update_yaxes(title_text="CO₂ per cápita (t)", row=1, col=2)
        
        fig_comp.update_layout(height=400, hovermode='x unified')
        st.plotly_chart(fig_comp, use_container_width=True)
        
        # Análisis comparativo
        st.subheader("Análisis Comparativo")
        
        cambio_a = ((data_a_rec['co2'] - data_a.iloc[0]['co2']) / data_a.iloc[0]['co2'] * 100) if data_a.iloc[0]['co2'] > 0 else 0
        cambio_b = ((data_b_rec['co2'] - data_b.iloc[0]['co2']) / data_b.iloc[0]['co2'] * 100) if data_b.iloc[0]['co2'] > 0 else 0
        
        col_an1, col_an2 = st.columns(2)
        
        with col_an1:
            st.markdown(f"""
            **{pais_a}**:
            - Cambio desde 1990: **{cambio_a:+.1f}%**
            - Emisiones actuales: **{data_a_rec['co2']:,.0f} Mt**
            - Per cápita: **{data_a_rec['co2_per_capita']:.1f} t/persona**
            """)
        
        with col_an2:
            st.markdown(f"""
            **{pais_b}**:
            - Cambio desde 1990: **{cambio_b:+.1f}%**
            - Emisiones actuales: **{data_b_rec['co2']:,.0f} Mt**
            - Per cápita: **{data_b_rec['co2_per_capita']:.1f} t/persona**
            """)

# ========== TAB 3: PROYECCIONES FUTURAS ==========
with tab3:
    st.header("Proyecciones Futuras")
    
    col_config1, col_config2 = st.columns([3, 1])
    
    with col_config1:
        st.write("Explora escenarios futuros basados en modelos de machine learning. Utilizamos **Prophet** entrenado con datos recientes para capturar la tendencia actual.")
    
    with col_config2:
        años_entrenamiento = st.slider(
            "Años de historia",
            min_value=20,
            max_value=50,
            value=30,
            step=5,
            help="Cantidad de años históricos para entrenar el modelo"
        )
    
    col_sel_proj, col_info_proj = st.columns([2, 3])
    
    with col_sel_proj:
        pais_proj = st.selectbox("Selecciona un país", sorted(df["country"].unique()), key="pais_proj")
    
    with col_info_proj:
        st.info(f"Se usarán los últimos **{años_entrenamiento} años** para capturar mejor la tendencia reciente y evitar discontinuidades.")
    
    data_proj = df[df["country"] == pais_proj].sort_values("year").copy()
    data_proj = data_proj[["year", "co2"]].dropna()
    data_proj = data_proj[data_proj["co2"] > 0]
    
    if len(data_proj) < 15:
        st.warning(f"No hay suficientes datos válidos para {pais_proj}")
    else:
        try:
            from prophet import Prophet
            from sklearn.metrics import mean_absolute_error, r2_score
            
            # SOLUCIÓN 1: Usar solo datos recientes
            ultimo_año_disponible = int(data_proj["year"].max())
            año_inicio = max(data_proj["year"].min(), ultimo_año_disponible - años_entrenamiento)
            
            data_proj_reciente = data_proj[data_proj["year"] >= año_inicio].copy()
            
            if len(data_proj_reciente) < 10:
                st.warning(f"No hay suficientes datos en el período seleccionado ({len(data_proj_reciente)} años)")
            else:
                # Preparar datos para Prophet
                df_prophet = pd.DataFrame({
                    'ds': pd.to_datetime(data_proj_reciente['year'], format='%Y'),
                    'y': data_proj_reciente['co2'].values
                })
                
                # Configurar modelo con mayor flexibilidad
                with st.spinner("Entrenando modelo Prophet..."):
                    model = Prophet(
                        changepoint_prior_scale=0.15,  # Más flexible
                        interval_width=0.80,
                        yearly_seasonality=False,
                        weekly_seasonality=False,
                        daily_seasonality=False,
                        changepoint_range=0.9  # Permite cambios hasta el final
                    )
                    model.fit(df_prophet)
                    
                    # Crear fechas futuras
                    future = model.make_future_dataframe(periods=10, freq='Y')
                    forecast = model.predict(future)
                
                # Extraer proyecciones
                forecast_future = forecast.tail(10)
                años_futuros = forecast_future['ds'].dt.year.values
                
                # SOLUCIÓN 2: Ajustar para continuidad
                ultimo_valor_real = data_proj_reciente['co2'].iloc[-1]
                primer_valor_proyectado = forecast_future['yhat'].values[0]
                ajuste = ultimo_valor_real - primer_valor_proyectado
                
                # Aplicar ajuste
                co2_tendencia = np.maximum(forecast_future['yhat'].values + ajuste, 0)
                co2_optimista = np.maximum(forecast_future['yhat_lower'].values + ajuste, 0)
                co2_pesimista = np.maximum(forecast_future['yhat_upper'].values + ajuste, 0)
                
                # Validación
                st.subheader("Calidad del Modelo")
                
                forecast_hist = forecast[:-10]
                y_real = data_proj_reciente['co2'].values
                y_pred = forecast_hist['yhat'].values[:len(y_real)] + ajuste
                
                mae = mean_absolute_error(y_real, y_pred)
                r2 = r2_score(y_real, y_pred)
                
                col_val1, col_val2, col_val3 = st.columns(3)
                
                with col_val1:
                    st.metric("R² Score", f"{r2:.3f}")
                    if r2 > 0.85:
                        st.success("Excelente")
                    elif r2 > 0.65:
                        st.warning("Moderado")
                    else:
                        st.error("Pobre")
                
                with col_val2:
                    st.metric("Error Medio", f"{mae:.1f} Mt")
                
                with col_val3:
                    error_pct = (mae / data_proj_reciente['co2'].mean()) * 100
                    st.metric("Error %", f"{error_pct:.1f}%")
                
                # Gráfico mejorado
                st.subheader("Proyección 2024-2033")
                
                fig_proj = go.Figure()
                
                # Histórico completo (gris claro)
                data_proj_antigua = data_proj[data_proj["year"] < año_inicio]
                if len(data_proj_antigua) > 0:
                    fig_proj.add_trace(go.Scatter(
                        x=data_proj_antigua["year"],
                        y=data_proj_antigua["co2"],
                        mode='lines',
                        name='Histórico (anterior)',
                        line=dict(color='lightgray', width=2),
                        opacity=0.5,
                        showlegend=True
                    ))
                
                # Histórico reciente (azul fuerte)
                fig_proj.add_trace(go.Scatter(
                    x=data_proj_reciente["year"],
                    y=data_proj_reciente["co2"],
                    mode='lines+markers',
                    name='Histórico (usado para proyección)',
                    line=dict(color='#1f77b4', width=3),
                    marker=dict(size=5)
                ))
                
                # Rango de incertidumbre
                fig_proj.add_trace(go.Scatter(
                    x=años_futuros,
                    y=co2_pesimista,
                    mode='lines',
                    line=dict(width=0),
                    showlegend=False,
                    hoverinfo='skip'
                ))
                
                fig_proj.add_trace(go.Scatter(
                    x=años_futuros,
                    y=co2_optimista,
                    mode='lines',
                    name='Rango de incertidumbre (80%)',
                    line=dict(width=0),
                    fillcolor='rgba(255, 165, 0, 0.2)',
                    fill='tonexty'
                ))
                
                # Tendencia proyectada
                fig_proj.add_trace(go.Scatter(
                    x=años_futuros,
                    y=co2_tendencia,
                    mode='lines+markers',
                    name='Proyección (tendencia esperada)',
                    line=dict(color='orange', width=3, dash='dash'),
                    marker=dict(size=7, symbol='diamond')
                ))
                
                # Línea divisoria
                fig_proj.add_vline(
                    x=ultimo_año_disponible,
                    line_dash="dot",
                    line_color="gray",
                    annotation_text="Proyección →",
                    annotation_position="top"
                )
                
                fig_proj.update_layout(
                    title=f"Proyección de Emisiones: {pais_proj}",
                    xaxis_title="Año",
                    yaxis_title="Emisiones CO₂ (Mt)",
                    height=500,
                    hovermode='x unified',
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                st.plotly_chart(fig_proj, use_container_width=True)
                
                # Resto del código (interpretación, tabla, etc.) se mantiene igual...
                st.subheader("Interpretación de Escenarios")
                
                cambio_tendencia = ((co2_tendencia[-1] - ultimo_valor_real) / ultimo_valor_real * 100)
                cambio_optimista = ((co2_optimista[-1] - ultimo_valor_real) / ultimo_valor_real * 100)
                cambio_pesimista = ((co2_pesimista[-1] - ultimo_valor_real) / ultimo_valor_real * 100)
                
                col_int1, col_int2, col_int3 = st.columns(3)
                
                with col_int1:
                    st.markdown(f"""
                    ### Optimista
                    - **2033**: {co2_optimista[-1]:,.0f} Mt
                    - **Cambio**: {cambio_optimista:+.1f}%
                    """)
                
                with col_int2:
                    st.markdown(f"""
                    ### Tendencia
                    - **2033**: {co2_tendencia[-1]:,.0f} Mt
                    - **Cambio**: {cambio_tendencia:+.1f}%
                    """)
                
                with col_int3:
                    st.markdown(f"""
                    ### Pesimista
                    - **2033**: {co2_pesimista[-1]:,.0f} Mt
                    - **Cambio**: {cambio_pesimista:+.1f}%
                    """)
                
                # Tabla de proyecciones
                with st.expander("Tabla de proyecciones detalladas"):
                    tabla_proj = pd.DataFrame({
                        'Año': años_futuros,
                        'Optimista (Mt)': co2_optimista.round(1),
                        'Tendencia (Mt)': co2_tendencia.round(1),
                        'Pesimista (Mt)': co2_pesimista.round(1)
                    })
                    st.dataframe(tabla_proj, use_container_width=True)
                
                st.info(f"""
                **Nota técnica**: 
                - Modelo entrenado con datos de **{año_inicio}-{ultimo_año_disponible}** ({len(data_proj_reciente)} años)
                - Ajuste aplicado para garantizar continuidad con el último valor real
                - Intervalo de confianza: 80%
                """)
                
        except Exception as e:
            st.error(f"Error: {str(e)}")

# ========== TAB 4: FUENTES DE EMISIÓN ==========
with tab4:
    st.header("Desglose por Fuentes de Emisión")
    st.write("Descubre qué combustibles fósiles contribuyen más a las emisiones de cada país.")
    
    pais_fuentes = st.selectbox("Selecciona un país", sorted(df["country"].unique()), key="pais_fuentes")
    
    data_fuentes = df[df["country"] == pais_fuentes].sort_values("year")
    
    # Verificar columnas disponibles
    fuentes_cols = ["coal_co2", "oil_co2", "gas_co2", "cement_co2", "flaring_co2"]
    fuentes_disponibles = [col for col in fuentes_cols if col in data_fuentes.columns]
    
    if len(fuentes_disponibles) == 0:
        st.warning(f"No hay datos de fuentes de emisión para {pais_fuentes}")
    else:
        # Datos del último año
        ultimo_año_fuentes = int(data_fuentes["year"].max())
        data_fuentes_rec = data_fuentes[data_fuentes["year"] == ultimo_año_fuentes].iloc[0]
        
        # Preparar datos para gráfico de torta
        fuentes_dict = {
            "coal_co2": ("Carbón", "#2c3e50"),
            "oil_co2": ("Petróleo", "#e74c3c"),
            "gas_co2": ("Gas Natural", "#3498db"),
            "cement_co2": ("Cemento", "#95a5a6"),
            "flaring_co2": ("Quema de Gas", "#f39c12")
        }
        
        valores = []
        etiquetas = []
        colores = []
        
        for col in fuentes_disponibles:
            if pd.notna(data_fuentes_rec[col]) and data_fuentes_rec[col] > 0:
                valores.append(data_fuentes_rec[col])
                etiquetas.append(fuentes_dict[col][0])
                colores.append(fuentes_dict[col][1])
        
        if len(valores) > 0:
            col_pie, col_info = st.columns([2, 1])
            
            with col_pie:
                fig_pie = go.Figure(data=[go.Pie(
                    labels=etiquetas,
                    values=valores,
                    marker=dict(colors=colores),
                    hovertemplate='<b>%{label}</b><br>%{value:.1f} Mt<br>%{percent}<extra></extra>'
                )])
                
                fig_pie.update_layout(
                    title=f"Fuentes de Emisión en {pais_fuentes} ({ultimo_año_fuentes})",
                    height=400
                )
                
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col_info:
                st.markdown("### Sobre las Fuentes")
                st.markdown("""
                **Carbón**: El más contaminante por unidad de energía.
                
                **Petróleo**: Principalmente transporte y calefacción.
                
                **Gas Natural**: Más limpio que carbón y petróleo.
                
                **Cemento**: Producción industrial con alto CO₂.
                
                **Quema de Gas**: Desperdicio en extracción petrolera.
                """)
            
            # Evolución temporal por fuente
            st.subheader("Evolución por Fuente")
            
            fig_fuentes_time = go.Figure()
            
            for col in fuentes_disponibles:
                if col in data_fuentes.columns:
                    fig_fuentes_time.add_trace(go.Scatter(
                        x=data_fuentes["year"],
                        y=data_fuentes[col],
                        mode='lines',
                        name=fuentes_dict[col][0],
                        line=dict(width=2.5),
                        stackgroup='one'
                    ))
            
            fig_fuentes_time.update_layout(
                title=f"Evolución de Fuentes de Emisión: {pais_fuentes}",
                xaxis_title="Año",
                yaxis_title="Emisiones CO₂ (Mt)",
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_fuentes_time, use_container_width=True)
            
            # Análisis de transición energética
            st.subheader("Análisis de Transición Energética")
            
            # Comparar primer y último año
            primer_año_fuentes = int(data_fuentes["year"].min())
            data_fuentes_primera = data_fuentes[data_fuentes["year"] == primer_año_fuentes].iloc[0]
            
            col_trans1, col_trans2 = st.columns(2)
            
            with col_trans1:
                st.markdown(f"**Año {primer_año_fuentes}**")
                for col in fuentes_disponibles:
                    if pd.notna(data_fuentes_primera[col]) and data_fuentes_primera[col] > 0:
                        st.write(f"- {fuentes_dict[col][0]}: {data_fuentes_primera[col]:.1f} Mt")
            
            with col_trans2:
                st.markdown(f"**Año {ultimo_año_fuentes}**")
                for col in fuentes_disponibles:
                    if pd.notna(data_fuentes_rec[col]) and data_fuentes_rec[col] > 0:
                        cambio = ((data_fuentes_rec[col] - data_fuentes_primera[col]) / data_fuentes_primera[col] * 100) if pd.notna(data_fuentes_primera[col]) and data_fuentes_primera[col] > 0 else 0
                        emoji = "📈" if cambio > 0 else "📉"
                        st.write(f"- {fuentes_dict[col][0]}: {data_fuentes_rec[col]:.1f} Mt {emoji} ({cambio:+.1f}%)")
            
            # Intensidad de carbono
            if "coal_co2" in fuentes_disponibles and data_fuentes_rec["co2"] > 0:
                intensidad_carbon = (data_fuentes_rec["coal_co2"] / data_fuentes_rec["co2"]) * 100
                
                st.markdown("---")
                st.subheader("Dependencia del Carbón")
                
                col_carb1, col_carb2 = st.columns([1, 2])
                
                with col_carb1:
                    st.metric(
                        "Intensidad de Carbón",
                        f"{intensidad_carbon:.1f}%",
                        help="Porcentaje de emisiones provenientes del carbón"
                    )
                    
                    if intensidad_carbon > 50:
                        st.error("Muy alta dependencia del carbón")
                    elif intensidad_carbon > 30:
                        st.warning("Alta dependencia del carbón")
                    else:
                        st.success("Baja dependencia del carbón")
                
                with col_carb2:
                    st.markdown("""
                    El carbón es el combustible fósil más contaminante. Países con alta dependencia del carbón 
                    necesitan priorizar la transición hacia energías renovables o gas natural como paso intermedio.
                    
                    **Estrategias de descarbonización:**
                    - Cierre progresivo de plantas de carbón
                    - Inversión en renovables (solar, eólica)
                    - Eficiencia energética
                    - Captura y almacenamiento de carbono (CCS)
                    """)
        else:
            st.info(f"No hay datos de fuentes disponibles para {pais_fuentes} en {ultimo_año_fuentes}")

# === CONCLUSIÓN GLOBAL ===
st.markdown("---")
st.header("¿Qué Nos Dice Esta Historia?")

col_conc1, col_conc2 = st.columns(2)

with col_conc1:
    st.markdown("""
    ### Puntos Clave
    - Las emisiones globales siguen **creciendo**, aunque más lentamente  
    - Los países desarrollados tienen mayor huella **per cápita**  
    - La **descarbonización** es posible sin frenar el desarrollo  
    - Cada décima de grado cuenta para el futuro del planeta
    - La transición energética requiere **acción inmediata**
    """)

with col_conc2:
    st.markdown("""
    ### Para Explorar Más
    - [IPCC - Panel sobre Cambio Climático](https://www.ipcc.ch/)  
    - [Our World in Data - CO₂](https://ourworldindata.org/co2-emissions)  
    - [Climate Action Tracker](https://climateactiontracker.org/)
    - [IEA - Agencia Internacional de Energía](https://www.iea.org/)
    """)

st.markdown("---")
st.caption("Datos: Our World in Data | Fuente: Global Carbon Project, BP Statistical Review, Maddison Project Database")
st.caption("Dashboard creado con Streamlit • Las proyecciones son estimaciones ilustrativas, no predicciones científicas oficiales")