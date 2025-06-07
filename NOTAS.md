# Análisis del simulador StableSystem (autor: Max)

Este documento tiene por objetivo reconstruir el comportamiento lógico del simulador sin alterar su código. Se parte del análisis de los archivos `moc_sim.py` e `historical_sim.py`.

---

## Estructura del modelo

### Clase central: `StableSystem`

Representa un sistema económico basado en colateral BTC y emisión de tokens DoC y BPRO.

### Variables clave

- `btc_collateral`: cantidad total de BTC disponible como colateral.
- `doc_supply`: cantidad de DoCs emitidos.
- `bpro_supply`: cantidad de BPROs emitidos.
- `price`: precio actual del BTC.
- `param_coverage`: cobertura objetivo del sistema.
- `vault_docs`: DOCs emitidos por usuarios (guardados en un depósito virtual).
- `price_ma180`: media móvil de 180 días del BTC.
- `ema_alpha`: parámetro de suavizado para la EMA.
- `doc_threshold`: umbral máximo para emisión.

---

## Flujo principal de simulación (`step_one_day`)

1. Se actualiza el precio de BTC (`set_price`).
2. Se ajusta automáticamente el supply de DoC según la cobertura objetivo.
3. Se calcula el volumen de DoC que puede emitirse sin romper la cobertura.
4. Se particiona ese volumen entre:
   - DOCs emitibles por el protocolo
   - DOCs emitibles por usuarios (`vault_docs`)
5. Se calcula una tasa de interés estimada (rate_max) basada en:
   - MA180 actual
   - MA180 de hace 4 años
6. Se compara `rate_max` con la tasa de mercado (`funding_rate_market`)
   - Si el sistema es más rentable, se mintean DOCs extra.
   - Si el mercado es más rentable, se redimen DOCs desde vault.
7. Se genera un interés adicional proporcional a `rate_max * doc_supply`.

---

## Precio del BPRO

\[
\text{Precio BPRO (USD)} = \frac{(\text{BTC colateral} \cdot \text{precio BTC}) - \text{DoC emitidos}}{\text{BPRO supply}}
\]

\[
\text{Precio BPRO (BTC)} = \frac{\text{Precio BPRO (USD)}}{\text{precio BTC}}
\]

---

## Observación

Aunque no lo explicita, el modelo contiene un mecanismo contracíclico basado en la evolución histórica del BTC, que modula los incentivos internos y puede afectar indirectamente el leverage del BPRO.

Este documento continuará creciendo a medida que se analicen casos concretos.

