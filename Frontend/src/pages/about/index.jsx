import InfoPage from '../../components/info-page/index.jsx'

const sections = [
  {
    title: 'O que e o Nexus IA',
    paragraphs: [
      'O Nexus IA e um portal editorial AI-first que combina coleta automatizada de fontes, estruturacao de materias, revisao humana e experiencia de leitura inspirada em jornais digitais.',
      'A proposta e transformar o frontend em uma capa viva de noticias, com editorias fixas, pagina dinamica de materia e integracao direta com o backend do projeto.',
    ],
  },
  {
    title: 'Como a plataforma funciona',
    paragraphs: [
      'O backend organiza fontes, artigos brutos, materias geradas, tags, categorias e revisao editorial. Ja o frontend consome essas publicacoes para montar home, editorias, busca e leitura individual.',
      'Essa arquitetura permite manter a identidade visual do portal enquanto a origem do conteudo pode evoluir junto com o pipeline e com a operacao de revisao.',
    ],
  },
  {
    title: 'Direcao do produto',
    paragraphs: [
      'O Nexus IA foi pensado para unir tecnologia, fluxo editorial e experiencia de produto em um mesmo ambiente, sem separar brutalmente area institucional, autenticacao e leitura jornalistica.',
      'A ideia e continuar expandindo a plataforma com mais integracoes, mais refinamento visual e mais controle editorial sobre o que vai para o ar.',
    ],
  },
]

export default function AboutPage({ onChangePage }) {
  return (
    <InfoPage
      kicker="Institucional"
      title="Sobre o Nexus IA"
      intro="Esta pagina apresenta a ideia central do projeto, sua estrutura editorial e a direcao do produto como portal de noticias apoiado por inteligencia artificial."
      sections={sections}
      onChangePage={onChangePage}
    />
  )
}
