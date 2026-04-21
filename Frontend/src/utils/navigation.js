const pageBySection = {
  inicio: 'home',
  noticias: 'noticias',
  negocios: 'negocios',
  tecnologia: 'tecnologia',
  saude: 'saude',
  clima: 'clima',
  cultura: 'cultura',
  politica: 'politica',
  'laboratorio ia': 'ciencia',
  videos: 'videos',
  ciencia: 'ciencia',
  'sobre o nexus ia': 'about',
}

const pageTitles = {
  home: 'Inicio',
  noticias: 'Noticias',
  negocios: 'Negocios',
  tecnologia: 'Tecnologia',
  saude: 'Saude',
  clima: 'Clima',
  cultura: 'Cultura',
  politica: 'Politica',
  ciencia: 'Ciencia',
  videos: 'Videos',
  review: 'Revisao',
  login: 'Entrar',
  register: 'Cadastro',
  'forgot-password': 'Recuperar senha',
  'reset-password': 'Nova senha',
  'terms-of-use': 'Termos de uso',
  'privacy-policy': 'Politica de privacidade',
  contato: 'Contato',
  about: 'Sobre o Nexus IA',
}

export function normalizeSection(value = '') {
  return value
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, ' ')
    .trim()
}

export function mapSectionToPage(section) {
  return pageBySection[normalizeSection(section)] ?? 'home'
}

export function getPageTitle(page) {
  return pageTitles[page] ?? 'Inicio'
}
