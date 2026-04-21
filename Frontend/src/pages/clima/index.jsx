import { useEffect, useState } from 'react'
import './clima.css'
import { ApiError, fetchCategoryPage, fetchWeatherOverview } from '../../services/portal-api'

const fallbackStateMonitor = [
  { locationKey: 'brasilia-df', city: 'Brasilia', stateCode: 'DF', stateName: 'Distrito Federal' },
  { locationKey: 'sao-paulo-sp', city: 'Sao Paulo', stateCode: 'SP', stateName: 'Sao Paulo' },
  { locationKey: 'rio-de-janeiro-rj', city: 'Rio de Janeiro', stateCode: 'RJ', stateName: 'Rio de Janeiro' },
  { locationKey: 'belo-horizonte-mg', city: 'Belo Horizonte', stateCode: 'MG', stateName: 'Minas Gerais' },
  { locationKey: 'salvador-ba', city: 'Salvador', stateCode: 'BA', stateName: 'Bahia' },
  { locationKey: 'curitiba-pr', city: 'Curitiba', stateCode: 'PR', stateName: 'Parana' },
  { locationKey: 'porto-alegre-rs', city: 'Porto Alegre', stateCode: 'RS', stateName: 'Rio Grande do Sul' },
  { locationKey: 'recife-pe', city: 'Recife', stateCode: 'PE', stateName: 'Pernambuco' },
]

function getSeverityLabel(severity) {
  if (severity === 'grande-perigo') return 'Grande perigo'
  if (severity === 'perigo') return 'Perigo'
  if (severity === 'perigo-potencial') return 'Potencial'
  if (severity === 'atencao') return 'Atencao'
  return 'Info'
}

function getSeverityClass(severity) {
  if (severity === 'grande-perigo') return 'clima-severity is-critical'
  if (severity === 'perigo') return 'clima-severity is-high'
  if (severity === 'perigo-potencial') return 'clima-severity is-medium'
  if (severity === 'atencao') return 'clima-severity is-attention'
  return 'clima-severity is-info'
}

function formatTemperature(value) {
  if (value === null || value === undefined) {
    return '--'
  }
  return `${value}C`
}

function normalizeSpaces(value) {
  return String(value ?? '')
    .replace(/\s+/g, ' ')
    .trim()
}

function getAlertKind(title = '') {
  const normalizedTitle = title.toLowerCase()
  if (normalizedTitle.includes('chuva')) return 'rain'
  if (normalizedTitle.includes('tempestade')) return 'storm'
  if (normalizedTitle.includes('vendaval')) return 'wind'
  if (normalizedTitle.includes('umidade')) return 'dry'
  if (normalizedTitle.includes('calor')) return 'heat'
  return 'alert'
}

function getAlertKindLabel(kind) {
  if (kind === 'rain') return 'Chuva'
  if (kind === 'storm') return 'Tempestade'
  if (kind === 'wind') return 'Vento'
  if (kind === 'dry') return 'Umidade'
  if (kind === 'heat') return 'Calor'
  return 'Aviso'
}

function getWeatherMarkClass(kind) {
  if (kind === 'rain') return 'weather-mark is-rain'
  if (kind === 'storm') return 'weather-mark is-storm'
  if (kind === 'wind') return 'weather-mark is-wind'
  if (kind === 'dry') return 'weather-mark is-dry'
  if (kind === 'heat') return 'weather-mark is-heat'
  return 'weather-mark is-cloud'
}

function truncateText(value, maxLength) {
  const normalizedValue = normalizeSpaces(value)
  if (normalizedValue.length <= maxLength) {
    return normalizedValue
  }
  return `${normalizedValue.slice(0, maxLength).trim()}...`
}

function buildAlertHeadline(title = '') {
  const cleanedTitle = normalizeSpaces(title)
    .replace(/\.\s*Severidade Grau:\s*.+$/i, '')
    .replace(/\.\s*Severidade:\s*.+$/i, '')
    .trim()

  return cleanedTitle || 'Aviso meteorologico'
}

