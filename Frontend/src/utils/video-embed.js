function safeUrl(value) {
  if (!value) {
    return null
  }

  try {
    return new URL(value)
  } catch {
    return null
  }
}

function normalizeYouTubeId(url) {
  const hostname = url.hostname.replace(/^www\./, '')

  if (hostname === 'youtu.be') {
    return url.pathname.split('/').filter(Boolean)[0] ?? null
  }

  if (hostname === 'youtube.com' || hostname === 'm.youtube.com') {
    if (url.pathname === '/watch') {
      return url.searchParams.get('v')
    }

    const [, section, id] = url.pathname.split('/')
    if (section === 'embed' || section === 'shorts' || section === 'live') {
      return id ?? null
    }
  }

  return null
}

function normalizeVimeoId(url) {
  const hostname = url.hostname.replace(/^www\./, '')
  if (hostname !== 'vimeo.com' && hostname !== 'player.vimeo.com') {
    return null
  }

  const segments = url.pathname.split('/').filter(Boolean)
  const numericSegment = segments.find((segment) => /^\d+$/.test(segment))
  return numericSegment ?? null
}

function isDirectVideoUrl(url) {
  return /\.(mp4|webm|ogg|mov)(\?.*)?$/i.test(url.pathname)
}

export function resolveVideoEmbed(videoUrl) {
  const parsedUrl = safeUrl(videoUrl)
  if (!parsedUrl) {
    return null
  }

  const youTubeId = normalizeYouTubeId(parsedUrl)
  if (youTubeId) {
    return {
      kind: 'iframe',
      provider: 'youtube',
      embedUrl: `https://www.youtube.com/embed/${youTubeId}`,
      originalUrl: parsedUrl.toString(),
      title: 'Video do YouTube',
    }
  }

  const vimeoId = normalizeVimeoId(parsedUrl)
  if (vimeoId) {
    return {
      kind: 'iframe',
      provider: 'vimeo',
      embedUrl: `https://player.vimeo.com/video/${vimeoId}`,
      originalUrl: parsedUrl.toString(),
      title: 'Video do Vimeo',
    }
  }

  if (isDirectVideoUrl(parsedUrl)) {
    return {
      kind: 'direct',
      provider: 'file',
      embedUrl: parsedUrl.toString(),
      originalUrl: parsedUrl.toString(),
      title: 'Video da materia',
    }
  }

  return {
    kind: 'external',
    provider: 'external',
    embedUrl: null,
    originalUrl: parsedUrl.toString(),
    title: 'Video externo',
  }
}
