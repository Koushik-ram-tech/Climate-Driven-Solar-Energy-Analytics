/**
 * useBackend
 * Polls /health once on mount, fetches city list on mount, then exposes
 * city/date selection state + a manual trigger for POST /predict and
 * POST /predict-explain (fired automatically alongside every prediction).
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { fetchHealth, fetchCities, fetchPredict, fetchPredictExplain } from '../services/api'

/** ISO string for today's date, e.g. "2025-06-13" */
function todayISO() {
  return new Date().toISOString().split('T')[0]
}

export function useBackend() {
  // ── health ───────────────────────────────────────────────────────────────
  const [health, setHealth]               = useState(null)
  const [healthError, setHealthError]     = useState(null)
  const [healthLoading, setHealthLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setHealthLoading(true)
    fetchHealth()
      .then((data) => { if (!cancelled) { setHealth(data); setHealthError(null) } })
      .catch((err)  => { if (!cancelled) setHealthError(err.message) })
      .finally(()   => { if (!cancelled) setHealthLoading(false) })
    return () => { cancelled = true }
  }, [])

  // ── cities ───────────────────────────────────────────────────────────────
  const [cities, setCities]           = useState([])
  const [citiesError, setCitiesError] = useState(null)

  useEffect(() => {
    let cancelled = false
    fetchCities()
      .then((data) => { if (!cancelled) setCities(data.cities ?? []) })
      .catch((err)  => { if (!cancelled) setCitiesError(err.message) })
    return () => { cancelled = true }
  }, [])

  // ── selection state ──────────────────────────────────────────────────────
  const [selectedCity, setSelectedCity] = useState('Bengaluru')
  const [selectedDate, setSelectedDate] = useState(todayISO())

  // ── prediction ───────────────────────────────────────────────────────────
  const [prediction, setPrediction]   = useState(null)
  const [predError, setPredError]     = useState(null)
  const [predLoading, setPredLoading] = useState(false)

  // ── explainability ───────────────────────────────────────────────────────
  const [explain, setExplain]           = useState(null)
  const [explainError, setExplainError] = useState(null)
  const [explainLoading, setExplainLoading] = useState(false)

  /**
   * Monotonically-increasing counter. Each call to runPredict stamps the
   * in-flight requests with the current generation. A response belonging to
   * an older generation is silently discarded (race-condition guard).
   */
  const generationRef = useRef(0)

  // ── Reset stale results when city or date changes ────────────────────────
  // If the user edits the selection without re-running, old data no longer
  // matches the current inputs — clear it immediately so nothing misleading
  // is displayed. Loading flags are intentionally NOT cleared here; if a
  // request is already in-flight it will finish and be dropped by the
  // generation guard anyway.
  useEffect(() => {
    setPrediction(null)
    setPredError(null)
    setExplain(null)
    setExplainError(null)
  }, [selectedCity, selectedDate])

  /**
   * Fires POST /predict and POST /predict-explain in parallel.
   *
   * Race-condition strategy: increment generationRef before launching.
   * Each promise closure captures its own `gen` snapshot. On resolution,
   * it checks generationRef.current — if a newer request has since been
   * fired, the stale response is silently dropped.
   *
   * Keep-previous UX: we do NOT clear `prediction` / `explain` before the
   * new data arrives. The previous result stays visible behind the loading
   * indicator and is replaced atomically on success, or left in place on
   * error (so the user still sees the last valid output).
   */
  const runPredict = useCallback(() => {
    if (!selectedCity || !selectedDate) return

    const gen = ++generationRef.current

    // ── mark both as loading; preserve existing data ──
    setPredLoading(true)
    setPredError(null)
    setExplainLoading(true)
    setExplainError(null)

    const predictPromise = fetchPredict(selectedCity, selectedDate)
      .then((data) => {
        if (generationRef.current !== gen) return   // stale — discard
        setPrediction(data)
        setPredError(null)
      })
      .catch((err) => {
        if (generationRef.current !== gen) return
        setPredError(err.message)
        // leave previous prediction visible on error — don't null it out
      })
      .finally(() => {
        if (generationRef.current === gen) setPredLoading(false)
      })

    const explainPromise = fetchPredictExplain(selectedCity, selectedDate)
      .then((data) => {
        if (generationRef.current !== gen) return   // stale — discard
        setExplain(data)
        setExplainError(null)
      })
      .catch((err) => {
        if (generationRef.current !== gen) return
        setExplainError(err.message)
        // leave previous explanation visible on error — don't null it out
      })
      .finally(() => {
        if (generationRef.current === gen) setExplainLoading(false)
      })

    return Promise.all([predictPromise, explainPromise])
  }, [selectedCity, selectedDate])

  return {
    // health
    health, healthError, healthLoading,
    // cities
    cities, citiesError,
    // selection
    selectedCity, setSelectedCity,
    selectedDate, setSelectedDate,
    // prediction
    prediction, predError, predLoading,
    // explainability
    explain, explainError, explainLoading,
    runPredict,
  }
}