function extractAlertNarrative(alert) {
  const summary = normalizeSpaces(alert.summary)
  if (!summary) {
    return ''
  }

  const descriptionMatch = summary.match(/Descri[^ ]*\s*(.*)$/i)
  const narrative = descriptionMatch ? descriptionMatch[1] : summary

  return narrative
    .replace(/^INMET publica aviso iniciando em:\s*[^.]+\.\s*/i, '')
    .replace(/\bAreas? Aviso para as Areas:\s*/i, 'Areas: ')
    .replace(/\bLink\s+Graf[^ ]*.*$/i, '')
    .trim()
}

function buildAlertExcerpt(alert) {
  const narrative = extractAlertNarrative(alert)
  if (!narrative) {
    return 'Aviso meteorologico ativo sem descricao adicional na origem.'
  }

  const areaMarker = narrative.search(/\bAreas?:\b/i)
  const baseSummary = areaMarker >= 0 ? narrative.slice(0, areaMarker).trim() : narrative
  return truncateText(baseSummary, 136)
}

function buildAlertFullText(alert) {
  const narrative = extractAlertNarrative(alert)
  if (!narrative) {
    return 'Sem detalhes adicionais na origem.'
  }

  return narrative
}

function buildAlertAreas(alert) {
  if (Array.isArray(alert.areas) && alert.areas.length > 0) {
    return alert.areas.slice(0, 3).join(' / ')
  }
  if (alert.area) {
    return alert.area
  }
  return 'Abrangencia nao informada'
}

function buildHeroHeadline(summary) {
  if ((summary.locationCount ?? 0) > 0 || (summary.activeAlertCount ?? 0) > 0) {
    return 'Radar do clima no Brasil'
  }
  return 'Painel nacional do tempo'
}

function buildHeroSummary(summary) {
  const summaryParts = []

  if ((summary.locationCount ?? 0) > 0) {
    summaryParts.push(`${summary.locationCount} capitais com leitura do dia`)
  }

  if ((summary.activeAlertCount ?? 0) > 0) {
    summaryParts.push(`${summary.activeAlertCount} avisos oficiais em acompanhamento`)
  }

  if (summaryParts.length > 0) {
    return `${summaryParts.join(' / ')}. Abra um estado para ver os proximos 7 dias e toque em um aviso para ler o conteudo completo.`
  }

  return 'Os alertas oficiais seguem visiveis, mas a fonte publica de previsao das capitais esta instavel agora.'
}

function buildStateCards(locations) {
  if (locations.length > 0) {
    return locations.map((location) => {
      const today = location.daily?.[0] ?? null
      const kind = getAlertKind(today?.condition ?? '')
      return {
        locationKey: location.locationKey,
        city: location.city,
        stateCode: location.stateCode,
        stateName: location.stateName,
        headline: today?.condition ?? 'Leitura da semana',
        maxTemp: today?.maxTempC ?? null,
        minTemp: today?.minTempC ?? null,
        temperatureLabel: 'Max/Min hoje',
        hasTemperature: today?.maxTempC !== null || today?.minTempC !== null,
        markClass: getWeatherMarkClass(kind),
      }
    })
  }

  return fallbackStateMonitor.map((item) => ({
    ...item,
    headline: 'Fonte de previsao indisponivel',
    maxTemp: null,
    minTemp: null,
    temperatureLabel: 'Leitura de hoje',
    hasTemperature: false,
    markClass: 'weather-mark is-offline',
  }))
}

export default function ClimaPage({ onOpenArticle }) {
  const [status, setStatus] = useState('loading')
  const [errorMessage, setErrorMessage] = useState('')
  const [weatherData, setWeatherData] = useState(null)
  const [editorialData, setEditorialData] = useState(null)
  const [editorialMessage, setEditorialMessage] = useState('')
  const [selectedLocation, setSelectedLocation] = useState(null)
  const [selectedAlert, setSelectedAlert] = useState(null)
  const [heroCarouselIndex, setHeroCarouselIndex] = useState(0)

  useEffect(() => {
    let isActive = true

    const loadClima = async () => {
      setStatus('loading')
      setErrorMessage('')
      setEditorialMessage('')

      const [weatherResult, editorialResult] = await Promise.allSettled([
        fetchWeatherOverview(),
        fetchCategoryPage('clima'),
      ])

      if (!isActive) {
        return
      }

      if (weatherResult.status === 'rejected') {
        setStatus('error')
        setErrorMessage(
          weatherResult.reason instanceof ApiError
            ? weatherResult.reason.message
            : 'Nao foi possivel carregar o painel meteorologico.',
        )
        return
      }

      setWeatherData(weatherResult.value)

      if (editorialResult.status === 'fulfilled') {
        setEditorialData(editorialResult.value)
      } else {
        setEditorialData(null)
        setEditorialMessage(
          editorialResult.reason instanceof ApiError
            ? editorialResult.reason.message
            : 'As materias publicadas da editoria de clima nao puderam ser carregadas.',
        )
      }

      setStatus('success')
    }

    loadClima()

    return () => {
      isActive = false
    }
  }, [])

  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        setSelectedLocation(null)
        setSelectedAlert(null)
      }
    }

    window.addEventListener('keydown', handleEscape)
    return () => {
      window.removeEventListener('keydown', handleEscape)
    }
  }, [])

  useEffect(() => {
    const intervalId = window.setInterval(() => {
      setHeroCarouselIndex((current) => current + 1)
    }, 3500)

    return () => {
      window.clearInterval(intervalId)
    }
  }, [])

  if (status === 'loading') {
    return (
      <section className="editorial-placeholder">
        <p className="story-kicker">Carregando clima</p>
        <h1>Organizando o radar nacional.</h1>
        <p>Montando estados monitorados, alertas oficiais e a vitrine editorial da semana.</p>
      </section>
    )
  }

  if (status === 'error' || !weatherData) {
    return (
      <section className="editorial-placeholder">
        <p className="story-kicker">Clima indisponivel</p>
        <h1>Nao foi possivel carregar a aba de clima.</h1>
        <p>{errorMessage || 'Tente novamente quando a API de clima estiver disponivel.'}</p>
      </section>
    )
  }

  const summary = weatherData.summary
  const locations = weatherData.locations ?? []
  const alerts = weatherData.alerts ?? []
  const stateCards = buildStateCards(locations)
  const featuredArticle = editorialData?.featuredArticle ?? null
  const editorialArticles = editorialData?.articles?.slice(1, 4) ?? []
  const selectedLocationForecast = selectedLocation
    ? locations.find((location) => location.locationKey === selectedLocation.locationKey) ?? null
    : null
  const temperatureCards = stateCards.filter((item) => item.hasTemperature)
  const averageMaxTemperature = temperatureCards.length > 0
    ? Math.round(temperatureCards.reduce((total, item) => total + (item.maxTemp ?? 0), 0) / temperatureCards.length)
    : null
  const averageMinTemperature = temperatureCards.length > 0
    ? Math.round(temperatureCards.reduce((total, item) => total + (item.minTemp ?? 0), 0) / temperatureCards.length)
    : null
  const heroCarouselItems = temperatureCards.length > 0
    ? Array.from({ length: Math.min(4, temperatureCards.length) }, (_, index) => {
      return temperatureCards[(heroCarouselIndex + index) % temperatureCards.length]
    })
    : stateCards.slice(0, 4)
  const heroHighlights = (summary.advisoryItems ?? []).slice(0, 3)

  return (
    <section className="clima-page">
      <div className="clima-hero">
        <article className="clima-hero__main">
          <div className="clima-hero__meta">
            <p className="story-kicker">Clima</p>
            <span className="clima-live-pill">Radar nacional</span>
          </div>

          <div className="clima-hero__header">
            <div className="clima-hero__copy">
              <div className="clima-hero__signals">
                <div className="clima-hero__signal">
                  <strong>{summary.activeAlertCount}</strong>
                  <span>alertas ativos</span>
                </div>
                <div className="clima-hero__signal clima-hero__signal--muted">
                  <strong>{summary.locationCount}</strong>
                  <span>capitais com leitura</span>
                </div>
              </div>

              <h1>{buildHeroHeadline(summary)}</h1>
              <p className="clima-hero__summary">{buildHeroSummary(summary)}</p>
            </div>

            <div className="clima-hero__snapshot">
              <div className="clima-hero__average">
                <span className="clima-hero__average-label">Media Brasil</span>
                <strong>{formatTemperature(averageMaxTemperature)}</strong>
                <span className="clima-hero__average-range">Minima media {formatTemperature(averageMinTemperature)}</span>
                <small className="clima-hero__average-note">Leitura agregada das capitais monitoradas hoje.</small>
              </div>

              <div className="clima-hero__bullet-panel">
                <span className="clima-hero__bullet-title">Pulso rapido</span>
                <ul className="clima-hero__bullet-list">
                  {heroHighlights.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                  {heroHighlights.length === 0 ? (
                    <li>Os destaques nacionais voltam a aparecer assim que a fonte publica responder.</li>
                  ) : null}
                </ul>
              </div>
            </div>
          </div>

          <div className="clima-hero__temperature-strip">
            <div className="clima-hero__strip-head">
              <div>
                <span className="clima-hero__strip-kicker">Capitais em destaque</span>
                <h2>Leitura rapida da semana</h2>
              </div>
              <p>Abra um card para ver maxima, minima e previsao dos proximos 7 dias.</p>
            </div>

            <div className="clima-hero__carousel">
              {heroCarouselItems.map((item) => (
                <button
                  className="clima-hero__carousel-card"
                  key={`hero-${item.locationKey}`}
                  type="button"
                  onClick={() => {
                    if (item.hasTemperature) {
                      setSelectedLocation(item)
                    }
                  }}
                  disabled={!item.hasTemperature}
                >
                  <div className="clima-hero__carousel-city">
                    <span className="clima-hero__carousel-state">{item.stateCode}</span>
                    <strong>{item.city}</strong>
                    <small>{item.headline}</small>
                  </div>
                  <div className="clima-hero__carousel-temps">
                    <span>{formatTemperature(item.maxTemp)}</span>
                    <small>{formatTemperature(item.minTemp)}</small>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="clima-hero__metrics">
            <div>
              <strong>{summary.locationCount}</strong>
              <span>Capitais monitoradas</span>
            </div>
            <div>
              <strong>{summary.activeAlertCount}</strong>
              <span>Avisos na grade</span>
            </div>
            <div>
              <strong>{summary.severeAlertCount}</strong>
              <span>Alertas fortes</span>
            </div>
          </div>

          <div className="clima-hero__sources">
            <span>Atualizado: {summary.updatedAt}</span>
            <span>Fontes: {(summary.sourceNames ?? []).join(' + ') || 'Fontes configuradas'}</span>
          </div>
        </article>
      </div>

      <section className="clima-section">
        <div className="section-bar">
          <div>
            <p className="story-kicker">Estados monitorados</p>
            <h2>Temperatura por capital de referencia</h2>
          </div>
          <p>
            {locations.length > 0
              ? 'Leitura resumida por estado com maxima, minima e condicao dominante do dia.'
              : 'A grade continua visivel, mas a fonte oficial de previsao esta instavel no momento.'}
          </p>
        </div>

        <div className="clima-state-grid">
          {stateCards.map((item) => (
            <button
              className="clima-state-card"
              key={item.locationKey}
              type="button"
              onClick={() => {
                if (item.hasTemperature) {
                  setSelectedLocation(item)
                }
              }}
              disabled={!item.hasTemperature}
            >
              <div className="clima-state-card__head">
                <div>
                  <p className="story-kicker">{item.stateCode}</p>
                  <h3>{item.city}</h3>
                </div>
                <span className={item.markClass} aria-hidden="true" />
              </div>

              <div className="clima-state-card__temps">
                <div className="clima-state-card__temps-main">
                  <strong>{formatTemperature(item.maxTemp)}</strong>
                  <span>{formatTemperature(item.minTemp)}</span>
                </div>
                <small className="clima-state-card__temps-label">{item.temperatureLabel}</small>
              </div>

              <p className="clima-state-card__status">{item.headline}</p>
              {!item.hasTemperature ? (
                <small className="clima-state-card__note">Sem leitura oficial de temperatura agora</small>
              ) : (
                <small className="clima-state-card__note clima-state-card__note--action">
                  Abrir semana completa
                </small>
              )}
            </button>
          ))}
        </div>
      </section>

      <section className="clima-section">
        <div className="section-bar">
          <div>
            <p className="story-kicker">Avisos ativos</p>
            <h2>Alertas em cartoes mais rapidos de ler</h2>
          </div>
          <p>Resumo curto, tipo do evento e abrangencia principal em vez de blocos enormes do feed bruto.</p>
        </div>

        {alerts.length > 0 ? (
          <div className="clima-alert-grid">
            {alerts.map((alert) => {
              const alertKind = getAlertKind(alert.title)

              return (
                <button
                  className="clima-alert-card clima-alert-card--compact"
                  key={alert.externalId}
                  type="button"
                  onClick={() => setSelectedAlert(alert)}
                >
                  <div className="clima-alert-card__head">
                    <div className="clima-alert-card__badges">
                      <span className={getSeverityClass(alert.severity)}>{getSeverityLabel(alert.severity)}</span>
                      <span className="clima-alert-kind">{getAlertKindLabel(alertKind)}</span>
                    </div>
                    <span className="clima-alert-card__source">{alert.sourceName}</span>
                  </div>

                  <div className="clima-alert-card__body">
                    <div className="clima-alert-card__copy">
                      <h3>{truncateText(buildAlertHeadline(alert.title), 70)}</h3>
                      <p>{buildAlertExcerpt(alert)}</p>
                    </div>
                  </div>

                  <div className="clima-alert-card__meta clima-alert-card__meta--compact">
                    <span>{truncateText(buildAlertAreas(alert), 72)}</span>
                    <span>{alert.publishedAt}</span>
                    <span className="clima-alert-card__action">Abrir detalhes</span>
                  </div>
                </button>
              )
            })}
          </div>
        ) : (
          <div className="editorial-placeholder">
            <p className="story-kicker">Sem alertas ativos</p>
            <h1>O feed de avisos nao retornou alertas no momento.</h1>
            <p>Se novos avisos entrarem na fonte, a grade sera atualizada pela API de clima.</p>
          </div>
        )}
      </section>

      <section className="clima-section">
        <div className="section-bar">
          <div>
            <p className="story-kicker">Editoria de clima</p>
            <h2>Contexto e cobertura publicados</h2>
          </div>
          <p>A camada de servico convive com a parte editorial para explicacao, impacto regional e contexto.</p>
        </div>

        {featuredArticle ? (
          <div className="clima-editorial-grid">
            <article className="clima-editorial-feature">
              {featuredArticle.imageUrl ? (
                <div className="clima-editorial-feature__media">
                  <img src={featuredArticle.imageUrl} alt={featuredArticle.title} />
                </div>
              ) : null}

              <p className="story-kicker">{featuredArticle.label}</p>
              <h2>{featuredArticle.title}</h2>
              <p>{featuredArticle.summary}</p>

              <div className="clima-editorial-feature__meta">
                <span>{featuredArticle.author}</span>
                <span>{featuredArticle.publishedAt}</span>
                <span>{featuredArticle.readTime}</span>
              </div>

              <div className="clima-editorial-feature__actions">
                <button className="primary-link" type="button" onClick={() => onOpenArticle(featuredArticle.slug)}>
                  Ler materia
                </button>
              </div>
            </article>

            <div className="clima-editorial-list">
              {editorialArticles.map((article) => (
                <button
                  className="clima-editorial-card"
                  key={article.slug}
                  type="button"
                  onClick={() => onOpenArticle(article.slug)}
                >
                  <span className="story-kicker">{article.label}</span>
                  <h3>{article.title}</h3>
                  <p>{article.excerpt || article.summary}</p>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="editorial-placeholder">
            <p className="story-kicker">Editoria em preparo</p>
            <h1>A camada de servico ja esta no ar, mas ainda nao ha materias publicadas de clima.</h1>
            <p>{editorialMessage || 'Quando artigos de clima forem publicados no backend, eles aparecerao aqui.'}</p>
          </div>
        )}
      </section>

      {selectedLocation && selectedLocationForecast ? (
        <div className="clima-modal-backdrop" role="presentation" onClick={() => setSelectedLocation(null)}>
          <section
            className="clima-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="clima-location-dialog-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="clima-modal__head">
              <div>
                <p className="story-kicker">{selectedLocation.stateCode}</p>
                <h2 id="clima-location-dialog-title">
                  {selectedLocation.city}
                  {' '}
                  nos proximos 7 dias
                </h2>
              </div>
              <button className="clima-modal__close" type="button" onClick={() => setSelectedLocation(null)}>
                Fechar
              </button>
            </div>

            <p className="clima-modal__summary">
              Fonte:
              {' '}
              {selectedLocationForecast.sourceName}
              {' '}
              / Atualizado:
              {' '}
              {selectedLocationForecast.updatedAt}
            </p>

            <div className="clima-modal__forecast-grid">
              {selectedLocationForecast.daily.map((day) => (
                <article className="clima-modal__forecast-card" key={`${selectedLocationForecast.locationKey}-${day.date}`}>
                  <span>{day.label}</span>
                  <strong>{formatTemperature(day.maxTempC)}</strong>
                  <small>{formatTemperature(day.minTempC)}</small>
                  <p>{day.condition}</p>
                  <em>
                    Chuva:
                    {' '}
                    {day.rainProbability ?? '--'}
                    %
                  </em>
                </article>
              ))}
            </div>
          </section>
        </div>
      ) : null}

      {selectedAlert ? (
        <div className="clima-modal-backdrop" role="presentation" onClick={() => setSelectedAlert(null)}>
          <section
            className="clima-modal clima-modal--alert"
            role="dialog"
            aria-modal="true"
            aria-labelledby="clima-alert-dialog-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="clima-modal__head">
              <div className="clima-modal__badges">
                <span className={getSeverityClass(selectedAlert.severity)}>{getSeverityLabel(selectedAlert.severity)}</span>
                <span className="clima-alert-kind">{getAlertKindLabel(getAlertKind(selectedAlert.title))}</span>
              </div>
              <button className="clima-modal__close" type="button" onClick={() => setSelectedAlert(null)}>
                Fechar
              </button>
            </div>

            <h2 id="clima-alert-dialog-title">{buildAlertHeadline(selectedAlert.title)}</h2>

            <div className="clima-modal__meta">
              <span>{selectedAlert.sourceName}</span>
              <span>{selectedAlert.publishedAt}</span>
              <span>{buildAlertAreas(selectedAlert)}</span>
            </div>

            <p className="clima-modal__alert-text">{buildAlertFullText(selectedAlert)}</p>
          </section>
        </div>
      ) : null}
    </section>
  )
}
